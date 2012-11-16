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

from re import match

from django.contrib.auth.models import User as DjangoUser
from django.utils.translation import ugettext as __
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from accounts.human import CaptchaTestForm
from crypto.pw_hash import password_hash
from user.exceptions import NoAuthenticatedUser
from user.dropcounter import DropCounter
from user.location import put_request_geoip


class User(DjangoUser):
    """
    Custom User, with his very own password setting and checking devices
    """
    class Meta:
        """transient derived class"""
        # Don't create a new table
        proxy = True

    def set_password(self, raw_password):
        """
        Sets the password to the hashed and salted version defined in settings.
        """
        if raw_password is None:
            self.set_unusable_password()
        else:
            self.password = password_hash(raw_password)

    def check_password(self, raw_password):
        """
        Return True if  user's private container can be decrypted with
        raw_password. If the user is still old-style, this function instead
        calls the standard django User.check_password
        """
        if match(settings.ID_REGEX, self.username):
            try:
                profile = self.get_profile()
            except ObjectDoesNotExist:
                raise NoAuthenticatedUser
            rcode = bool(profile.decrypt(
                container="private", passphrase=raw_password)
            )
            if not rcode:
                print "*** %s can't decrypt with key %s" \
                    % (self.username, raw_password)
            return rcode
        else:
            # Old style user
            return super(User, self).check_password(raw_password)

    def prj_delete(self):
        """
        When a user deletes himself, we need to keep his drop container
        so what we actually do is deleting his user_profile:private_data,
        friend_public_data, auth_user:password, user_dropcounter[id] line
        send mail_manager a message that email address does not exist anymore
        send graph a message about him being deleted invalidating all requests
        from drops
        """
        self.password = ""
        self.is_active = False

        profile = self.get_profile()
        profile.private_data = ""
        profile.friend_public_data = ""

        if profile.allow_email:
            profile.notify_mailmanager(old_email=profile.email, new_email="")
        profile.send_delete_notification()

        try:
            my_dc = DropCounter.objects.get(uid = profile.uid)
            my_dc.delete()
        except ObjectDoesNotExist:
            pass

        profile.save(unsafe=True)
        self.save()

    def remove(self):
        """Django deletion method"""
        pass   

def generate_new_loginphrase():
    """
    Returns a (unused) password/loginphrase
    """
    try:
        password = User.objects.make_random_password(
            length = settings.LOGINPHRASE_LENGTH,
            allowed_chars=settings.ALPHABET
        )
        User.objects.get (password = password_hash(password))
        # If we get to here, the password already exists.
        # generate another one...
        return generate_new_loginphrase()
    except ObjectDoesNotExist:
        return password

def aboutme_errors(request, return_values = 4):
    """check for errors in 'about_me' data"""
    try:
        about_me = request.POST['about_me'].strip()
        if len(about_me) == 0:
            return (
                __('About me'), '4',
                __('Please provide at least some information'),
                "abouterror"
            )[0:return_values]
        elif len(about_me) > 10000:
            return (
                __('About me'), '4',
                __('Sorry, this is a little too much information " \
                    "for us to handle!'), "abouterror"
            )[0:return_values]
    except KeyError:
        return (
            __('About me'), '4',
            __('Please provide at least some information'),
            "abouterror"
        )[0:return_values]

def contactinfo_errors(request, return_values = 4):
    """check for errors in contact data"""
    try:
        contact_info = request.POST['contact_info'].strip()
        if len(contact_info) == 0:
            return (
                __('Contact info'), '4',
                __('Please provide at least some contact information'),
                "contacterror"
            )[0:return_values]
        elif len(contact_info) > 10000:
            return (
                __('Contact info'), '4',
                __('Sorry, this is a little too much information " \
                    "for us to handle!'), "contacterror"
                )[0:return_values]
    except KeyError:
        return (
            __('Contact info'), '4',
            __('Please provide at least some contact information'),
            "contacterror"
        )[0:return_values]

def is_inactive_user(email):
    """check for inactive user"""
    try:
        user = User.objects.get(email=email)
        if user.is_active:
            return False
        else:
            return True
    except ObjectDoesNotExist:
        return True

def set_register_vars(request, template_vars):
    """save registration data"""
    template_vars['title'] = __('Sign Up')
    template_vars['step'] = "1"
    put_request_geoip(request, template_vars)
    form = CaptchaTestForm()
    template_vars['captcha'] = form
    template_vars['step'] = "1"
    template_vars['numSteps'] = "5"
    template_vars['use_maps_single'] = True
    phrase = generate_new_loginphrase()
    template_vars['loginphrase'] = phrase
    request.session['loginphrase'] = phrase

def integer_id(cid):
    """
    convert the easily memorable ids like BF1942 to integers 
    (so that the django builtin User class can use it as id)
    """
    return int(str(ord(cid[0])) + str(ord(cid[1])) + str(cid[2:]))

def char_id(iid):
    """
    reverse of integerId.
    charId(integerId("XX1337") == "XX1337"
    """
    istr = str(iid)
    return str(chr(int(istr[0:2])) + chr(int(istr[2:4])) + istr[4:])

def get_username_from_loginphrase(_):
    """
    Deprecated since the Loginphrase does not contain the username anymore
    and we identify the accounts by their passwords directly
    """
    return "x"

def get_password_from_loginphrase(loginphrase):
    """
    Returns password from loginphrase input, tries to correct spelling
    mistakes and uppercases the whole thing.
    """
    result = ""
    loginphrase = loginphrase.upper()
    for char in loginphrase:
        if not char in settings.ALPHABET:
            if char in settings.TYPO_CONVERSION:
                char = settings.TYPO_CONVERSION[char]
            else:
                char = '?'
        result += char
    return result[:settings.LOGINPHRASE_LENGTH]

