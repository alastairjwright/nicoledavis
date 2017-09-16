# Vagrant provisioning setup

# Local Installation Prerequisites

+ [Vagrant](http://www.vagrantup.com/downloads.html)
+ [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
+ [Vagrant Hostsupdater](https://github.com/cogitatio/vagrant-hostsupdater)
+ [fabric](http://fabric.readthedocs.org/en/latest/index.html)

## Setup

1. Install Virtualbox and Vagrant (download links above)
2. Install fabric on your local: `sudo easy_install pip && sudo pip install fabric`
3. Run `vagrant plugin install vagrant-hostsupdater` from command line
4. Open up the Vagrantfile and change the local hostname (named "changeme" by default)
5. Open the puppet manifest file, which sits in vagrant/puppet/manifests/init.pp and change the "$database" variable to your desired DB name.
6. Run the command `vagrant up` from the directory (might take a few minutes)
7. Open your browser to http://hostname.dev, where "hostname" is the name you picked in step 4

## Setting up the database
1. Open fabfile.py and setup each environment variable under the functions "vagrant", "dev", "staging", etc. Change each dbname, user and password variable accordingly.
2. Run fab replace_db from the project root directory
3. Enter "staging" as your SOURCE environment (first prompt)
4. Enter "vagrant" as your TARGET environment (second prompt)
5. Enter staging DB/SSH passwords when prompted

## Working with the environment

To SSH into your vagrant box:

`vagrant ssh` - from anywhere inside the project directory.

To start your vagrant box:

`vagrant up`

To halt/shutdown your vagrant box:

`vagrant halt`

To suspend your vagrant box (saves state):

`vagrant suspend`

Vagrant by default will map the project root directory to the /vagrant folder.
In other words, if you ssh into your vagrant box and `cd /vagrant`, you'll see
all your project files there. So you can use this to transfer files to/from
the vagrant box and your host machine.

To reload Vagrantfile and/or restart your vagrant box:

`vagrant reload`

To destroy your vagrant box (yes this is generally safe to do, just make sure you transfer any files you need):

`vagrant destroy`

To recreate it, run `vagrant up` the same way you did initially :).

To see which SSH port vagrant is listening to/misc information:

`vagrant ssh-config`

For a full list of vagrant commands, see the [vagrant documentation](http://docs.vagrantup.com/v2/cli/)

To access the local installation:

`http://hostname.dev/

## Changing the hostname

You can change the hostname by editing the Vagrantfile, find the lines with "changeme.dev"
and change to your liking.

## A Few Details

* If you're needing a password (for anything - including mysql, it's usually `vagrant`)
* Be wary of environment differences between vagrant/dev/staging!
