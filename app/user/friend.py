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


class Friend(object):
    """
    Class for quick access to decrypted friends from the session.
    """
    def __init__(self, profile):
        """initialize instance"""
        self.profile = profile

class SpecialFriend(Friend):
    """special friend class (transient instances for dropped friends)"""
    def __init__(self, profile, speciality):
        self.speciality = speciality
        super(SpecialFriend, self).__init__(profile)

