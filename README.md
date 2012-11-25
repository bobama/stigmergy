STIGMERGY
=========

the "stigmergic social network"

Licence
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Introduction
------------

STIGMERGY represents a totally new form of social networking. It is designed to
allow people to "mesh up" in a global movement and to retain their individual
privacy - and without the risk of revealing the complete network graph to
intruders and adversaries.

This goal is achieved by different means:
    
    1. All information of a user is encrypted and is visible only to the user
       and the assigned contacts. Nobody else can read the information!
       
    2. The layout of the connections of the network (who is in contact with
       whom) is also hidden. No contact of a user can find out which other
       contacts are  maintained by the user. A friend of a friend is not
       necessarily a friend!
       
    3. Even if a server is seized by an adversary the information of the
       individual user and the network graph are protected and can't be
       reconstructed from the data visible on the server.

Unlike other social networking platforms like Facebook or Google+, the number
of contacts you have in "Stigmergy" is limited - and you get contacts assigned
instead of choosing them.

In total you have exactly twelve contacts: six local contacts (geographically
close to you) and six global contacts that speak one of the languages you
speak. If you have a contact that is unresponsive, rude or suspected of being
"incompatible" with the ideas of the other users of the network, you can drop
the contact and get a new contact assigned after some time. 

INSTALL
-------

### Prerequisites:

You need the following base packages installed:
    
* Python 2.7
* Django 1.4 with django-simple-captcha
* GnuPG 1.4

Additional Python modules may be required depending on your local
installation. 

### Base directory

It is assumed you have extracted/cloned the repository into a
directory of your choice. The name of this directory is called
"<base>" in all following instructions. 

### Create local settings file

Change into the "<base>/app/" folder and copy the template file:

    $ cp tpl.settings_personal.py settings_personal.py
   
Have a look at the file but don't change anything yet. 

### Create missing directories

Change into the "<base>/" folder 

    $  mkdir -p database crypto/keys
    $  for p1 in 0 1 2 3 4 5 6 7 8 9 A B C D E F; do
           for p2 in 0 1 2 3 4 5 6 7 8 9 A B C D E F; do
               mkdir crypto/keys/${p1}${p2}
           done
       done

### Create system keys

Change into the "<base>/crypto/" folder and use GnuPG 1.4 to create mandatory
system keys; make sure you remember the passwords you assign to the private
keys!

    $ gpg --home . --gen-key [Create RSA-1024 key for mail manager]
    $ gpg --home . --gen-key [Create RSA-1024 key for graph manager]
    
 Copy the resulting key fingerprints and put them into the corresponding
 fields in the file "personal_settings.py"; the fields are named
 "CRYPTO_KEY_MAIL" and "CRYPTO_KEY_GRAPH".
 
 If done, archive the generated keys:

     $ tar cvzf manager_keys.tar.gz *.gpg 

### Generate a file for hash salts

Change to the "<base>/app/" folder and generate a random salts file:

    $ dd if=/dev/urandom of=salts bs=1 count=1048599

### Compile and install additional modules

Change into the "<base>/modules/hec/" folder and run:

    $ sudo python setup.py install

RUNNING
-------    

Change to the "<base>/app/" folder. To start with a new and empty database and
clean crypto folder, run:

    $ ./clean_run.sh

To run the application with existing data, run:

    $ ./run.sh
