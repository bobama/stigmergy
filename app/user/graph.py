"""
Graph messages

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
from django.conf import settings

from user.encryption import encrypt_notification


class Graph(models.Model):
    """
    Messages to the graph by users where they can request new local or global friends.
    They need to give their languages, location and list of people they have ever known.
    """
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key in self.schema["fields"]:
                setattr(self, key, value)
        encrypted_data = encrypt_notification(self)
        super(Graph, self).__init__(data = encrypted_data)

    schema = {
        "keys" : [settings.CRYPTO_KEY_GRAPH],
        "fields" : [
            "msgType",
            "accnt_id",
            "keyfp",
            "latitude",
            "longitude",
            "languages",
            "num_local_needed",
            "langs_global_needed_str",
            "known_contacts_str",
            "keep_contacts_str",
        ],
    }
    data = models.TextField()

