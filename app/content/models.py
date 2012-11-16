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

from django.db import models
from user.entity import User


class Token(models.Model):
    """Token for invitation-only registration"""
    REGISTRATION_CHOICES = (
        (0, "Free"),
        (1, "Registered"),
    )
    USED_CHOICES = (
        (0, "Never used"),
        (1, "Has been used"),
    )
    token_string = models.CharField(max_length=32) # fixed random strings
    user = models.ForeignKey(User, on_delete=models.SET(1))
    deleted_email = models.CharField(max_length=75)
    
    # every token can only have one user registered with it
    registered = models.IntegerField(choices=REGISTRATION_CHOICES)
    # keeping track of which tokens are used
    ever_used = models.IntegerField(choices=USED_CHOICES)
