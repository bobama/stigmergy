"""

=======================================================================

Authors:
    Monk )2011)
    Lorenzo (2011-2012)
    Yamashi (2012) >Y<

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
"""

PRJ_ADMIN = "admin@STIGMERGY.aaa"
PRJ_FEEDBACK = 'feedback@STIGMERGY.aaa'
PRJ_DOMAIN = 'localhost:8000'
PRJ_MAIL = "@STIGMERGY.aaa"

SQL_ENGINE = 'django.db.backends.sqlite3'
#SQL_ENGINE = 'django.db.backends.mysql'
SQL_HOST = 'localhost'
SQL_PORT = ''
SQL_NAME = '../database/project.db'
SQL_USER = ''
SQL_PASSWD = ''
SQL_OPTIONS = ''
#SQL_OPTIONS = '{ 'init_command': 'SET storage_engine=INNODB; SET NAMES utf8' }'

CRYPTO_HOME = "../crypto"
CRYPTO_EXEC = "gpg"
CRYPTO_KEY_MAIL = "<...fingerprint...>"
CRYPTO_KEY_GRAPH = "<...fingerprint...>"
CRYPTO_KEY_TYPE = "RSA"
CRYPTO_KEY_LENGTH = 1024 
CRYPTO_KEY_SUBTYPE = "RSA"
CRYPTO_KEY_SUBLENGTH = 1024 
#CRYPTO_KEY_TYPE = "ECDSA"
#CRYPTO_KEY_LENGTH = 384 
#CRYPTO_KEY_SUBTYPE = "ECDH"
#CRYPTO_KEY_SUBLENGTH = 384 
CRYPTO_KEY_HOM_N = 426985845438863600614868422003820033136241123421514946559663494615494833625919 # pylint: disable=C0301
CRYPTO_KEY_HOM_G = 627398423423849268723424922182858227942518126068162286667180140466107648842572565613813229372396932441628644186755601564075513741425077638718840 # pylint: disable=C0301

HASH_SALT_FILE = "salts"
HASH_SALT_LENGTH = 16
HASH_ROUNDS = 2**18
