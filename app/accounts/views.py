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

import urlparse
from re import match

from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout, login as auth_login
from django.contrib.auth import REDIRECT_FIELD_NAME, SESSION_KEY
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse
from django.db import connection, transaction
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from accounts.utils import loginphrase2username_password
from content.token import valid_token, token_splash_page
from user.encryption import handle_encrypted_login, populate_session, \
                            encrypt_unencrypted_profile
from user.entity import User, get_password_from_loginphrase
from user.exceptions import NoAuthenticatedUser

@csrf_protect
@never_cache
def django_login (request, template_name='registration/login.html',
                  redirect_field_name=REDIRECT_FIELD_NAME,
                  authentication_form=AuthenticationForm,
                  current_app=None, extra_context=None):
    """
    Copied from django.contrib.auth.views login().
    Added the call to encryption
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        try:
            form_valid = form.is_valid()
        except NoAuthenticatedUser:
            return no_authenticated_user(request)
        if form_valid:
            netloc = urlparse.urlparse(redirect_to)[1]
            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL
            # Okay, security checks complete. Log the user in.
            user = form.get_user()
            auth_login(request, user)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            # Remove the last_login timestamp immediately
            cursor = connection.cursor()
            cursor.execute("UPDATE auth_user " +
                           "SET last_login = '" + settings.MISC_LAST_LOGIN +
                           "' WHERE username = '%(username)s'"
                           % { "username":user.username })
            # Data modifying operation - commit required
            transaction.commit_unless_managed()
            if request.session.get("loginWithEmail",""):
                # Old style login. Need to give the user his new login phrase!
                return HttpResponseRedirect(reverse('accounts.views.newLogin'))
                
            handle_encrypted_login(request)
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)
    request.session.set_test_cookie()
    current_site = get_current_site(request)
    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    context.update(extra_context or {})
    return render_to_response (
        template_name, context,
        context_instance=RequestContext(request, current_app=current_app)
    )

# all login_required functions need a Forwarding function, so that token-less
# users can't infer anything about the server by guessing urls.

def login_forwarding(request, log_out=False):
    """
    login requested
    """
    if not valid_token(request):
        return token_splash_page(request)

    extra = {}
    extra.update({'title' : _('Login')})
    if "savedphrase" in extra:
        del extra["savedphrase"]
    if "just_logged_out" in extra:
        del extra["just_logged_out"]
    if "captchaerror" in extra:
        del extra["captchaerror"]
    if log_out:
        extra.update({'title' : _('You have been logged out.')})
        extra.update({'just_logged_out' : True })
    if request.method == "POST":
        # Split loginphrase in username and password. Also adds a flag to the
        # session so we can see which type of login was used.
        request.POST = loginphrase2username_password(request)
        if "captcha" in extra:
            del extra["captcha"]
    return django_login(request, extra_context=extra)

def logout_forwarding(request):
    """
    logout requested
    """
    if not valid_token(request):
        return token_splash_page(request)

    log_out = request.user.is_authenticated()
    if request.user.is_authenticated():
        auth_logout(request)
    return login_forwarding(request, log_out)

def delete_forwarding(request):
    """
    account deletion requested
    """
    if not valid_token(request):
        return token_splash_page(request)
    return delete(request)

@login_required
def delete(request, password_error=False):
    """
    account deletion
    """
    if not valid_token(request):
        return token_splash_page(request)

    if request.method == "GET" or password_error:
        template_path = 'registration/delete.html'
        template_vars = {}
        template_vars['title'] = _('Delete Profile')
        template_vars['passworderror'] = password_error
        return render_to_response(template_path, template_vars,
                                  context_instance=RequestContext(request))
    else:
        return delete_confirm(request)

def delete_confirm_forwarding(request):
    """
    forwarding on delete confirm request
    """
    if not valid_token(request):
        return token_splash_page(request)
    return delete_confirm(request)

@login_required
def delete_confirm(request):
    """
    confirm a delete request
    """
    if not valid_token(request):
        return token_splash_page(request)

    if request.POST.has_key('yes'):
        login_phrase = request.POST.get("password","")
        password = get_password_from_loginphrase(login_phrase)
        if request.user.check_password(password):
            template_path = 'registration/delete_confirm.html'
            template_vars = {}
            template_vars['title'] = _('Profile Deleted')
            user = request.user
            auth_logout(request)
            user.prj_delete()
            return render_to_response(template_path, template_vars,
                                      context_instance=RequestContext(request))
        else:
            return delete(request, password_error=_("Wrong password."))
    else:
        return redirect('/')

def new_login(request):
    """ 
    Careful - this function does not use django's login/logout functions
    intelligently. Bugs are likely to arise from here.
    """
    if not valid_token(request):
        return token_splash_page(request)

    if match(settings.ID_REGEX, request.user.username):
        # the user already has the new passphrase. Don't let him change it.
        return HttpResponseRedirect(reverse('user.views.profileForwarding'))

    template_path = 'registration/new_login.html'
    template_vars = {}
    template_vars['title'] = _('IMPORTANT')

    # Restore the user's session. If he tries to visit any other page,
    # he will remain logged out.
    if "savedSession" in request.session:
        for key, value in request.session["savedSession"].items(): 
            request.session[key] = value
        if SESSION_KEY in request.session:
            request.user = User.objects.get(id=request.session[SESSION_KEY])
        del request.session["savedSession"]
    user = request.user

    # Don't let people visit this page without logging in.
    # Copied from django.contrib.auth.decorators.user_passes_test
    if not user.is_authenticated():
        login_url = None
        path = request.build_absolute_uri()
        # If the login url is the same scheme and net location then just
        # use the path as the "next" url.
        login_scheme, login_netloc = urlparse.urlparse(login_url or
                                                       settings.LOGIN_URL)[:2]
        current_scheme, current_netloc = urlparse.urlparse(path)[:2]
        if ((not login_scheme or login_scheme == current_scheme) and
            (not login_netloc or login_netloc == current_netloc)):
            path = request.get_full_path()
        return redirect_to_login(path, login_url, REDIRECT_FIELD_NAME)

    user_profile = user.get_profile()
    if request.method == "POST":
        loginphrase_entered = request.POST.get("loginphrase","").upper()
        loginphrase = request.session.get("temploginphrase","")
        if loginphrase_entered == loginphrase:
            # The user received the passphrase and has hopefully written it
            # down. Because now we are changing his credentials.
            user.username = user_profile.id
            password = get_password_from_loginphrase(loginphrase)
            encrypt_unencrypted_profile(user_profile, password)
            user.email = user_profile.get_anonymous_email()
            user.set_password(password)
            user.save()
            populate_session(request, password)
            return HttpResponseRedirect(
                reverse('user.views.profileForwarding')
            )

    loginphrase = user_profile.generateNewLoginPhrase()
    template_vars['loginphrase'] = loginphrase
    request.session['temploginphrase'] = loginphrase

    # Delete the user's session: Stop the user from going to his profile pages
    # before he has entered the passphrase.
    saved_session = {}
    for key, value in request.session._session.items(): 
        saved_session[key] = value
    auth_logout(request)
    request.session["savedSession"] = saved_session
    template_vars['savedSession'] = saved_session

    return render_to_response(template_path, template_vars,
                              context_instance=RequestContext(request))

def no_authenticated_user(request):
    """
    This page is shown if a user logs in but his Profile is not finished
    with being encrypted.
    """
    if not valid_token(request):
        return token_splash_page(request)

    template_path = 'not_yet_encrypted.html'
    template_vars = {}
    return render_to_response(template_path, template_vars,
                              context_instance=RequestContext(request))
