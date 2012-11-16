"""
Exceptions

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


class EncryptionError(Exception):
    """
    Failed encryption
    """
    pass

class CantEncryptPublicInfo(EncryptionError):
    """
    Faild encryption of public info
    """
    pass

class NoAuthenticatedUser(Exception):
    """
    Missing profile
    """
    pass

