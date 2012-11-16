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

from django.conf import settings

from crypto.engines import GNUPG


def msg_encrypt (data, keys, hidden=False):
    """encrypt data with key(s)"""
    return GNUPG.encrypt (data, keys, hidekeyid=hidden, always_trust=True)

def msg_decrypt (data, key, passphrase):
    """decrypt data with key"""
    keyring = settings.CRYPTO_HOME + "/keys/" + key[0:2] + "/" + key
    return GNUPG.decrypt (
        data, secretkey=key, passphrase=passphrase,
        always_trust=True, keyring=keyring
    )

def gen_keypair (uid, passphrase, email):
    """generate keypair for user"""
    # set key parameters
    params = {
        'Key-Type':     settings.CRYPTO_KEY_TYPE,
        'Key-Length':   settings.CRYPTO_KEY_LENGTH,
        'Name-Real':    uid,
        'Name-Comment': "Server-side generated key",
        'Name-Email':   email,
    }
    if settings.CRYPTO_KEY_SUBTYPE is not None:
        params["Subkey-Type"] = settings.CRYPTO_KEY_SUBTYPE
        params["Subkey-Length"] = settings.CRYPTO_KEY_SUBLENGTH

    if settings.VERBOSE:
        print "############"
        print "Generating key pair with parameters: %s" % params
        kinput = GNUPG.gen_key_input ( # pylint: disable=W0142
            passphrase=passphrase, **params 
        )
        fingerprint = GNUPG.gen_key(kinput).fingerprint
        keyring = settings.CRYPTO_HOME + "/keys/"
        keyring += fingerprint[0:2] + "/" + fingerprint
        key_data = GNUPG.export_keys (fingerprint, True)
        GNUPG.import_keys (key_data, keyring=keyring)
        return fingerprint
