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

import json
import traceback
import sys
from Crypto.Random import random

from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str

from crypto.prj_crypt import msg_encrypt, msg_decrypt, gen_keypair
from user.entity import User, char_id
from user.dropcounter import DropCounter
from user.exceptions import CantEncryptPublicInfo
from user.graph import Graph
from user.friend import Friend
from user.mail import Mail


class Profile(models.Model):
    """user profile class"""

    ##############
    ####fields ###
    ##############
    uid = models.CharField(max_length=10, primary_key=True)
    user = models.OneToOneField(User)
    keyfp = models.CharField(max_length=40)

    # keyfp should have unique=True, but this can not be implemented
    # while there are still users who have not generated a key pair for
    # themselves. Add unique=True when the unencrypted users have been
    # deleted from the database.
    allow_email = False 

    # Encrypted data containers
    private_data = models.TextField()
    friend_public_data = models.TextField()
    assignment_data = models.TextField()

    # Text "DROPPED" encrypted with dropped friends' public keys
    dropped_signal = models.TextField()

    # Plaintext fields.
    latitude = 0.0
    longitude = 0.0
    about_me = ""
    contact_info = ""
    display_language = ""
    lang_str = ""

    pwd = ""
    remote_friend_str = ""
    local_friend_str = ""
    global_token_str = ""
    drop_comments = None
    former_friend_str = ""
    keep_friend_str = ""
    unique_langs = ""
    email = ""


    def save(self, unsafe=False):
        """
        Overwrite save() function to make sure that the un-encrypted
        data is never saved to the database.
        """
        if not unsafe:
            self.unencrypted_data_to_container("private")
            self.unencrypted_data_to_container("friend_public")
            self.delete_unencrypted_data()
        super(Profile, self).save()

    #######################
    ### data encryption ###
    #######################

    def meta_info(self, container):
        """meta data structures"""
        if container == "private":
            return { 
                "keys": [self.keyfp],
                "fields": {
                    "friend_public_keys": "", 
                    "display_language": "en", 
                    "lang_str": ",en,en,en,en,en,en,",
                    "local_friend_str": ",0,0,0,0,0,0,", 
                    "remote_friend_str": ",0,0,0,0,0,0,", 
                    "global_token_str": ",0,0,0,0,0,0,",
                    "former_friend_str": "",
                    "keep_friend_str": "",
                    "extra_dropped_msg_friend_str": "",
                    "drop_comments": [],
                    "email": "",
                    "allow_email": False,
                },
            }
        elif container == "friend_public":
            return { 
                "keys": self.get_own_and_friend_keys(),
                "fields": {
                    "about_me": "",
                    "contact_info": "",
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "unique_langs": ["en"],
                },
            }
        elif container == "assignment":
            return { 
                "keys": [self.keyfp],
                "fields": {
                    "new_local_friend_str": "", 
                    "new_remote_friend_str": "", 
                    "new_global_token_str": "",
                },
            }

    def delete_unencrypted_data(self):
        """
        Delete data (private, friend_public) from the object's fields.
        This should always be called before calling .save() on the object
        to ensure that plaintext data is not written to the database.
        Should usually be called after writeUnencryptedDbDataToContainer
        in order not to lose the data.
        """
        private_info = self.meta_info("private")
        private_fields = private_info["fields"]
        public_info = self.meta_info("friend_public")
        public_fields = public_info["fields"]
        fields = public_fields.keys() + private_fields.keys()

        for field in fields:
            if hasattr(self, field):
                if isinstance(getattr(self, field), (float, int)):
                    setattr(self, field, 0)
                    if settings.VERBOSE:
                        print "Just deleted field %s from user %s" \
                            % (field, self.uid)
            else:
                setattr(self, field, "")
                if settings.VERBOSE:
                    print "Just deleted field %s from user %s" \
                        % (field, self.uid)

    def write_session_to_container(self, request, container=""):
        """
        unused function, we are rather restoring instances of this class 
        from the session and then saving instance variables to DB (i.e. this
        function in two steps)
        """
        info = self.meta_info(container)
        keys = info["keys"]
        fields = info["fields"]
        data_map = {}
        for field in fields:
            data_map[field] = request.session.get(field, fields[field])
        data = json.dumps(data_map)
        self.encrypt(container, data, keys)

    def unencrypted_data_to_container(self, container=""):
        """
        This function takes the relevant unencrypted values from the transient
        instance variables (or from database fields), encrypts them with the
        container-keys and saves them to container_data
        """
        info = self.meta_info(container)
        keys = info["keys"]
        fields = info["fields"]
        data_map = {}
        for field in fields:
            data_map[field] = getattr(self, field, fields[field])
        data = json.dumps(data_map)
        self.encrypt(container, data, keys)

    def container_to_transient(self, container="", prv_key="", passphrase=""):
        """
        Decrypt the data in container and save it into variables of the
        instance of Profile. Ignore the meta_info objects and simply
        stick the decrypted JSON object to the instance.
        """
        json_data = smart_str(self.decrypt(container, prv_key, passphrase))
        if json_data == "":
            return False
        try:
            data = json.loads(json_data)
        except ValueError:
            print "*** JSON faled on '%s'" % json_data
            return False
        for field, value in data.items():
            setattr(self, field, value)
            if settings.DEBUG:
                print "I just set %s to %s" % (field, smart_str(value))
        return True

    def get_own_and_friend_keys(self):
        """
        Returns a list of the friends' public keys, plus the own public key.
        Only works if the password for the private key of the user is in
        self.pwd or the list is already decrypted.
        To be more flexible and up-to-date, this should pull the key
        fingerprints from the database and not from the private container.
        Or maybe this would be a security risk?
        """
        try:
            friend_keys = self.db_csv_to_array("friend_public_keys")
        except AttributeError:
            if hasattr(self, "pwd"):
                # Gotta decrypt the private data to get the list
                # of friends' keys.
                self.container_to_transient(
                    container="private", passphrase=self.pwd
                )
                friend_keys = self.db_csv_to_array("friend_public_keys")
            else:
                raise CantEncryptPublicInfo
        return friend_keys + [self.keyfp]

    def read_dropped_msg(self, friend, keyid=None, passphrase=None):
        """
        Return the content of dropped_signal of the given friendProfile.
        If the keyid can not decrypt the contents, return None.
        """
        if keyid is None:
            keyid = self.keyfp
        if passphrase is None:
            try:
                passphrase = self.pwd
            except AttributeError:
                if settings.VERBOSE:
                    print "trying to decrypt, but no passphrase given. exiting."
                traceback.print_stack(file=sys.stdout)
                return None

        data = getattr(friend, "dropped_signal", "")
        if settings.VERBOSE:
            print "########"
            print "Decrypting the dropped message from %s's profile with key " \
                "%s passphrase %s*" % (friend.id, keyid, passphrase[0:3])
            print "DATA:\n%s" % data
        decrypted_data = msg_decrypt (str(data), keyid, passphrase)
        if settings.VERBOSE:
            print "Decrypted data:\n %s\n\n\n\n" % decrypted_data.data
        return decrypted_data.data or None

    def encrypt(self, container="", data="", keys=[]):
        """
        Takes as argument the container to encrypt to and the data that should
        be a json string, encrypts it with keys and stores the encrypted data
        into container_data.
        """
        if settings.VERBOSE:
            print "########"
            print "Encrypting to container %s data:\n %s" % (container, data)

        data = msg_encrypt(str(data), keys, hidden=True)
        setattr(self, container+"_data", data)
        if settings.VERBOSE:
            print "Encrypted data:\n %s\n\n\n\n" \
                % (getattr(self, container+"_data", "") )

    def decrypt(self, container="", keyid=None, passphrase=None):
        """
        Decrypts the data stored inside self.{{container}} using the specified
        keyid and passphrase. Outputs the decrypted data as a json string.
        """
        if not keyid:
            keyid = self.keyfp
        if not passphrase:
            try:
                passphrase = self.pwd
            except AttributeError:
                if settings.VERBOSE:
                    print "trying to decrypt, but no passphrase -- exiting."
                    traceback.print_stack(file=sys.stdout)
                return ""
        data = getattr(self, container+"_data", "")
        if settings.VERBOSE:
            print "########"
            print "Decrypting data from %s's container %s with key %s " \
                "passphrase %s*" % (self.uid, container, keyid, passphrase[0:3])
            print "DATA:\n%s" % data
        decrypted_data = msg_decrypt (str(data), keyid, passphrase)
        if settings.VERBOSE:
            print "Decrypted data:\n %s\n\n\n\n" % decrypted_data.data
        return decrypted_data.data

    def gen_key(self, passphrase=""):
        """
        Private method for generating the private/public key pair
        for the user.
        """
        if not self.keyfp:
            if not passphrase:
                passphrase = self.pwd

            fingerprint = gen_keypair(
                self.uid, passphrase,
                self.get_anonymous_email()
            )
            try:
                # Check whether we made a duplicate key (unlikely)
                Profile.objects.get(keyfp = fingerprint)
                self.gen_key(passphrase)
            except ObjectDoesNotExist:
                self.keyfp = fingerprint
                if settings.VERBOSE:
                    print "Generated key %s\n#######\n\n" % self.keyfp
                    print "passphrase %s* " % passphrase[0:3]
        else:
            print "Trying to generate key pair for Profile %s. But it " \
                "already has key with id %s!" % (self.uid, str(self.keyfp))
            traceback.print_stack(file=sys.stdout)

    ########################
    ### instance methods ###
    ########################

    def __unicode__(self):
        return self.uid

    def init(self, user, email, longitude, latitude,
             languages, about_me, contact_info,
             display_language="en", allow_email=False,
             passphrase=None):
        """
        initializes and saves a Profile instance, encrypting the data to
        their respective containers. Requests 12 friends from the graph.
        """

        # Unencrypted Profile Meta Data
        self.user = user
        self.uid = char_id(user.id)
        self.allow_email = bool(allow_email)
        self.pwd = passphrase
        self.drop_comments = None

        if settings.VERBOSE:
            print "[!] Generating key for new user %s\n" % self.uid

        self.gen_key(passphrase = passphrase)

        # let's build the encrypted blobs and store them into the database
        # Drop counters
        try:
            dcnt = DropCounter.objects.create (uid = self.uid)
        except IntegrityError as exc:
            print "Profile.init: Couldn't initiate DropCounter with " \
                "id=%s. It already exists!" % self.uid
            print exc
        else:
            dcnt.init()

        # private data
        self.display_language = display_language
        self.local_friend_str = "," + settings.NUM_LOCAL_FRIENDS * "0,"
        self.remote_friend_str = "," + settings.NUM_REMOTE_FRIENDS * "0,"
        self.global_token_str = "," + settings.NUM_REMOTE_FRIENDS * "0,"
        self.former_friend_str = ""
        self.keep_friend_str = ""
        self.email = email
        self.set_langs_spoken(languages)

        # Friends can see this data
        self.longitude = longitude
        self.latitude = latitude
        self.about_me = about_me
        self.contact_info = contact_info
        self.unique_langs = self.get_unique_languages()

        self.refresh_dropped_signal()
        if self.allow_email:
            self.notify_mailmanager(old_email="", new_email=self.email)
        self.send_friend_request()

        self.save()

    def array_to_db_csv(self, array_attr, array):
        """convert array to csv"""
        csv = ",".join([str(item) for item in array])
        if csv:
            csv = csv.join([",",","])
        setattr(self, array_attr, csv)

    def db_csv_to_array(self, str_attr):
        """
        convert a value stored as a csv in the db to an array
        """
        attr = getattr(self, str_attr, "")
        if attr:
            return attr.strip(',').split(',')
        else:
            return []

    def append_to_csv(self, csv, appendix):
        """
        Append the appendix (needs to implement __str__) to the csv string of
        this instance.
        """
        tmp_list = self.db_csv_to_array(csv)
        tmp_list.append(appendix)
        self.array_to_db_csv(csv, tmp_list)

    def remove_from_csv(self, csv, removix):
        """
        Remove all entries that are equal to removix from the csv string of
        this instance.
        """
        tmp_list = self.db_csv_to_array(csv)
        while removix in tmp_list:
            tmp_list.remove(removix)
        self.array_to_db_csv(csv, tmp_list)

    def replace_in_csv(self, csv, old, new):
        """
        Replace all occurances of old by new in the csv string of this instance.
        """
        tmp_list = self.db_csv_to_array(csv)
        while old in tmp_list:
            tmp_list[tmp_list.index(old)] = new
        self.array_to_db_csv(csv, tmp_list)

    def find_slot_for_new_remotefriend(self, lang):
        """find slot for remote friend"""
        old_remotes = self.db_csv_to_array('remote_friend_str')
        langs = self.db_csv_to_array('lang_str')
        if len(langs) == 0:
            langs = ["en"] * getattr(self, "NUM_REMOTE_FRIENDS", 6)
        for num, fid in enumerate(old_remotes):
            try:
                relevant_lang = langs[num]
            except IndexError:
                relevant_lang = langs[0]
            if fid == "0" and lang == relevant_lang:
                return num
        return None

    def find_slot_for_new_localfriend(self):
        """find slot for local friend"""
        old_locals = self.db_csv_to_array('local_friend_str')
        for num, fid in enumerate(old_locals):
            if fid == "0":
                return num
        return None

    def add_friends_from_graph(self):
        """
        Add newly assigned local and global friends from the graph algorithm.
        Then, encrypt the profile so that the new friends can read it.
        """
        for new_friend, lang in zip(
            self.friend_id_list("new_remote"),
            self.db_csv_to_array("new_global_token_str")
        ):
            if not new_friend:
                continue
            if key_fingerprint(new_friend) is None:
                if settings.VERBOSE:
                    print "Can't add friend %s: " \
                        "Can't find his key fingerprint" % new_friend
            else:
                # For every new remote friend: Do i have a free slot with his
                # language? If not: logistical-drop
                free_slot = self.find_slot_for_new_remotefriend(lang)
                if free_slot is None:
                    if settings.VERBOSE:
                        print "Can't add friend %s: Doesn't have a matching " \
                            "token slot for language %s " % (new_friend, lang)
                        
                    # Tell a friend that he has been dropped, but do not
                    # treat it as a graph-relevant drop. This means that
                    # only the DROPPED-container is encrypted to the
                    # friend's key. No DropCounters are increased and we
                    # are not saving the friend in the former_friend_str
                    # so that it is possible to get assigned to him again
                    # in a future graph round.
                    self.append_to_csv(
                        "extra_dropped_msg_friend_str", new_friend
                    )
                else:
                    if settings.VERBOSE:
                        print "########"
                        print "[-] Adding friend %s." % new_friend

                    # Add his key so that he can read our public info
                    self.append_to_csv(
                        "friend_public_keys", key_fingerprint(new_friend)
                    )

                    # Insert him into remote_friend_str
                    tmp_remotes = self.db_csv_to_array("remote_friend_str")
                    tmp_remotes[free_slot] = new_friend
                    self.array_to_db_csv("remote_friend_str", tmp_remotes)

                    # Insert the corresponding language into global_token_str
                    tmp_globals = self.db_csv_to_array("global_token_str")
                    tmp_globals[free_slot] = lang
                    self.array_to_db_csv("global_token_str", tmp_globals)

                    # Remove him from the dropped-msg-recipients
                    self.remove_from_csv(
                        "extra_dropped_msg_friend_str", new_friend
                    )

        for new_friend in self.friend_id_list("new_local"):
            if not new_friend:
                continue
            if key_fingerprint(new_friend) is None:
                if settings.VERBOSE:
                    print "Can't add friend %s: Can't find his key " \
                        "fingerprint" % new_friend
            else:
                # Simply add the new local friends until there are no more
                # free slots in local_friend_str
                free_slot = self.find_slot_for_new_localfriend()
                if free_slot is None:
                    if settings.VERBOSE:
                        print "Can't add friend %s: Local friend slots " \
                            "are filled." % (new_friend)
                            
                    # Tell a friend that he has been dropped, but do not treat
                    # it as a graph-relevant drop. This means that only the
                    # DROPPED-container is encrypted to the friend's key. No
                    # DropCounters are increased and we are not saving the
                    # friend in the former_friend_str so that it is possible
                    # to get assigned to him again in a future graph round.
                    self.append_to_csv(
                        "extra_dropped_msg_friend_str", new_friend
                    )
                else:
                    if settings.VERBOSE:
                        print "########"
                        print "[-] Adding friend %s." % new_friend

                    # Add his key so that he can read our public info
                    self.append_to_csv(
                        "friend_public_keys", key_fingerprint(new_friend)
                    )

                    # Insert him into local_friend_str
                    tmp_locals = self.db_csv_to_array("local_friend_str")
                    tmp_locals[free_slot] = new_friend
                    self.array_to_db_csv("local_friend_str", tmp_locals)

                    # Remove him from the dropped-msg-recipients
                    self.remove_from_csv(
                        "extra_dropped_msg_friend_str", new_friend
                    )

        self.refresh_dropped_signal()

    def send_friend_request(self):
        """
        If the user has less friends than the maximum allowed, give the graph
        an update of what the user needs.
        """
        total = settings.NUM_LOCAL_FRIENDS + settings.NUM_REMOTE_FRIENDS
        avail = len(self.friend_list())
        if avail < total:
            message = {
                "msgType" : "drop",
                "accnt_id" : self.uid,
                "keyfp" : self.keyfp,
                "latitude" : self.latitude,
                "longitude" : self.longitude,
                "languages" : self.get_unique_languages(),
                "num_local_needed" : \
                    int(settings.NUM_LOCAL_FRIENDS) - \
                    len(self.friend_list(friend_type = "local")),
                "langs_global_needed_str" : self.get_global_langs_needed(),
                "known_contacts_str" : self.known_contacts_list(),
            }
            Graph.objects.create(**message) # pylint: disable=W0142

    def send_delete_notification(self):
        """
        When a user deletes himself, all his friends get green dropped
        when this happens, graph messages asking for new friends are generated
        this notifies the graph that the user deleted himself and thus said
        msgs are invalid
        """
        message = {
            "msgType" : "delete",
            "accnt_id" : self.uid
        }
        Graph.objects.create(**message) # pylint: disable=W0142

    def notify_mailmanager(self, new_email, old_email):
        """send notification to mail manager"""
        message = {
            "email": {
                "old_email": old_email,
                "new_email": new_email,
            },
            "languages": self.get_unique_languages(),
            "pref_lang": self.display_language,
            "timezone": self.get_timezone(),
        }
        if settings.VERBOSE:
            print message
        Mail.objects.create(**message) # pylint: disable=W0142

    def refresh_dropped_signal(self):
        """
        Encrypt "DROPPED" to own and all dropped friends' keys.
        The purpose of this is that when a user logs in he can distinguish
        between friends who have not decrypted their profile for him 
        and friends who have dropped him.
        """
        dropped_keys = [self.keyfp]
        for fid in self.friend_id_list("former"):
            fprint = key_fingerprint(fid)
            if fprint is not None:
                dropped_keys.append(fprint)

        for fid in self.friend_id_list("extra_dropped_msg"):
            fprint = key_fingerprint(fid)
            if fprint is not None:
                dropped_keys.append(fprint)

        if settings.VERBOSE:
            print "########"
            print "Encrypting 'DROPPED' message to keys %s. data:\n %s" \
                % (str(dropped_keys), settings.DROPPED_CONTENT)

        data = msg_encrypt(settings.DROPPED_CONTENT, dropped_keys, hidden=True)
        self.dropped_signal = data
        if settings.VERBOSE:
            print "Encrypted data:\n %s\n\n\n\n" % self.dropped_signal

    def get_timezone(self):
        """get timezone data"""
        try:
            lon = float(self.longitude)
        except ValueError:
            return "unknown"
        return int(lon / 15)

    def get_global_token(self, i):
        """
        returns the language which matched the user with
        his i-th global friend
        """
        try:
            return self.db_csv_to_array("global_token_str")[i]
        except IndexError:
            return ""

    def get_anonymous_email(self):
        """get anonymous email address"""
        return self.uid + settings.PRJ_MAIL

    def human_public_name(self, frmt=settings.ACCNT_FORMAT):
        """
        Mostly obsolete. The human public name is now just the ID.
        Generate a human readable version of the "public name".
        @frmt: the format for the human readable format. Array containing the
        number of chars before each space.
        """
        number = self.uid
        human_number = number[0:frmt[0]]

        # The following code does not do anything when using the ID as the
        # public name.
        pos = frmt[0]
        for idx in range(0, len(frmt)-1):
            human_number += ' ' + number[pos:pos+frmt[idx+1]]
            pos += frmt[idx+1]
        human_number += ' ' + number[pos:]
        return human_number

    def friend_id_list(self, friend_type = None):
        """
        Return the ids of the user's friendType friends in a list. 
        Call without an argument to get all current friends' fids.
        """
        if friend_type is None:
            return self.friend_id_list("local") + \
                   self.friend_id_list("remote")

        fids = self.db_csv_to_array('%s_friend_str' % str(friend_type))
        try:
            while True:
                fids.remove("0")
        except ValueError:
            try:
                while True:
                    fids.remove("")
            except ValueError:
                return fids

    def friend_list(self, session = None, friend_type = None):
        """
        Return the user's friendType friends' profile objects in a list.
        """
        friend_ids = self.friend_id_list(friend_type = friend_type)
        if session is not None:
            friends = []
            for friend_id in friend_ids:
                try:
                    friends.append(session[friend_id])
                except KeyError:
                    if settings.VERBOSE:
                        print "friendId %s not found in session" % friend_id
        else:
            try:
                profiles = Profile.objects.filter(uid__in=friend_ids)
            except ValueError:
                profiles = []
            friends = []
            for prf in profiles:
                friends.append (Friend(prf))

        return friends

    def known_contacts_list(self):
        """
        Return an unordered list of past and present friends' ids.
        """
        known_fids = self.friend_id_list() + \
                     self.friend_id_list("former")

        # So that nobody can tell which friends are the most recent ones
        random.shuffle( known_fids)

        self.array_to_db_csv("known_contacts_tmp", known_fids)
        return known_fids

    def get_global_langs_needed(self):
        """
        Returns an unordered list with repetitions of the languages that the 
        user's new global friends should speak
        """
        tokens = self.db_csv_to_array('global_token_str')
        langs = self.db_csv_to_array('lang_str')
        need = []
        # Some people may have lost their lang_str for some reason.
        # Corrupted data etc.
        if len(langs) == 0:
            langs = ["en"] * getattr(self, "NUM_REMOTE_FRIENDS", 6)
            for i, lang in enumerate(tokens):
                if lang == "0":
                    try:
                        need.append(langs[i])
                    except IndexError:
                        need.append(langs[0])
        random.shuffle(need)
        self.array_to_db_csv("global_langs_tmp", need)
        return need

    def get_langs_spoken(self):
        """get list of spoken languages"""
        return self.db_csv_to_array('lang_str')

    def get_unique_languages(self):
        """
        Returns a shuffled list of languages that the user speaks, without
        repetition
        """
        if hasattr(self, 'unique_langs'):
            unique_langs = self.unique_langs
        else:
            unique_langs = list(set(self.db_csv_to_array('lang_str')))
        random.shuffle(unique_langs)
        return unique_langs

    def local_or_remote(self, friend_id):
        """detect if a friend is local or remote"""
        if friend_id in self.friend_id_list("local"):
            return "local"
        elif friend_id in self.friend_id_list("remote"):
            return "remote"
        else:
            return None

    def set_langs_spoken(self, langs_spoken):
        """
        set the languages a user speaks:
        -ordered list in lang_str
        -unordered list without repetitions in unique_langs
        """
        self.array_to_db_csv('lang_str', langs_spoken)
        self.unique_langs = list(set(langs_spoken))

    def mark_dropped_token(self, friend_fid):
        """delete language token for drop"""
        pos = self.friend_id_list("remote").index(friend_fid)
        tokens = self.db_csv_to_array('global_token_str')
        try:
            tokens[pos] = "0"
        except IndexError:
            if pos < settings.NUM_REMOTE_FRIENDS:
                # Fill the missing tokens with zeroes
                tokens += (settings.NUM_REMOTE_FRIENDS - len(tokens)) * ["0"]
        self.array_to_db_csv('global_token_str', tokens)

    def process_drop_by(self, friend_fid):
        """
        Get dropped by a friend.
        Remove the friend_fid from all friend lists and his key from the
            friend_public_keys.
        Do not increase any counters or add the friend to former_friend_str,
            because this is only done by the active dropper.
        """
        # Verify that the user is a friend.
        if not friend_fid in self.friend_id_list():
            return False

        # Update own profile data.
        if friend_fid in self.friend_id_list("remote"):
            # Set corresponding global token to Zero
            self.mark_dropped_token(friend_fid)

        dropped_key = key_fingerprint(friend_fid)
        self.remove_from_csv("friend_public_keys", dropped_key)
        self.replace_in_csv("local_friend_str", friend_fid, "0")
        self.replace_in_csv("remote_friend_str", friend_fid, "0")
        return True

    def process_deleted_friend(self, friend_fid):
        """
        A friend deleted himself. This has exactly the same effect as a
        drop by that friend.
        """
        self.process_drop_by(friend_fid)

    def defriend(self, friend_fid, reason, comment):
        """
        Drop a friend.
        Before:
          lang_str="en,fr"
          global_token_str="en,fr"
          global_friend_str="id1,id2"
        After dropping id2:
          lang_str="en,fr"
          global_token_str="en,0"
          global_friend_str="id1,0"
          Encrypted "DROPPED" to id2's key.
          Re-encrypted public data to id1 and own key only.
          Increased one of my dropper-Counters.
          Increased one of id2's dropped-Counters.
          Requested a french friend.
        """
        # Verify that the dropped user is a friend.
        if not friend_fid in self.friend_id_list():
            return False
        # Update own profile data.
        if friend_fid in self.friend_id_list("remote"):
            # Set corresponding global token to Zero
            self.mark_dropped_token(friend_fid)

        dropped_key = key_fingerprint(friend_fid)
        self.remove_from_csv("friend_public_keys", dropped_key)

        self.replace_in_csv("local_friend_str", friend_fid, "0")
        self.replace_in_csv("remote_friend_str", friend_fid, "0")

        self.append_to_csv("former_friend_str", friend_fid)

        if len(comment) > 500:
            comment = comment[:500]
        try:
            self.drop_comments.append((friend_fid, comment))
        except AttributeError:
            self.drop_comments = [(friend_fid, comment)]

        # Encrypt dropped signal with newly dropped key as well.
        self.refresh_dropped_signal()

        # Increase homomorphic counters
        try:
            my_dc = DropCounter.objects.get(id=self.uid)
        except ObjectDoesNotExist:
            my_dc = DropCounter.objects.create(id=self.uid)
            my_dc.init()
        try:
            friend_dc = DropCounter.objects.get(id=friend_fid)
        except ObjectDoesNotExist:
            friend_dc = DropCounter.objects.create(id=friend_fid)
            friend_dc.init()

        my_dc.increase(who="subject", reason=reason)
        friend_dc.increase(who="object", reason=reason)

        DropCounter.obfuscate()

        self.send_friend_request()

        # Save changes to the DB
        my_dc.save()
        friend_dc.save()
        # This re-encrypts the public_info container with the correct keys.
        self.save()
        return True

    def get_user(self):
        """get user instance"""
        return User.objects.get(uid=self.uid)

def generate_unused_dbkey():
    """
    Returns a id matching /[A-Z]{2}[1-9][0-9]{3}/
    for example WL2007
    """
    # Two upper case letters
    new_key = "".join(random.choice(settings.CHARS) for x in range(2))
    # Four digit number, not starting with zero
    new_key += str(random.choice(settings.NUMBERS[1:10]))
    new_key += "".join(random.choice(settings.NUMBERS) for x in range(3))
    try:
        Profile.objects.get(uid = new_key)
        # If we get to here, the key already exists. generate another one..
        return generate_unused_dbkey()
    except ObjectDoesNotExist:
        return new_key

def key_fingerprint(uid):
    """get fingerprint of key"""
    if not uid:
        return None
    try:
        profile = Profile.objects.get(uid = uid)
    except ObjectDoesNotExist as exc:
        print "Can't find user %s. Error: %s" % (uid, exc)
        traceback.print_stack(file=sys.stdout)
        return None
    try:
        return profile.keyfp
    except AttributeError as exc:
        print "Can't find the key fingerprint of user %s. Error: %s" \
            % (uid, exc)
        traceback.print_stack(file=sys.stdout)
        return None
