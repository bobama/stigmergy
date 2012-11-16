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

from user.entity import get_password_from_loginphrase, \
                        get_username_from_loginphrase


MAX_LOGIN_ATTEMPTS = 3
LOGIN_ATTEMPT_TIMEOUT = 10

def loginphrase2username_password(request):
    """convert login phrase to username/password pair"""
    phrase = request.POST.get("loginphrase","")
    username = get_username_from_loginphrase(phrase)
    password = get_password_from_loginphrase(phrase)
    clone = request.POST.copy()
    clone["username"] = username
    clone["password"] = password
    return clone

def remove_password(request):
    """remove password from request"""
    clone = request.POST.copy()
    clone["password"] = ""
    request.POST = clone
    return request.POST
