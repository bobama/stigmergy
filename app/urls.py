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
from django.conf.urls.defaults import patterns, include
from django.views.generic.simple import direct_to_template


urlpatterns = patterns( # pylint: disable=C0103
     '',
     (r'^robots\.txt$', direct_to_template,
         {'template': 'misc/robots.txt', 'mimetype': 'text/plain'}
     ),
)

if settings.UNDER_MAINTENANCE:
    urlpatterns += patterns(
        '',
        (r'.*', 'content.views.maintenance'), # Maintenance page
    )

else:
    urlpatterns += patterns(
        '',
        # Static content pages
        (r'^/?$', 'content.views.home'),
        (r'^about/?$', 'content.views.about'),
        (r'^membership/?$', 'content.views.membership'),
        (r'^faq/?$', 'content.views.faq'),        

        # Language selection
        (r'^i18n/selectlang/?$', 'user.views.select_lang'),
        (r'^i18n/setlang/$', 'content.views.i18n_forwarding'),

        # User pages: register, profiles...
        (r'^user/', include('user.urls')),

        # preconfigured django login logout etc
        (r'^accounts/', include('accounts.urls')),

        # captcha
        (r'^captcha/', include('captcha.urls')),

    )

    #ALL other requests
    urlpatterns += patterns(
        '',
        #This must be the LAST pattern
        (r'.*', 'content.token.token_splash_page'),
    )
