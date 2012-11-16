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

from string import replace as str_replace
from math import sin, cos
from Crypto.Random import random

from django.utils.translation import check_for_language, ugettext as __
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation


def language_errors(request, return_values = 4):
    """find invalid languages"""
    try:
        languages = [code for code, _ in settings.SPOKEN_LANGUAGES]
        for i in range(6):
            lang = request.POST['lang_' + str(i)]
            if lang not in languages:
                return (
                    __('Language ') + str(i+1), '2',
                    __('"%(LANGUAGE)s" is not a valid language')
                        % { "LANGUAGE" : lang },
                    "languageserror"
                )[0:return_values]
    except KeyError:
        return (
            __('Language'), '2',
            __('You did not provide enough language tokens'),
            "languageserror"
        )[0:return_values]

def location_errors(request, return_values = 4):
    """find invalid locations"""
    try:
        longitude = float(str_replace(request.POST['longitude'], ",", "."))
        assert -180 <= longitude <= 180
    except KeyError:
        return (
            __('Longitude'), '3', __('Please provide a longitude'),
            "locationerror"
        )[0:return_values]
    except Exception:
        return (
            __('Longitude'), '3',
            __('"%(LONGITUDE)s" is not a valid longitude')
                % {"LONGITUDE":str(request.POST['longitude'])},
            "locationerror"
        )[0:return_values]

    try:
        latitude = float(str_replace(request.POST['latitude'], ",", "."))
        assert -90 <= latitude <= 90
    except KeyError:
        return (
            __('Latitude'), '3',
            __('Please provide a latitude'),
            "locationerror"
        )[0:return_values]
    except Exception:
        return (
            __('Latitude'), '3',
            '"%s" is not a valid latitude' % str(request.POST['latitude']),
            "locationerror"
        )[0:return_values]

def get_request_geoip(request):
    """get geo coordinates from request data"""
    if settings.NORMALSERVER:
        try:
            city = request.META.get("GEOIP_CITY","Moscow")
            country_name = request.META.get("GEOIP_COUNTRY_NAME","Russia")
            country_code = request.META.get("GEOIP_COUNTY_CODE","RU")
            region = request.META.get("GEOIP_REGION","")
            postal_code = request.META.get("GEOIP_POSTAL_CODE","12345")
            longitude = request.META.get("GEOIP_LONG","37")
            latitude = request.META.get("GEOIP_LAT","55")
            # IP addresses can't be read directly on our server.
            # Direct GeoIP not needed...
            return {
                'city': city,
                'region': region,
                'longitude': longitude,
                'latitude': latitude,
                'postal_code': postal_code,
                'country_code': country_code,
                'country_name': country_name
            }
        except Exception: # pylint: disable=W0703
            pass

    return {
        'city': 'Mountain View',
        'region': 'CA',
        'area_code': 650,
        'longitude': -122.05740356445312,
        'country_code3': 'USA',
        'latitude': 37.419200897216797,
        'postal_code': '94043',
        'dma_code': 807,
        'country_code': 'US',
        'country_name': 'United States'
    }

def put_request_geoip(request, template_vars):
    """store geoip data in template"""
    city_dict = get_request_geoip(request)
    template_vars['cityDict'] = city_dict

def display_in_native_language(request, user_profile):
    """display information in native language"""
    lang_code = user_profile.display_language
    refresh = False
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            disp_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME,"")
            if disp_lang != lang_code:         
                response = HttpResponseRedirect(request.path)
                response.set_cookie(
                    settings.LANGUAGE_COOKIE_NAME, value=lang_code,
                    secure = settings.SESSION_COOKIE_SECURE,
                    httponly = settings.SESSION_COOKIE_HTTPONLY
                )
                refresh = True
        translation.activate(lang_code)
    if refresh:
        return response
    return None


def randomize_location(lat, lon):
    """randomize location"""
    rnd1 = float("0."+"".join(str(random.randrange(10)) for x in range(32)))
    rnd2 = float("0."+"".join(str(random.randrange(10)) for x in range(32)))
    d_min = 100 # meters
    d_max = 700 # meters
    gamma = 6.35e-6 # meters^-1
    angle = -180 + 360 * rnd1 # degrees
    distance = d_min + (d_max - d_min) * rnd2 # meters

    # don't move when we are at the poles
    if -89 < lat < 89:
        lat = lat + distance * gamma * \
            (1 + (sin(lat))** 2) * sin(angle)
        lon = lon + distance * gamma * \
            (1 + (sin(lat)) ** 2) * cos(angle) / cos(lat)

    # take care at the edges - avoid invalid values
    if lat > 90:
        lat = 90 - ( lat - 90 )
    elif lat < -90:
        lat = -90 - ( lat - (-90) )
    if lon < -180:
        lon += 360
    elif lon > 180:
        lon -= 360

    return lat, lon

def generate_random_latitude():
    """
    creates a random coordinate
    """
    return str(90 - float(random.randrange(10000000))/10000000 * 180)

def generate_random_longitude():
    """
    creates a random coordinate
    """
    return str(180 - float(random.randrange(10000000))/10000000 * 360)

def generate_random_languages(num):
    """generate a random language"""
    return [random.choice(settings.SPOKEN_LANGUAGES)[0] for _ in range(num)]
