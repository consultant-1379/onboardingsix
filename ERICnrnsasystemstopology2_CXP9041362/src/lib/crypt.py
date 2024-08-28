#!/usr/bin/env python
####################################################################
# COPYRIGHT Ericsson AB 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
####################################################################
from __future__ import print_function
import argparse
import base64
from base64 import standard_b64decode, standard_b64encode
import ConfigParser
import getpass
import os
from os import chmod, chown, getuid, path
import sys
from collections import OrderedDict
from grp import getgrnam
from pwd import getpwnam

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

SECURITY_CONF_FILE_PATH = "/etc/nr-nsa_security.conf"
INITIALIZATION_VECTOR = os.urandom(16)


def pad(data, padding=16):
    pad_length = (padding - (len(data) - 1) % padding) - 1
    return data + chr(3) * pad_length


class CrypterKeyException(Exception):
    pass


class Crypter(object):

    def __init__(self):
        parser = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
        parser.read(SECURITY_CONF_FILE_PATH)
        self.keyset = parser.get("keyset", "path")
        self.password_file_path = os.path.join(parser.get("password", "path"),
                                               getpass.getuser())
        self.args = None

    @staticmethod
    def read_key(location):
        """Read a private RSA key from the location

        :param location: File location where is key is saved.
        :type location: str
        :returns: RSA key from file.
        :rtype: str
        :raises IOError: If IO is interrupted while reading file."""

        with open(location, 'r') as open_file:
            key = standard_b64decode(open_file.readlines()[0])
            if not key or len(key) != 32:
                raise CrypterKeyException
        return key

    def _encrypt(self, data=''):
        """Encrypt data and then base-64 encode it
        @param data: data to encrypt
        @type data: string"""
        key = Crypter.read_key(self.keyset)
        cipher = Cipher(algorithms.AES(key), modes.CFB(INITIALIZATION_VECTOR),
                        backend=default_backend())
        encryptor = cipher.encryptor()
        crypted = encryptor.update(data) + encryptor.finalize()
        return crypted

    # decrypt with cryptography

    def _decrypt(self, encrypted):
        key = Crypter.read_key(self.keyset)
        return Crypter.decrypt(key, encrypted)

    @staticmethod
    def decrypt(key, data=''):
        """Decrypt data and then base-64 decode it

        :param key: RSA key to decrypt with
        :type key: str
        :param data: data to decrypt
        :type data: str
        :raises TypeError: If key or data is not valid string"""

        if not data:
            return ''  # Should raise TypeError: Not encrypted value
        # Create encryptor from AES module
        cipher = Cipher(algorithms.AES(key), modes.CFB(INITIALIZATION_VECTOR),
                        backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(data) + decryptor.finalize()
        return decrypted

    @staticmethod
    def generate_key():
        """Generate the random key"""
        key = os.urandom(32)
        return key

    @staticmethod
    def write_key(location, key):
        """Write the key to the key file, if the key is not
           present the new key is generated

           :param location: location of the key file
           :param key: the generated key """
        with open(location, 'w') as open_file:
            open_file.write(standard_b64encode(key))
        try:
            if getuid() == 0:
                chmod(location, 0o440)
                chown(location, getpwnam("root").pw_uid,
                      getgrnam("scripting_users").gr_gid)
        except OSError as exc:
            print("Permission denied. %s" % exc)
        except KeyError:
            print("Group scripting_users does not exist.")

    def set_key(self, dummy):
        """ Generate a new private key to be used by cricitalbackup
        password storage
        """
        del dummy  # unused
        messages = []
        try:
            key = Crypter.read_key(self.keyset)

        except (IOError, IndexError, CrypterKeyException) as exc:
            try:
                key = Crypter.generate_key()
                Crypter.write_key(self.keyset, key)

            except IOError as exc:
                messages.append("%s" % exc)

        finally:
            Crypter.send_messages_to_stderr(messages)
            if messages:
                sys.exit(1)

    @staticmethod
    def send_messages_to_stderr(msg_list):
        for message in msg_list:
            sys.stderr.write("%s\n" % message)

    def get_password(self, service, user):
        """Return a password."""
        config_parser = ConfigParser.SafeConfigParser()
        config_parser.optionxform = str
        config_parser.read(self.password_file_path)

        b64_username = base64.standard_b64encode(user).replace('=', '')
        try:
            enc_password = config_parser.get(service, b64_username)
        except ConfigParser.NoOptionError:
            enc_password = config_parser.get(service, user)

        password = self._decrypt(enc_password)
        return password

    def get_password_cli(self, args):
        user = args.user
        service = args.service
        password = self.get_password(service, user)
        sys.stdout.write(password)
        sys.stdout.flush()

    def set_password(self, args):
        messages = []
        try:
            self._check_password(args, messages)
        except (IOError, IndexError, TypeError) as exc:
            messages.append("Error in writing to %s" % self.password_file_path)
            messages.append("%s" % exc)
        except OSError as exc:
            messages.append("%s" % exc)

        finally:
            Crypter.send_messages_to_stderr(messages)
            if messages:
                sys.exit(1)

    def _check_password(self, args, messages):
        err = False
        service = args.service
        user = args.user
        if args.password and args.pass_prompt:
            messages.append("unrecognized arguments: " +
                            "%s. password not needed " +
                            "with --prompt" % self.args.password)
            err = True

        if args.pass_prompt and not err:
            password = Crypter._get_password()
        else:
            password = args.password

        args_dict = dict(zip(("service", "user", "password"),
                             (service, user, password)))

        for key, value in args_dict.items():
            if not value:
                messages.append("Error: %s must not be empty" % key)
                err = True

        if not err:
            self._write_password(args, password)

    @staticmethod
    def _get_password():
        pw1 = ""
        pw2 = "b"
        flag_first = True
        while pw1 != pw2:
            if flag_first:
                flag_first = False
            else:
                print("passwords don't match")
                pw1 = ""
            while not pw1:
                pw1 = getpass.getpass()
                if not pw1:
                    print("Error: password must not be empty")
            pw2 = getpass.getpass("Confirm password:")
        return pw1

    def _write_password(self, args, password):
        service = args.service
        user = args.user
        b64_user = standard_b64encode(user).replace('=', '')
        config_parser = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
        config_parser.optionxform = str
        config_parser.read(self.password_file_path)
        if not config_parser.has_section(service):
            config_parser.add_section(service)
        enc_password = self._encrypt(password)

        if config_parser.has_option(service, user):
            config_parser.remove_option(service, user)

        config_parser.set(service, b64_user, enc_password)
        with open(self.password_file_path, 'wb') as password_file:
            config_parser.write(password_file)

        chmod(self.password_file_path, 0o600)

        if getuid() == 0 and path.exists(self.password_file_path):
            chmod(self.password_file_path, 0o664)
            # user root, group litp-admin
            chown(self.password_file_path, getpwnam("root").pw_uid,
                  getgrnam("scripting_users").gr_gid)

    def delete_password(self, args):
        err = False
        service = args.service
        user = args.user
        messages = []
        args_dict = dict(zip(("service", "user"),
                             (service, user)))

        for key, value in args_dict.items():
            if not value:
                messages.append("Error: %s must not be empty" % key)
                err = True

        if err:
            Crypter.send_messages_to_stderr(messages)
            sys.exit(1)

        config_parser = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
        config_parser.optionxform = str
        config_parser.read(self.password_file_path)
        b64_user = standard_b64encode(user).replace('=', '')

        if not config_parser.has_section(service):
            messages.append("Given service does not exist")

        elif not config_parser.has_option(service, b64_user) \
                and not config_parser.has_option(service, user):
            messages.append("Given username does not exist")

        if messages:
            Crypter.send_messages_to_stderr(messages)
            sys.exit(1)
        elif len(config_parser.options(service)) == 1:
            config_parser.remove_section(service)
        elif config_parser.has_option(service, b64_user):
            config_parser.remove_option(service, b64_user)
        else:
            config_parser.remove_option(service, user)

        with open(self.password_file_path, 'wb') as password_file:
            config_parser.write(password_file)

    def run(self, args):
        parser = argparse.ArgumentParser(
            description="nr-nsa command line interface to manage "
                        "passwords required by nr-nsa service."
        )
        subparsers = parser.add_subparsers(
            title='actions',
            description=(
                "Actions to execute on stored passwords.\n"
                "For more detailed information on each action enter "
                "the command 'crypt <action> -h'"
            ),
            help="",
            metavar="")

        parser_set = subparsers.add_parser(
            'set',
            help='Add a password to nr-nsa password storage',
            description="set - Add a password to nr-nsa"
                        " password storage")
        parser_set.set_defaults(func=self.set_password)

        parser_set.add_argument('service',
                                help=('keyword uniquely identifying the '
                                      'service and host'))

        parser_set.add_argument('user', help=('user'))

        parser_set.add_argument('password', nargs='?',
                                help=('password as an argument ' +
                                      'can\'t be used with prompt'))

        parser_set.add_argument('--prompt', dest="pass_prompt",
                                action="store_true",
                                help=('prompt for password'))

        parser_delete = subparsers.add_parser(
            'delete',
            help='Remove a password from nr-nsa password storage',
            description=("delete - Remove a password from nr-nsa"
                         " password storage"))
        parser_delete.set_defaults(func=self.delete_password)
        parser_delete.add_argument('service',
                                   help=('keyword uniquely identifying the '
                                         'service and host'))

        parser_delete.add_argument('user', help=('user'))

        parser_setkey = subparsers.add_parser(
            'setkey',
            help='Set the private key for nr-nsa password storage',
            description=("setkey - Set the private key for nr-nsa"
                         " password storage"))
        parser_setkey.set_defaults(func=self.set_key)

        parser_getpassword = subparsers.add_parser(
            'getpassword',
            help='Get the private  key for nr-nsa password storage',
            description=("getpassword - Get the private key for nr-nsa"
                         " password storage")
        )
        parser_getpassword.set_defaults(func=self.get_password_cli)
        parser_getpassword.add_argument('service',
                                        help=('keyword uniquely identifying'
                                              ' the service and host'))
        parser_getpassword.add_argument('user', help=('user'))

        self.args = parser.parse_args(args)

        return self.args.func(self.args)


if __name__ == "__main__":
    CLI = Crypter()
    sys.exit(CLI.run(sys.argv[1:]))
