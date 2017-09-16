# Setup configuration variables here like DB name, mysql root password, etc...
$db_root_pass = 'vagrant'
$database = 'NICOLEDAVISDB'

exec { 'apt_update':
  command => 'apt-get update',
  path    => '/usr/bin'
}

# set global path variable for project
# http://www.puppetcookbook.com/posts/set-global-exec-path.html
Exec { path => [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/", "/usr/local/bin", "/usr/local/sbin", "~/.composer/vendor/bin/" ] }

# Define each module you want installed on the system
# these should correspond with the directories under puppet/modules
# each directory under puppet/modules should have its own manifests directory
# populated with an init.pp file which describes the module.
# e.g. puppet/modules/apache2/manifests/init.pp
class { 'git::install': }
class { 'apache2::install': }
class { 'php5::install': }
class { 'mysql::install': }
class { 'composer::install': }
