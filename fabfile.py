#!/usr/bin/env python

from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.console import confirm
from fabric.utils import warn
import getpass
import os
from datetime import datetime as dt

env.run = run

@task(aliases=['local'])
def localhost():
    env.hosts = ['localhost']
    env.run = local
    env.web_service = 'apache2'
    # Mysqldump files are stored here
    env.db_dir = os.getcwd()
    env.db = 'DBNAME'
    env.db_user = 'root'
    env.db_pass = ''

@task
def vagrant():
    env.user = 'vagrant'
    env.web_service = 'apache2'
    env.db = 'DBNAME'
    env.db_user = 'root'
    env.db_pass = 'vagrant'
    # Mysqldump files are stored here
    env.db_dir = '/tmp'
    # Use vagrant key if needed
    vagrantpath = os.getcwd()
    with lcd(vagrantpath):
        ssh_port = local('vagrant ssh-config | grep Port', capture=True).split()[1]
        keyfile = local('vagrant ssh-config | grep IdentityFile', capture=True).split()[1]
        if keyfile.startswith('"') and keyfile.endswith('"'):
            keyfile = keyfile[1:-1]
        env.key_filename = keyfile
        env.hosts = ['127.0.0.1:{}'.format(ssh_port)]

    puts("Using vagrant keyfile {}".format(env.key_filename))
    env.run = run

@task(aliases=['dev'])
def development():
    env.user = 'DEVUSER'
    env.hosts = ['DEVSERVER.dev.domanistudios.com']
    env.web_service = 'httpd'
    env.db = 'DEVDB'
    env.db_user = 'DEVDBUSER'
    env.db_pass = getpass.getpass("Please enter DB password for DEV: ")
    # Mysqldump files are stored here
    env.db_dir = '/tmp'
    env.run = run

@task(aliases=['stage', 'stging', 'stg'])
def staging():
    env.user = 'STGUSER'
    env.hosts = ['STGSERVER.stg.domanistudios.com']
    env.web_service = 'httpd'
    env.db = 'STGDB'
    env.db_user = 'STGDBUSER'
    env.db_pass = getpass.getpass("Please enter DB password for STAGING: ")
    # Mysqldump files are stored here
    env.db_dir = '/tmp'
    env.run = run

@task(aliases=['prod'])
def production():
    env.user = 'ec2-user'
    env.hosts = ['PRODSERVER.com']
    env.web_service = 'nginx'
    env.db = 'PRODDB'
    env.db_user = 'PRODDBUSER'
    env.db_pass = getpass.getpass("Please enter DB password for PRODUCTION: ")
    # Mysqldump files are stored here
    env.db_dir = '/tmp'
    env.key_filename = '~/.ssh/PRODKEY.pem'
    env.run = run


def get_dumpfile():
    return os.path.join(
        env.db_dir,
        "{}_dump_{:%Y-%m-%d-%H:%M:%S}.sql".format(env.host_string, dt.today()
    ))

@task
def backup_db():
    dumpfile = get_dumpfile()
    pass_flag = ''
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

    if env.host_string != 'localhost':
        # Download the new dump file
        download = get(dumpfile, os.getcwd())
        if download.failed and not confirm("Download of file {} failed. Continue anyway?".format(dumpfile), default=False):
            abort("Aborting at user request.")
    env.dumpfile = os.path.join(os.getcwd(), os.path.basename(dumpfile))

@task
def import_db(remotefile=None):
    if not remotefile:
        remotefile = prompt("Please enter the path to the MySQLdump file: ")

    pass_flag = ''
    if env.db_pass:
        pass_flag = "-p'{}'".format(env.db_pass)
    result = env.run("mysql -u {user} {pass} {db} < {remotefile}".format(**{
        'user': env.db_user,
        'pass': pass_flag,
        'db': env.db,
        'remotefile': remotefile,
    }))
    if result.failed and not confirm("MySQL import of file {} failed. Continue anyway?".format(remotefile), default=False):
        abort("Aborting at user request.")

@task(aliases=['wpenv', 'wp_env'])
def update_wordpress_environment(wp_env=None):
    if not wp_env:
        wp_env = env.get('wp_env_number') or prompt("Please enter the life environment number to set: ")

    pass_flag = ''
    if env.db_pass:
        pass_flag = "-p'{}'".format(env.db_pass)

    query = "UPDATE wp_options SET option_value = '{}' WHERE option_name='{}' LIMIT 1".format(wp_env, env.wp_env_option)
    result = env.run("mysql -u {user} {pass} -e \"{query}\" {db}".format(**{
        'user': env.db_user,
        'pass': pass_flag,
        'db': env.db,
        'query': query,
    }))
    if result.failed and not confirm("MySQL wordpress URL replace failed. Continue anyway?", default=False):
        abort("Aborting at user request.")

@task(aliases=['wordpress_url', 'wp_url', 'wpurl'])
def update_wordpress_url(url=None):
    if not url:
        url = env.get('wp_url') or prompt("Please enter wordpress URL to set: ")

    pass_flag = ''
    if env.db_pass:
        pass_flag = "-p'{}'".format(env.db_pass)
    url = url.replace(':', '\:')
    query = "UPDATE wp_options SET option_value = '{}' WHERE option_name IN ('siteurl', 'home')".format(url)
    result = env.run("mysql -u {user} {pass} -e \"{query}\" {db}".format(**{
        'user': env.db_user,
        'pass': pass_flag,
        'db': env.db,
        'query': query,
    }))
    if result.failed and not confirm("MySQL wordpress URL replace failed. Continue anyway?", default=False):
        abort("Aborting at user request.")

@task(aliases=['stripe', 'update_stripe', 'stripe_keys'])
def update_wordpress_stripe_keys(pubkey=None, privkey=None):
    if not pubkey:
        pubkey = env.get('stripe_public_key')
    if not privkey:
        privkey = env.get('stripe_secret_key')

    if not pubkey or not privkey:
        warn("Stripe private or public key is not set, skipping option update...")
        return

    pass_flag = ''
    if env.db_pass:
        pass_flag = "-p'{}'".format(env.db_pass)
    query = "UPDATE wp_options SET option_value = '{}' WHERE option_name='stripe_public_key' LIMIT 1".format(pubkey)
    result = env.run("mysql -u {user} {pass} -e \"{query}\" {db}".format(**{
        'user': env.db_user,
        'pass': pass_flag,
        'db': env.db,
        'query': query,
    }))
    if result.failed and not confirm("Stripe key setting failed. Continue anyway?", default=False):
        abort("Aborting at user request.")

    query = "UPDATE wp_options SET option_value = '{}' WHERE option_name='stripe_private_key' LIMIT 1".format(privkey)
    result = env.run("mysql -u {user} {pass} -e \"{query}\" {db}".format(**{
        'user': env.db_user,
        'pass': pass_flag,
        'db': env.db,
        'query': query,
    }))
    if result.failed and not confirm("Stripe key setting failed. Continue anyway?", default=False):
        abort("Aborting at user request.")


@task
def upload_file(local, remote):
    if env.host_string != 'localhost':
        upload = put(local, remote)
        if upload.failed and not confirm("Upload failed. Continue anyway?", default=False):
            abort("Aborting at user request.")

@task(aliases=['restart'])
def restart_web():
    service = env.get('web_service')
    if not service:
        warn("Web service not defined for environment. Skipping...")
        return

    result = sudo("service {} restart".format(service))
    if result.failed and not confirm("{} restart failed. Continue anyway?".format(service), default=False):
        abort("Aborting at user request.")

@task(aliases=['cvc', 'cache', 'clear_cache', 'clear-cache'])
def clear_varnish_cache(url='.'):
    sudo("varnishadm -T 127.0.0.1:6082 -S /etc/varnish/secret \"ban.url {}\"".format(url))

@task
def replace_db():
    # Function mappings to let each env define user/db creds
    envs = {
        'vagrant': vagrant,
        'local': localhost,
        'dev': development,
        'staging': staging,
        'production': production,
        'prod': production,
    }
    source_env = prompt("Choose the SOURCE environment (press enter for LOCAL) ({}): ".format('/'.join(envs.iterkeys())))
    target_env = prompt("Choose the TARGET environment (press enter for DEV) ({}): ".format('/'.join(envs.iterkeys())))
    if not source_env:
        source_env = 'local'
    if not target_env:
        target_env = 'dev'
    if source_env not in envs or target_env not in envs:
        abort("Not a valid target or source environment.")

    if target_env in ('prod', 'production') and not confirm("***WARNING***: YOU HAVE SELECTED PROD "
                                                            "AS YOUR TARGET DATABASE. This will *REPLACE* "
                                                            "the production database!!!! Are you sure?: ",
                                                            default=False):
        abort("Aborting at user request")

    # Backup both databases
    execute(envs[source_env])
    execute('backup_db')
    puts("Backed up {} database...".format(source_env))
    source_dump = env.dumpfile

    execute(envs[target_env])
    execute('backup_db')
    puts("Backed up {} database...".format(target_env))
    remote_dump = env.dumpfile

    puts("Uploading {} to {}".format(source_dump, target_env))
    remotefile = os.path.join(env.db_dir, os.path.basename(source_dump))
    execute('upload_file', source_dump, remotefile)
    puts(u"\u0f3c \u3064 \u25d5_\u25d5 \u0f3d\u3064 PUSH TO {}!".format(target_env.upper()))
    execute('import_db', remotefile)
    puts(u"\u250f (-_-)\u251b\u2517 (-_-\ufeff )\u2513\u2517 (-_-)\u251b\u250f (-_-)\u2513 Successfully replaced DB on {}!".format(target_env))
