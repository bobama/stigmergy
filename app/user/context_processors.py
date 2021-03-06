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

def settings_vars(context):
    """set context variables"""
    smap = {}
    smap['DEVELOPMENT'] = settings.DEVELOPMENT
    smap['VERBOSE'] = settings.VERBOSE
    smap['NORMALSERVER'] = settings.NORMALSERVER
    smap['FEEDBACK_EMAIL'] = settings.FEEDBACK_EMAIL
    smap['TRANSLATIONS_DONE'] = settings.TRANSLATIONS_DONE
    if settings.VERBOSE:
        smap['context'] = context
    return smap
