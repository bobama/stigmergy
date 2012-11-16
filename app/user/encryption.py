"""
Some helper functions to carry the unencrypted data through the webpage

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

import json

from django.conf import settings
from django.db import IntegrityError
from django.utils.translation import check_for_language

from crypto.gpg_crypt import gpg_encrypt
from user.dropcounter import DropCounter
from user.friend import SpecialFriend
from user.utils import as_float
from user.location import randomize_location


def encrypt_notification(instance):
    """
    Used for messages to the graph and the mail manager
    """
    info = instance.schema
    keys = info["keys"]
    fields = info["fields"]
    data_map = {}
    for field in fields:
        data_map[field] = getattr(instance, field, "")
    data = json.dumps(data_map)
    if settings.VERBOSE:
        print "########"
        print "Encrypting message to %s data:\n %s" % (instance, data)
    encrypted_data = gpg_encrypt(str(data), keys)
    if settings.VERBOSE:
        print "Encrypted data:\n %s\n\n\n\n" % encrypted_data
    return encrypted_data

def handle_encrypted_login(request):
    """
    Stores the decrypted data in the session and
    checks if the user has new friends
    """
    password = request.POST.get("password","")
    populate_session(request, password)
    process_graph_message(request, password)

def generate_keypair(profile, passphrase):
    """
    This function could be used to assign previously
    generated keypairs to the users...
    """
    profile.gen_key(passphrase)

def encrypt_unencrypted_profile(profile, passphrase):
    """
    Takes a Profile instance which has values saved in cleartext
    in the DB. Generates a key for the user, encrypts his data with
    that key and deletes the data from the db.
    """
    # Give the instance its password in RAM and
    # create a key pair with the password
    profile.pwd = passphrase
    generate_keypair(profile, passphrase)

    # Fill new fields
    profile.email = profile.user.email
    profile.allow_email = True
    profile.unique_langs = profile.get_unique_languages()
    profile.local_friend_str = "," + settings.NUM_LOCAL_FRIENDS * "0,"
    profile.remote_friend_str = "," + settings.NUM_REMOTE_FRIENDS * "0,"
    profile.global_token_str = "," + settings.NUM_REMOTE_FRIENDS * "0,"
    profile.former_friend_str = ""
    profile.keep_friend_str = ""

    # Add a row to the DropCounter table
    try:
        dcnt = DropCounter.objects.create (uid = profile.uid)
    except IntegrityError as exc:
        print "encryptNonEncryptedProfile: Couldn't initiate DropCounter " \
            "with id=%s. It already exists!" % profile.uid
        print exc
    else:
        dcnt.init()

    profile.refresh_dropped_signal()
    profile.send_friend_request()
    profile.save()

def populate_session(request, password):
    """
    This is the main decryption function.
    After a user logs in with his loginphrase, decrypt the data stored in the
    user's private & public containers and store the data in the session so
    that it is available on all pages of the website.
    """
    session = request.session
    profile = request.user.get_profile()
    if settings.VERBOSE:
        print "Populating session with data from %s" % profile.uid
    profile.pwd = password
    populate_session_owndata(profile, session)
    populate_session_frienddata(profile, session)

def populate_session_owndata(profile, session):
    """get private data"""
    # Own private data
    profile.container_to_transient(container="private")
    # Own public data
    profile.container_to_transient(container="friend_public")

    # maybe it would be smarter to store the data
    # as a profile instance in the session (like
    # the friend data) and not as separate values.
    for fields in [
        profile.meta_info("private")["fields"],
        profile.meta_info("friend_public")["fields"]
    ]:
        for field in fields:
            session[field] = getattr(profile, field, fields[field])

def populate_session_frienddata(profile, session):
    """get public data of friends"""
    send_graph_msg = False
    session["display_local"] = []
    session["display_remote"] = []
    # Friends' public data
    for friend in profile.friend_list():
        fprofile = friend.profile
        if not fprofile.friend_public_data == "":
            if fprofile.container_to_transient(
                container = "friend_public", privateKeyFp = profile.keyfp,
                passphrase = profile.pwd
            ):
                session[fprofile.uid] = friend
            else:
                try:
                    # This guy might have dropped us.
                    # Decrypt the drop msg
                    drop_signal = profile.read_dropped_msg(
                        fprofile, keyid=profile.keyfp, passphrase = profile.pwd
                    )
                    if drop_signal == settings.DROPPED_CONTENT:
                        key = "display_%s" % profile.localOrRemote(fprofile.id)
                        session[key].append(
                            SpecialFriend(fprofile, "droppedme")
                        )
                        profile.process_drop_by(fprofile.uid)
                        send_graph_msg = True
                    else:
                        # Nope, he has not dropped us.
                        raise ValueError
                except ValueError:
                    # The friend has not added us to his key list yet.
                    # This is simply giving the friend an empty profile with
                    # the single attribute speciality="stillencrypted". 
                    session[profile.uid] = \
                        SpecialFriend(fprofile, "stillencrypted")
        else:
            # This guy has deleted himself.
            key = "display_%s" % profile.localOrRemote(fprofile.uid)
            session[key].append(
                SpecialFriend(fprofile, "droppedme")
            )
            profile.process_deleted_friend(fprofile.uid)
            send_graph_msg = True

    if send_graph_msg:
        session.modified = True
        profile.send_friend_request()
        # Save changes to the DB
        # This re-encrypts the public_info container with the correct keys.
        profile.save()
        # Reload the new data into the session
        populate_session_owndata(profile, session)

def restore_profile_from_session(request, profile):
    """
    Reads the plaintext data out of the session and gives the
    Profile instance its attributes back.
    """
    sess = request.session
    for fields in [
        profile.meta_info("private")["fields"],
        profile.meta_info("friend_public")["fields"]
    ]:
        for field in fields:
            try:
                setattr(profile, field, sess[field])
            except KeyError:
                print "KeyError: Couldn't find %s in the session of user %s " \
                    "for unknown reasons.\nSetting it to default: %s" % \
                    (field, sess.get("_auth_user_id","UNKNOWN"), fields[field])
                setattr(profile, field, fields[field])

def process_graph_message(request, password):
    """read message from graph algorithm"""
    profile = request.user.get_profile()
    if profile.assignment_data:
        if settings.VERBOSE:
            print "Getting new friends!"
        restore_profile_from_session(request, profile)
        profile.pwd = password
        
        # Read what the graph is telling us...
        # And add new friends to the profile.
        profile.container_to_transient(container="assignment")
        profile.add_friends_from_graph()
        
        # Delete the processed message
        profile.assignment_data = ""
        profile.save()
        request.session["got_new_friends"] = True
        request.session["new_friends"] = \
            profile.friend_fids_as_list("new_local") + \
            profile.friend_fids_as_list("new_remote")
        if settings.VERBOSE:
            print request.session["new_friends"]
        request.session.modified = True
        populate_session(request, password)
        
        # In case we didn't get enough friends from the graph,
        # request new ones. If we DID get enough friends, this
        # doesn't do anything.
        profile.send_friend_request() 

def save_edited_info(request):
    """
    Post-processes and saves the information that was entered by the user when
    he edits his profile. Sends change-notifications to the appropriate
    recipients 
    """
    profile = request.user.get_profile()
    restore_profile_from_session(request, profile)

    # Get old values for comparison
    old_lat, old_lon = profile.latitude, profile.longitude
    old_email = profile.email
    old_allow_email = profile.allow_email
    old_timezone = profile.get_timezone()
    old_unique_langs = set(profile.get_unique_languages())
    old_global_langs_needed = set(profile.get_global_langs_needed())
    
    # Randomize the entered coordinates
    longitude = as_float(request.POST.get('longitude', profile.longitude))
    latitude = as_float(request.POST.get('latitude', profile.latitude))
    fudged_latitude, fudged_longitude = randomize_location(latitude, longitude)

    languages = []
    # this could be more than len(old Langs)
    for i in range(settings.NUM_REMOTE_FRIENDS):
        lang_i = request.POST.get("lang_" + str(i), None)
        if lang_i is not None and check_for_language(lang_i):
            languages.append(lang_i)

    profile.set_langs_spoken(languages)
    profile.about_me = request.POST.get("about_me", profile.about_me)
    profile.contact_info = \
        request.POST.get("contact_info", profile.contact_info)
    profile.email = request.POST.get("email", old_email)
    profile.allow_email = request.POST.get("allow_email", False)

    position_changed = \
        (abs(old_lat-latitude) > 1e-8 or abs(old_lon-longitude) > 1e-8)
    if position_changed:
        profile.latitude = fudged_latitude
        profile.longitude = fudged_longitude

    unique_langs_changed = \
        (old_unique_langs != set(profile.get_unique_languages()))
    global_langs_needed_changed = \
        (old_global_langs_needed != set(profile.get_global_langs_needed()))
    timezone_changed = (old_timezone != profile.get_timezone())
    email_changed = (old_email != profile.email)
    allow_email_changed = (old_allow_email != profile.allow_email)

    if settings.VERBOSE:
        print "***", profile.allow_email, allow_email_changed, old_allow_email

    if allow_email_changed:
        if profile.allow_email:
            profile.notify_mailmanager(new_email=profile.email, old_email="")
        else:
            profile.notify_mailmanager(new_email="", old_email=old_email)
            profile.email = ""
    elif profile.allow_email and \
        (unique_langs_changed or timezone_changed or email_changed):
        profile.notify_mailmanager(
            new_email=profile.email, old_email=old_email
        )

    # We don't always need to send a message to the graph if a language token
    # changes. No message needed when there is a global friend still sitting
    # on that token. Thus globalLangsNeededChanged and not simply
    # languagesChanged.
    if position_changed or unique_langs_changed or global_langs_needed_changed:
        profile.send_friend_request()

    profile.save()
    request.session["changes_saved"] = True
