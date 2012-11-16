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

from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist

from crypto.pw_hash import password_hash
from user.entity import User


class GpgBackend(ModelBackend):
    """
    Backend to enable log-in with a loginphrase only and no username
    """

    def authenticate(self, **kwargs):
        """
        Log in with a loginphrase.
        """
        loginphrase = kwargs['password']
        try:
            # Finds Users by the hash of their loginphrase only,
            # no username required.
            hashed = password_hash(loginphrase)
            user = User.objects.get(password=hashed)
            if user.check_password(loginphrase):
                return user
        except ObjectDoesNotExist:
            return None

    def get_user(self, user_id):
        """get assdociated user"""
        try:
            return User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None
