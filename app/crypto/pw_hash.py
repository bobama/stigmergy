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
from hashlib import sha512 # pylint: disable=E0611


def password_hash(password):
    """multi-round password hash"""
    salts = open(settings.SALT_FILE,"rb").read(-1)
    salt_length = settings.HASH_SALT_LENGTH
    salt_size = len(salts) - salt_length
    rounds = settings.HASH_ROUNDS

    data = sha512(password.encode("utf-8")).hexdigest()
    salt0_start = int(data, 16) % salt_size
    salt0 = salts[salt0_start : salt0_start + salt_length]
    result = sha512(password.encode("utf-8") + salt0)

    for _ in range(rounds):
        salt_start = int(result.hexdigest(), 16) % salt_size
        result = sha512(
            result.digest() + salts[salt_start : salt_start + salt_length]
        )

    return result.hexdigest()   
