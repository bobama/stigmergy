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

from django.conf import settings

if not settings.TOKENSACTIVE and not settings.SPLASHPAGENOTOKENS:
    
    ###################################################################
    #### no tokens used for the project
    ###################################################################

    from django.http import Http404
    def valid_token(request): # pylint: disable=W0613
        """no function"""
        return True
    def has_valid_token_cookie(request): # pylint: disable=W0613
        """no function"""
        return True
    def validate_token_in_db(token): # pylint: disable=W0613
        """no function"""
        return True
    def token_splash_page(request): # pylint: disable=W0613
        """no function"""
        raise Http404

else:
    ###################################################################
    #### token module
    ###################################################################

    from django.contrib.auth import logout
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    from django.utils.translation import ugettext as _
    from django.utils.datastructures import MultiValueDictKeyError
    from content.models import Token
    from django.http import HttpRequest, Http404

    def valid_token(request):
        """check for valid token"""
        if has_valid_token_cookie(request):
            return True
        
        if request.method == 'POST':
            try:
                token = request.POST["token"]
                return validate_token_in_db(token)
            except MultiValueDictKeyError:
                return False
        else:
            return False

    def has_valid_token_cookie(request):
        """check for valid token cookie"""
        try:
            token = request.COOKIES["prj_token"]
            return validate_token_in_db(token)
        except Exception: # pylint: disable=W0703
            return False

    def validate_token_in_db(token):
        """store token in database"""
        if settings.SPLASHPAGENOTOKENS:
            return str(token)=="prjtoken"
      
        try: 
            test_token = Token.objects.get(token_string=token)
            if test_token.ever_used == 0:
                test_token.ever_used = 1
                test_token.save()
            return True
        except Exception: # pylint: disable=W0703
            return False

    def token_splash_page(request):
        """show token splash page"""
        if valid_token(request): #User got here by entering a non-existent URL
            raise Http404

        #This is shown on any page, to users who have no valid token 
        logout(request)
        template_vars = {}
        if settings.SPLASHPAGENOTOKENS:
            template_path = 'splash_no_tokens.html'
        else:
            template_path = 'splash.html'
            template_vars['thispage'] = HttpRequest.get_full_path(request)
        template_vars.update({
            'title' : _('Welcome to STIGMERGY!'),
            'subtitle' : _('<prj_subtitle>')
        })
        return render_to_response(template_path, template_vars,
                                  context_instance=RequestContext(request))
