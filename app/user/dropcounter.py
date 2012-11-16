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

import hec

from django.db import models
from django.conf import settings


class DropCounter(models.Model):
    """
    Homomorphic encryption for drops.
    """
    # hec.quit() should be called before django terminates,
    # to clear memory. Somehow, somewhere.

    #### Fields
    # ID
    uid = models.CharField(max_length=10, primary_key=True)

    # Counters for when the user drops somebody else
    subject_nice = models.TextField()
    subject_middle = models.TextField()
    subject_bad = models.TextField()

    # Counter for when the user gets dropped
    object_nice = models.TextField()
    object_middle = models.TextField()
    object_bad = models.TextField()

    #### Constants
    grammatical_functions = ["subject", "object"]
    reasons = ["nice", "middle", "bad"]

    #### Methods
    def init(self):
        """
        Save the initial values of the drop counters. Needs to be called after creation of a row.
        """
        for fct in self.grammatical_functions:
            for rsn in self.reasons:
                # Initiate a counter.
                encrypted_counter = hec.new()
                # Save some disk space.
                enc_counter_compressed = int2db(encrypted_counter)
                setattr(self, "_".join([fct, rsn]), enc_counter_compressed)
        self.save()

    @classmethod
    def obfuscate(cls):
        """
        Increase the counters of about 100 randomly chosen contacts all by 0
        Not implemented because there are bigger security threats, such as: the number
        of friends can be counted directly from the friend_public_data encrypted blobs.
        """
        pass

    def increase(self, who=None, reason=None, amount=1):
        """
        Increase the drop counter in column "who_reason" by amount.
        Also increase all other counters of this row by 0, thereby changing their encrypted
        representation to obfuscate the change of who_reason.
        """
        if who in self.grammatical_functions and reason in self.reasons:
            field = "_".join([who, reason])

            other_fields = []
            for grm in self.grammatical_functions:
                for rsn in self.reasons:
                    if not ("_".join([grm, rsn]) == field):
                        other_fields.append ("%s_%s" % (grm, rsn)) 

            # increase the counter
            before = self.read_number(field)
            after = inc_number(before, amount)
            self.save_number(field, after)

            # obfuscate the other counter values by adding zero.
            for other_field in other_fields:
                before = self.read_number(other_field)
                after = inc_number(before, 0)
                self.save_number(other_field, after)

        elif settings.VERBOSE:
            print "Couldn't increase drop counter with who=%s and reason=%s." \
                % (who, reason)

    def read_number(self, field):
        """
        read counter from database
        """
        return db2int(getattr(self, field))

    def save_number(self, field, num):
        """
        save counter to database
        """
        setattr(self, field, int2db(num))


def inc_number(enc_number, amount):
    """
    Return the encryption of decryption(enc_number) + amount.
    """
    return hec.inc(str(enc_number), amount)

def int2db(num):
    """
    Converts an integer to a string, using hexadecimal compression.
    (base64 compression would be better).
    """
    string = hex(int(num)).lstrip("0x").rstrip("L")
    return string

def db2int(string):
    """
    Reads a compressed number from its database representation.
    """
    num = int(string, 16)
    return num

