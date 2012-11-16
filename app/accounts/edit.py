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

from datetime import datetime, timedelta
from hashlib import sha256 # pylint: disable=E0611

from django.db import models
from django.core.exceptions import ObjectDoesNotExist


EDIT_LIVESPAN = 1
MAX_EDITS = 5


class EditCounts(models.Model):
    """track edits"""
    username_hash = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    count = models.IntegerField()

def edit_needs_captcha(request):
    """needs captcha"""
    result = False
    uhash = sha256(request.user.username).hexdigest()
    try:
        entry = EditCounts.objects.get(username_hash = uhash)
        live_span = timedelta (hours = EDIT_LIVESPAN)
        if datetime.now() - entry.created > live_span:
            entry.delete()
            raise ObjectDoesNotExist()
        else:
            if entry.count > MAX_EDITS:
                result = True
    except ObjectDoesNotExist:
        result = False
    return result

def delete_old_edit_data():
    """delete old edit tack data"""
    all_entries = EditCounts.objects.all()
    for entry in all_entries:
        if datetime.now() - entry.created > timedelta(hours=EDIT_LIVESPAN):
            entry.delete()

def increase_edit_count(request):
    """increase edit count"""
    uhash = sha256(request.user.username).hexdigest()
    try:
        entry = EditCounts.objects.get(username_hash = uhash)
    except ObjectDoesNotExist:
        entry = EditCounts.objects.create(username_hash = uhash, count=0)

    entry.count += 1
    entry.save()
