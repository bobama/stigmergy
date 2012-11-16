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

def settings_vars(request):
    """set context variables"""
    smap = {}
    smap['DEBUG'] = settings.DEBUG
    smap['TRANSLATED_LANGUAGES'] = sorted(settings.TRANSLATED_LANGUAGES)
    smap['SPLASH_LANGUAGES'] = sorted(settings.SPLASH_LANGUAGES)
    smap['SPOKEN_LANGUAGES'] = settings.SPOKEN_LANGUAGES
    smap['SESSION_COOKIE_HTTPONLY'] = settings.SESSION_COOKIE_HTTPONLY
    smap['SESSION_COOKIE_SECURE'] = settings.SESSION_COOKIE_SECURE
    try:
        smap['hide_lang_box'] = request.COOKIES["hide_lang_box"]
    except Exception: # pylint: disable=W0703
        pass
    return smap
