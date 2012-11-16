"""
Mail messages

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
from django.utils.translation import ugettext as __
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from user.encryption import encrypt_notification


class Mail(models.Model):
    """
    Users can send messages to this class,
    such as when they change their email address.
    """
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key in self.schema["fields"]:
                setattr(self, key, value)
        if not hasattr(self, "deleted"):
            self.deleted = False #todo: throw WTF at lorenzo
        encrypted_data = encrypt_notification(self)
        super(Mail, self).__init__(data = encrypted_data)

    schema = {
        "keys" : [settings.CRYPTO_KEY_MAIL],
        "fields" : [
            "email",
            "languages",
            "pref_lang",
            "timezone", # Could be "unknown" or an integer
            "deleted",
        ],
    }
    data = models.TextField()   

def email_errors(request, return_values = 4):
    """check for email errors"""
    if request.POST.get('allow_email', False):
        try:
            email = request.POST['email']
            validate_email(email)
            if len(email) > 75:
                return (
                    __('Email'), '1', __('The email address is too long'),
                    "emailerror"
                )[0:return_values]
        except KeyError:
            return (
                __('Email'), '1', __('You need to enter an email address'),
                "emailerror"
            )[0:return_values]
        except ValidationError:
            return (
                __('Email'), '1', __('"%(EMAIL)s" is not a valid email') \
                % {"EMAIL":email}, "emailerror"
            )[0:return_values]
    else:
        return None
