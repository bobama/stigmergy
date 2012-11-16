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

from copy import deepcopy
from random import choice
 
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as __

from accounts.human import save_valid_captcha, invalidate_captcha, \
                           CaptchaTestForm,  edit_captcha_ok, \
                           edit_needs_captcha
from content.token import valid_token, token_splash_page
from user.registration import new_user
from user.utils import get_redirect_url
from user.encryption import restore_profile_from_session, populate_session, \
                            save_edited_info
from user.entity import set_register_vars, aboutme_errors, \
                        contactinfo_errors, get_password_from_loginphrase
from user.location import display_in_native_language, \
                           location_errors, language_errors
from user.mail import email_errors


def register(request):
    """Allows someone to register for the service"""
    if not valid_token(request):
        return token_splash_page(request)

    template_vars = {}
    template_path = 'registration/register.html'
    set_register_vars(request, template_vars)
    return render_to_response(template_path, template_vars,
                              context_instance=RequestContext(request))

def new_submit(request):
    """
    A new user submits their registration here
    """
    if not valid_token(request):
        return token_splash_page(request)

    if request.method == "POST":
        tpl_path, tpl_vars, _ = new_user(request, True)
        return render_to_response(
            tpl_path, tpl_vars,
            context_instance=RequestContext(request)
        )
    else:
        return register(request)

def profile_forwarding(request):
    """Own profile pages"""
    if not valid_token(request):
        return token_splash_page(request)
    return profile(request)

@login_required
def profile(request):
    """show profile"""
    if not valid_token(request):
        return token_splash_page(request)

    user_ = request.user
    profile_ = user_.get_profile()
    restore_profile_from_session(request, profile_)

    # show the page in the user's language
    response = display_in_native_language(request, profile_)
    if response:
        return response

    template_path = 'user/profile.html'
    template_vars = {}
    template_vars['title'] = __('My Profile')

    if request.method == "POST":
        if settings.VERBOSE:
            print "POST on the profile. this is a Drop-attempt"
        password = request.POST.get("loginphrase", "")
        dropped_fid = request.POST.get('dropped_fid', None)
        reason = request.POST.get('reason', "")
        comment = request.POST.get('comment', "")
        reason_map = {
            "unresponsive":"nice",
            "differences":"middle",
            "rude":"bad",
        }
        if settings.VERBOSE:
            print "Trying to drop %s for reason %s with comment\n%s" \
                % (dropped_fid, reason, comment)

        if user.check_password(password):
            if dropped_fid is not None and reason in reason_map:
                reason = reason_map[reason]
                dropped = profile_.defriend(dropped_fid, reason, comment)
                if dropped:
                    populate_session(request, password)
                    if dropped_fid in request.session:
                        del request.session[dropped_fid]
                    template_vars['droppedFriend'] = dropped_fid
                    template_vars['message'] = \
                        __('Your contact has been dropped. '
                            'We will find you another one soon.')
                    if settings.VERBOSE:
                        print "Drop successful."

        elif settings.VERBOSE:
            print "Drop failed: Wrong password"

    template_vars['user'] = user_
    template_vars['profile'] = profile_
    template_vars['localFriends'] = \
        profile_.friend_list(request.session, friend_type="local") + \
        request.session.get("display_local", [])
    template_vars['remoteFriends'] = \
        profile_.friend_list(request.session, friend_type="remote") + \
        request.session.get("display_remote", [])
    template_vars['ownUniqueLanguages'] = \
        set(profile_.get_unique_languages())
    template_vars['newFriends'] = request.session.get("new_friends", [])
    template_vars['use_maps_multiple'] = True

    if request.session.get("changes_saved", False):
        template_vars['success_message'] = __("Changes saved.")
        del request.session['changes_saved']

    if settings.VERBOSE:
        print "============SESSION DUMP============"
        for key, value in request.session.items():
            print key, smart_str(value)

    return render_to_response(
        template_path, template_vars,
        context_instance=RequestContext(request)
    )

def edit_forwarding(request, clicked):
    """edit profile request"""
    if not valid_token(request):
        return token_splash_page(request)

    return edit(request, clicked)

@login_required
def edit(request, clicked):
    """edit profile"""
    if not valid_token(request):
        return token_splash_page(request)

    template_vars = {}
    if request.method == "POST":
        loginphrase = request.POST.get("password","")
        password = get_password_from_loginphrase(loginphrase)
        if request.user.check_password(password):
            if edit_captcha_ok(request):
                validation_errors =  contactinfo_errors(request) or \
                                     aboutme_errors(request) or \
                                     location_errors(request) or \
                                     language_errors(request) or \
                                     email_errors(request) or None
                if validation_errors:
                    validation_errors = ([contactinfo_errors(request)] + \
                                         [aboutme_errors(request)] + \
                                         [location_errors(request)] + \
                                         [language_errors(request)] + \
                                         [email_errors(request)])
                    for val_error in validation_errors:
                        if val_error is not None:
                            template_vars[val_error[-1]] = val_error[2]
                else:
                    save_edited_info(request)
                    # Get the newly encrypted data into the session again
                    populate_session(request, password)
                    return HttpResponseRedirect(
                        reverse('user.views.profile_forwarding')
                    )
            else:
                template_vars["captchaerror"] = True
                template_vars["captcha"] = CaptchaTestForm(request.POST)
        else:
            template_vars["passworderror"] = __("Wrong passphrase.")
    else:
        if edit_needs_captcha(request):
            template_vars["captcha"] = CaptchaTestForm()
            
    template_vars['contact_info'] = request.POST.get("contact_info", False)
    template_vars['about_me'] = request.POST.get("about_me", False)
    template_vars['email'] = request.POST.get("email", False)
    template_vars['user'] = request.user
    profile_ = request.user.get_profile()
    restore_profile_from_session(request, profile_)
    template_vars['profile'] = profile_

    for num, lang in enumerate(profile_.get_langs_spoken()):
        template_vars['lang_'+str(num)] = \
            request.POST.get("lang_" + str(num), lang)

    template_vars['use_maps_single'] = True
    template_vars['cityDict'] = {
        'latitude' : request.POST.get("latitude", profile_.latitude),
        'longitude' : request.POST.get("longitude", profile_.longitude),
    }
    template_vars["clicked"] = clicked
    template_vars['title'] = __('Edit the information about you')
    template_path = "user/edit_profile.html"

    return render_to_response(template_path, template_vars,
                              context_instance=RequestContext(request))

def user_forwarding(request, friend_id):
    """friend profile request"""
    if not valid_token(request):
        return token_splash_page(request)
    return user(request, friend_id)

@login_required
def user(request, friend_id):
    """show friend profile"""
    if not valid_token(request):
        return token_splash_page(request)

    template_vars = {}
    user_ = request.user
    profile_ = user.get_profile()
    restore_profile_from_session(request, profile_)
    local_friends = profile_.friend_list(request.session, friend_type="local")
    remote_friends = profile_.friend_list(request.session, friend_type="remote")

    template_vars['user'] = user_
    template_vars['profile'] = profile_
    template_vars['localFriends'] = local_friends
    template_vars['remoteFriends'] = remote_friends
    template_vars['friend_id'] = friend_id

    found = False
    friend = None
    for frnd in local_friends:
        if frnd.profile.id == friend_id:
            template_vars['friend'] = frnd
            friend = frnd
            found = True
            friend_type = "local"
            break
    if not found:
        for i, frnd in enumerate(remote_friends):
            if frnd.profile.id == friend_id:
                template_vars['match_lang'] = profile.get_global_token(i)
                template_vars['friend'] = frnd
                friend = frnd
                found = True
                friend_type = "global"
                break
      
    if not found and friend_id == profile.id:
        class XFriend(object):
            """temporary friend class"""
            def __init__(self, prf):
                """init xfriend instance"""
                self.profile = prf
        me_as_friend = XFriend(profile_)
        template_vars['ownPage'] = True
        template_vars['friend'] = me_as_friend
        friend_type = choice(["global", "local"])
        friend = me_as_friend
        found = True

    if found:
        template_vars['uniqueLanguages'] = friend.profile.getUniqueLanguages()
        template_vars['ownUniqueLanguages'] = profile_.getUniqueLanguages()

        template_path = 'user/user_found.html'
        template_vars['title'] = __('Friend') + ' ' + \
            friend.profile.human_public_name()
        template_vars['use_maps_single'] = True
        template_vars['friendType'] = friend_type
        template_vars['cityDict'] = {
           'latitude' : friend.profile.latitude,
           'longitude' : friend.profile.longitude,
        }
    else:
        template_vars['title'] = \
            __('Friend %(friend_id)s not found') % {'friend_id' : friend_id}
        template_path = 'user/user_not_found.html'

    return render_to_response(
        template_path, template_vars,
        context_instance=RequestContext(request)
    )

def drop_friend_forwarding(request):
    """drop request"""
    if not valid_token(request):
        return token_splash_page(request)
    return drop_friend(request)

@login_required
def drop_friend(request):
    """drop contact"""
    if not valid_token(request):
        return token_splash_page(request)

def select_lang(request):
    """select language request"""
    if not valid_token(request):
        return token_splash_page(request)

    template_vars = {}
    template_vars['title'] = __('Select language')
    template_vars['previouspage'] = get_redirect_url(request)
    template_path = 'i18n/setlang.html'

    return render_to_response(template_path, template_vars,
                              context_instance=RequestContext(request))

def get_new_captcha(request):
    """get new captcha image"""
    if not valid_token(request):
        return token_splash_page(request)

    invalidate_captcha(request)
    form = CaptchaTestForm()
    new_form = ""
    for field in form:
        new_form += str(field)
    return HttpResponse (new_form)

def validate_captcha(request):
    """validate captcha"""
    if not valid_token(request):
        return token_splash_page(request)
  
    # extract captcha data from request
    test = deepcopy(request.POST)
    cid = request.GET.get("captchaid", "")
    ctext = request.GET.get("captchatext", "")
    test.__setitem__('captcha_0', cid)
    test.__setitem__('captcha_1', ctext)

    captcha_form = CaptchaTestForm (test)
    
    if not captcha_form.is_valid():
        invalidate_captcha(request)
        return HttpResponse("fail")
    else:
        save_valid_captcha(request)
        return HttpResponse("win")
