"""
Captcha

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

from Crypto.Random import random
from datetime import datetime, timedelta

from django import forms
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from captcha.fields import CaptchaField

from accounts.edit import increase_edit_count, delete_old_edit_data, \
                          edit_needs_captcha


CAPTCHA_LIVESPAN = 5


class CaptchaTestForm (forms.Form):
    """Test captcha input"""
    captcha = CaptchaField()


class CaptchaEntry(models.Model):
    """
    When a user enters a captcha correctly, this model stores Booleans
    indicating that he can check whether an email is registered once
    and that he can register once.
    """
    can_check_email = models.BooleanField()
    can_register = models.BooleanField()
    last_accessed = models.DateTimeField(auto_now=True, auto_now_add=True)
    sessionid = models.CharField(max_length=40, unique=True)

    def __init__(self):
        super(CaptchaEntry, self).__init__()

def edit_captcha_ok(request):
    """edit captcha"""
    increase_edit_count(request)
    if edit_needs_captcha(request):
        captcha_form = CaptchaTestForm(request.POST)
        result = captcha_form.is_valid()
    else:
        result = True

    if random.getrandbits(5) == 1:
        # roughly every 32 checks..
        delete_old_edit_data()

    return result

def captcha_valid(request, mode):
    """check for valid captch"""
    if random.getrandbits(4) == 1:
        # roughly every 16 checks..
        delete_old_data()

    sessionid = get_captcha_id(request)
    try:
        entry = CaptchaEntry.objects.get(sessionid = sessionid)
        live_span = timedelta (hours = CAPTCHA_LIVESPAN)
        if datetime.now() - entry.lastAccessed < live_span:
            if mode == "register":
                return entry.canRegister
            elif mode == "email":
                return entry.canCheckEmail
    except Exception: # pylint: disable=W0703
        pass
    return False

def get_captcha_id(request):
    """get captch id"""
    try:
        sessionid = request.COOKIES["csrftoken"]
    except Exception: # pylint: disable=W0703
        sessionid = request.session.session_key
        # this fallback is often not actually staying constant...
    return sessionid

def delete_old_data():
    """delete old captch data"""
    all_entries = CaptchaEntry.objects.all()
    live_span = timedelta (hours = CAPTCHA_LIVESPAN)
    for entry in all_entries:
        if datetime.now() - entry.lastAccessed > live_span:
            entry.delete()

def save_valid_captcha(request):
    """save valid captch"""
    sessionid = get_captcha_id(request)
    try:
        entry = CaptchaEntry.objects.get(sessionid = sessionid)
        entry.canRegister = True
        entry.canCheckEmail = True
    except ObjectDoesNotExist:
        entry = CaptchaEntry.objects.create(
            sessionid=sessionid, canRegister=True, canCheckEmail=True
        )
    entry.save()

def invalidate_captcha (request, mode="both"):
    """invalidate captcha"""
    sessionid = get_captcha_id(request)
    try:
        entry = CaptchaEntry.objects.get(sessionid = sessionid)
        if mode == "both":
            entry.canRegister = False
            entry.canCheckEmail = False
        elif mode == "email":
            entry.canCheckEmail = False
        elif mode == "register":
            entry.canRegister = False
        entry.save()
    except Exception: # pylint: disable=W0703
        return False
