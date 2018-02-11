#!/usr/bin/env python

from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.console import confirm
import getpass
import os
from datetime import datetime as dt
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

env.run = run
env.serverhub_path = '/home/ec2-user/fabric'
env.serverhub_sql_path = "{}/db-backups/sql".format(env.serverhub_path)


@task
def vagrant():
	env.user = 'vagrant'
	env.serverhub = False
	env.hostname = os.environ.get("VAGRANT_HOSTNAME")
	env.db = os.environ.get("VAGRANT_DB_NAME")
	env.db_user = os.environ.get("VAGRANT_DB_USER")
	env.db_pass = os.environ.get("VAGRANT_DB_PASS")
	env.db_dir = '/tmp'
	vagrantpath = os.getcwd()
	with lcd(vagrantpath):
		ssh_port = local('vagrant ssh-config | grep Port', capture=True).split()[1]
		keyfile = local('vagrant ssh-config | grep IdentityFile', capture=True).split()[1].translate(None, '"')
		env.key_filename = keyfile
		env.hosts = ['127.0.0.1:{}'.format(ssh_port)]

	puts("Using vagrant keyfile {}".format(env.key_filename))
	env.run = run

@task
def development():
	env.user = 'ec2-user'
	env.hosts = ['developer.serverhub.domanistudios.com']
	env.serverhub = True
	env.hostname = os.environ.get("DEV_HOSTNAME")
	env.db = os.environ.get("DEV_DB_NAME")
	env.db_user = os.environ.get("DEV_DB_USER")
	env.db_pass = os.environ.get("DEV_DB_PASS")
	env.db_host = get_serverhub_dbhost(os.environ.get("MYSQL_VERSION"))
	env.db_dir = ''
	env.key_filename = os.path.expanduser(os.environ.get("SERVER_HUB_SSH_KEY"))
	env.run = run

@task
def staging():
	env.user = 'ec2-user'
	env.hosts = ['developer.serverhub.domanistudios.com']
	env.serverhub = True
	env.hostname = os.environ.get("STG_HOSTNAME")
	env.db = os.environ.get("STG_DB_NAME")
	env.db_user = os.environ.get("STG_DB_USER")
	env.db_pass = os.environ.get("STG_DB_PASS")
	env.db_host = get_serverhub_dbhost(os.environ.get("MYSQL_VERSION"))
	env.db_dir = ''
	env.key_filename = os.path.expanduser(os.environ.get("SERVER_HUB_SSH_KEY"))
	env.run = run

@task
def get_serverhub_dbhost(mysqlVersion):
	formatted_mysql_version = mysqlVersion.replace(".", "")
	return "mysql{}.internal.domanistudios.com".format(formatted_mysql_version)

@task
def get_serverhub_docroot_from_hostname(hostname):
	return "/domani/var/www/vhosts/{}/html".format(hostname)

@task
def get_vagrant_docroot():
	return "/vagrant/html"

@task
def get_local_docroot():
	return os.path.join(os.path.dirname(__file__), 'html')

@task
def get_remote_rsync_string(path):
	return "{user}@{host}:{path}".format(**{
		'user': env.user,
		'host': env.hosts[0],
		'path': path,
	})

@task
def get_dumpfile():
	return os.path.join(
		env.db_dir,
		"{}_{}-{:%Y-%m-%d-%H:%M:%S}.sql".format(env.db, env.hostname, dt.today()
	))

@task
def backup_db(dumpfile):
	if env.serverhub:
		dump_result = env.run("{serverhub_path}/db-backups/backup -u \"{user}\" -p \"{pass}\" -i \"{host}\" -d \"{db}\" -f \"{dumpfile}\"".format(**{
			'serverhub_path': env.serverhub_path,
			'user': env.db_user,
			'pass': env.db_pass,
			'host': env.db_host,
			'db': env.db,
			'dumpfile': dumpfile,
		}))
	else:
		pass_flag = ""
		if env.db_pass:
			pass_flag = "-p'{}'".format(env.db_pass)
		dump_result = env.run("mysqldump -u {user} {pass} {db} > {dumpfile}".format(**{
			'user': env.db_user,
			'pass': pass_flag,
			'db': env.db,
			'dumpfile': dumpfile,
		}))
	if dump_result.failed and not confirm("mysqldump failed. Continue anyway?", default=False):
		abort("Aborting at user request.")

@task
def download_db(dumpfile):
	dumpfile = prefix_serverhub_file(dumpfile)
	download = get(dumpfile, os.getcwd())
	if download.failed and not confirm("Download of file {} failed. Continue anyway?".format(dumpfile), default=False):
		abort("Aborting at user request.")

@task
def prefix_serverhub_file(dumpfile):
	if env.serverhub:
		dumpfile = "{}/{}".format(env.serverhub_sql_path, dumpfile)
	return dumpfile

@task
def import_db(remotefile):
	if env.serverhub:
		import_result = env.run("{serverhub_path}/db-backups/replace -u \"{user}\" -p \"{pass}\" -i \"{host}\" -d \"{db}\" -f \"{remotefile}\"".format(**{
			'serverhub_path': env.serverhub_path,
			'user': env.db_user,
			'pass': env.db_pass,
			'host': env.db_host,
			'db': env.db,
			'remotefile': remotefile.replace("{}/".format(env.serverhub_sql_path), ""),
		}))
	else:
		pass_flag = ""
		if env.db_pass:
			pass_flag = "-p'{}'".format(env.db_pass)
		import_result = env.run("mysql -u {user} {pass} {db} < {remotefile}".format(**{
			'user': env.db_user,
			'pass': pass_flag,
			'db': env.db,
			'remotefile': remotefile,
		}))
	if import_result.failed and not confirm("MySQL import of file {} failed. Continue anyway?".format(remotefile), default=False):
		abort("Aborting at user request.")

@task
def should_download_db(source_env, target_env):
	should_download = True
	if source_env == 'local':
		should_download = False
	if is_remote_only_migration(source_env, target_env):
		should_download = False
	return should_download

@task
def is_remote_only_migration(source_env, target_env):
	is_remote_only_migration = False
	if source_env == 'dev' and target_env == 'stg':
		is_remote_only_migration = True
	if source_env == 'stg' and target_env == 'dev':
		is_remote_only_migration = True
	return is_remote_only_migration

@task
def run_search_replace(target_env, search_string, replace_string, is_multisite=False, target_url=""):
	multisite_arguments = ""
	if is_multisite:
		multisite_arguments = "--network --url={}".format(target_url)
	if target_env == 'vagrant':
		path = get_vagrant_docroot()
	else:
		path = get_serverhub_docroot_from_hostname(env.hostname)

	search_replace_result = env.run("wp search-replace '{find}' '{replace}' {multisite_arguments} --recurse-objects --all-tables --path={path}".format(**{
		'find': search_string,
		'replace': replace_string,
		'multisite_arguments': multisite_arguments,
		'path': path,
	}))
	if search_replace_result.failed and not confirm("WordPress search replace failed. Continue anyway?", default=False):
		abort("Aborting at user request.")

@task
def upload_file(local, remote):
	if env.host_string != 'localhost':
		upload = put(local, remote)
		if upload.failed and not confirm("Upload failed. Continue anyway?", default=False):
			abort("Aborting at user request.")

@task
def serverhub_internal_rsync(source_media, target_media):
	rsync_result = env.run("{serverhub_path}/rsync-internal/rsync -s \"{source_media}\" -d \"{target_media}\"".format(**{
		'serverhub_path': env.serverhub_path,
		'source_media': source_media,
		'target_media': target_media,
	}))
	if rsync_result.failed and not confirm("Media rsync failed. Continue anyway?", default=False):
		abort("Aborting at user request.")

@task
def run_rsync(source_env, target_env, source_media, target_media):
	dir_suffix = ""
	if source_env == 'vagrant':
		if os.path.isdir(source_media):
			dir_suffix="/"
		target_media = get_remote_rsync_string(target_media)
	else:
		with settings(warn_only=True):
			is_dir_result = env.run("[ -d {} ]".format(source_media))
			if is_dir_result.return_code == 0:
				dir_suffix="/"
		source_media = get_remote_rsync_string(source_media)
	rsync_result = local("rsync -rav --size-only --progress -e \"ssh -q -o StrictHostKeyChecking=no -i {key_filename}\" {source_media}{dir_suffix} {target_media}{dir_suffix}".format(**{
		'key_filename': env.key_filename,
		'source_media': source_media,
		'target_media': target_media,
		'dir_suffix': dir_suffix
	}))
	if rsync_result.failed and not confirm("Media rsync failed. Continue anyway?", default=False):
		abort("Aborting at user request.")

@task
def trim_lead_trail_slash(val):
	val = val.lstrip('/')
	val = val.rstrip('/')
	return val

@task
def get_env_object():
	return {
		'vagrant': vagrant,
		'dev': development,
		'stg': staging,
	}

@task
def replace_db():
	envs = get_env_object()
	source_env = prompt("Choose the SOURCE environment (press enter for STG) ({}): ".format('/'.join(envs.iterkeys())))
	target_env = prompt("Choose the TARGET environment (press enter for VAGRANT) ({}): ".format('/'.join(envs.iterkeys())))
	if not source_env:
		source_env = 'stg'
	if not target_env:
		target_env = 'vagrant'
	if source_env not in envs or target_env not in envs:
		abort("Not a valid source or target environment.")

	execute(envs[source_env])

	dumpfile = get_dumpfile()
	execute('backup_db', dumpfile)
	puts("Backed up {} database...".format(source_env))

	if should_download_db(source_env, target_env):
		execute('download_db', dumpfile)

	execute(envs[target_env])
	execute('backup_db', get_dumpfile())
	puts("Backed up {} database...".format(target_env))

	if not is_remote_only_migration(source_env, target_env):
		source_dump = os.path.join(os.getcwd(), os.path.basename(dumpfile))
		remotefile = os.path.join(env.db_dir, os.path.basename(source_dump))
		remotefile = prefix_serverhub_file(remotefile)
		puts("Uploading {} to {} as {}".format(source_dump, target_env, remotefile))
		execute('upload_file', source_dump, remotefile)
	else:
		remotefile = dumpfile

	execute('import_db', remotefile)
	puts("Successfully replaced DB on {} \xF0\x9F\x91\x8D".format(target_env))

@task
def wp_search_replace():
	envs = get_env_object()
	target_env = prompt("Choose the TARGET environment (press enter for VAGRANT) ({}): ".format('/'.join(envs.iterkeys())))
	if not target_env:
		target_env = 'vagrant'
	if target_env not in envs:
		abort("Not a valid source environment.")
	execute(envs[target_env])

	is_multisite = prompt('Is this a multisite [y/N]? ', default='N')
	is_multisite = is_multisite.upper()

	search_string = prompt('Enter the search string: ')
	replace_string = prompt('Enter the replace string: ', default=env.hostname)

	if not search_string or not replace_string:
		abort("Not a valid search or replace string.")

	if is_multisite == 'N' or is_multisite == 'NO':
		execute('run_search_replace', target_env, search_string, replace_string)
	else:
		target_url = prompt("-------------------------------\nMultisite requires a target URL.\nIf you are replacing the hostname, this will be the same as your search string.\nOtherwise it will be your current hostname ({}):".format(env.hostname), default=search_string)
		execute('run_search_replace', target_env, search_string, replace_string, True, target_url)

	puts("\xF0\x9F\x94\x8D  Successfully replaced {} with {} on {} \xF0\x9F\x94\x8E".format(search_string, replace_string, target_env))

@task
def rsync():
	envs = get_env_object()
	source_env = prompt("Choose the SOURCE environment (press enter for STG) ({}): ".format('/'.join(envs.iterkeys())))
	target_env = prompt("Choose the TARGET environment (press enter for VAGRANT) ({}): ".format('/'.join(envs.iterkeys())))
	if not source_env:
		source_env = 'stg'
	if not target_env:
		target_env = 'vagrant'
	if source_env not in envs or target_env not in envs:
		abort("Not a valid source or target environment.")

	media = prompt("Enter the file or directory name including relative path: ", default="wp-content/uploads")
	media = trim_lead_trail_slash(media)

	if not media:
		abort("Not a valid media.")

	if is_remote_only_migration(source_env, target_env):
		execute(envs[source_env])
		source_media = "{}/{}".format(get_serverhub_docroot_from_hostname(env.hostname), media)
		execute(envs[target_env])
		target_media = "{}/{}".format(get_serverhub_docroot_from_hostname(env.hostname), media)
		execute('serverhub_internal_rsync', source_media, target_media)
	else:
		if source_env == 'vagrant':
			execute(envs[target_env])
			source_media = "{}/{}".format(get_local_docroot(), media)
			target_media = "{}/{}".format(get_serverhub_docroot_from_hostname(env.hostname), media)
		else:
			execute(envs[source_env])
			source_media = "{}/{}".format(get_serverhub_docroot_from_hostname(env.hostname), media)
			target_media = "{}/{}".format(get_local_docroot(), media)
		execute('run_rsync', source_env, target_env, source_media, target_media)

	puts("\xF0\x9F\x8C\x88  Successfully synced {} from {} to {} \xF0\x9F\x8C\x85".format(media, source_env, target_env))
