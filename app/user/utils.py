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

from Crypto.Random import  get_random_bytes


def get_redirect_url(request):
    """create redirection url from referrer name"""
    referrer = request.META.get('HTTP_REFERER', 'x://y')
    server = referrer.split("://")[1].split("/")[0].split(":")[0]
    if request.META.get('SERVER_NAME',"") == server:
        return request.META.get('HTTP_REFERER',"/")
    else:
        return "/"

def as_float(rep, retry=False):
    """Convert string to Python float representation."""
    import string
    try:
        return float(rep)
    except ValueError:
        if retry:
            return 0.0
        rep = string.translate (rep, string.maketrans(",.'",".  "), " ") 
        return as_float(rep, True)

def generate_random_hex_field(chars=40):
    """
    Generate a Cryptographically secure hex field long
    as much as chars. Good for ids and salts.
    """
    keyspace = '0123456789abcdef'
    random_data = get_random_bytes(chars)
    return ''.join(keyspace[ord(x) % 16] for x in random_data)

