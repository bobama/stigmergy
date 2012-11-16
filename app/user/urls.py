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

from django.conf.urls.defaults import patterns
from django.conf import settings


urlpatterns = patterns( # pylint: disable=C0103
    'user.views',
    (r'^getNewCaptcha/?$', 'get_new_captcha'),
    (r'^validateCaptcha/?$', 'validate_captcha'),
    (r'^new/?$', 'register'),
    (r'^newsubmit/?$', 'new_submit'),
    (r'^profile/?$', 'profile_forwarding'),
    (r'^profile/edit/(?P<clicked>[a-zA-Z]*)/?$', 'edit_forwarding'),
    (r'^dropfriend/?$', 'drop_friend_forwarding'),
    (r'^(?P<friend_id>' + settings.ID_REGEX[1:-1] + ')/?$', 'user_forwarding'),
)
