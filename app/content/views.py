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

from django import http
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import check_for_language, ugettext as _
import django.views.i18n as i18n

from content.token import valid_token, token_splash_page, has_valid_token_cookie
from user.encryption import restore_profile_from_session


def home(request):
    """show home page"""
    if not valid_token(request):
        return token_splash_page(request)

    # copied from i18n - required to give users their language
    # after entering a token
    if request.method == 'POST':
        next_page = request.REQUEST.get('next', None)
        if not next_page:
            next_page = request.META.get('HTTP_REFERER', None)
        if not next_page:
            next_page = '/'
        response = http.HttpResponseRedirect(next_page)
        # give users the token which they have just entered as a cookie
        if not has_valid_token_cookie(request):
            response.set_cookie(
                "prj_token", value=request.POST.get('token', None),
                secure = settings.SESSION_COOKIE_SECURE,
                httponly = settings.SESSION_COOKIE_HTTPONLY)
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            if hasattr(request, 'session'):
                request.session['django_language'] = lang_code
            else:
                response.set_cookie(
                    settings.LANGUAGE_COOKIE_NAME, value=lang_code, 
                    secure = settings.SESSION_COOKIE_SECURE,
                    httponly = settings.SESSION_COOKIE_HTTPONLY)
    else:
        template_path = 'content/index.html'
        template_vars = {'title' : _('Welcome to STIGMERGY!'), 'quote' : True}
        response = render_to_response(
            template_path, template_vars,
            context_instance=RequestContext(request)
        )

    return response

def about(request):
    """show about page"""
    if not valid_token(request):
        return token_splash_page(request)

    template_path = 'content/all_content.html'
    template_vars = {}
    return render_to_response(
        template_path, template_vars,
        context_instance=RequestContext(request)
    )

def membership(request):
    """show info about project membership"""
    if not valid_token(request):
        return token_splash_page(request)

    template_path = 'content/membership.html'
    template_vars = {}
    return render_to_response(
        template_path, template_vars,
        context_instance=RequestContext(request)
    )

def faq(request):
    """show faq page"""
    if not valid_token(request):
        return token_splash_page(request)

    template_path = 'content/faq.html'
    template_vars = {}
    return render_to_response(
        template_path, template_vars,
        context_instance=RequestContext(request)
    )

def i18n_forwarding(request):
    """select display language"""
    if not valid_token(request):
        return token_splash_page(request)

    if request.user.is_authenticated():
        user_profile = request.user.get_profile()
        restore_profile_from_session(request, user_profile)
        old_lang = user_profile.display_language
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            user_profile.display_language = lang_code

        if old_lang != user_profile.display_language:
            user_profile.notify_mailmanager (
                user_profile.email,user_profile.email
            )
        user_profile.save()
        request.session["display_language"] = user_profile.display_language
    return i18n.set_language(request)

def maintenance(request):
    """show maintenance page"""
    return render_to_response(
        "maintenance.html", {},
        context_instance=RequestContext(request)
    )
