#Install MySQL

class mysql::install {

  package { [
      'mysql-client',
      'mysql-server',
    ]:
    ensure => installed,
  }

  exec { 'Set MySQL server\'s root password':
    subscribe   => [
      Package['mysql-server'],
      Package['mysql-client'],
    ],
    refreshonly => true,
    unless      => "mysqladmin -uroot -p${db_root_pass} status",
    command     => "mysqladmin -uroot password ${db_root_pass}",
  }

  exec { 'Setup DB':
    subscribe   => [
      Package['mysql-server'],
      Package['mysql-client'],
      Exec['Set MySQL server\'s root password'],
    ],
    refreshonly => true,
    command     => "mysql -uroot -p${db_root_pass} -e \"CREATE DATABASE IF NOT EXISTS ${database}\"",
  }

}
