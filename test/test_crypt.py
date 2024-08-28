from __future__ import print_function

import os
from mock import patch, MagicMock
from tempfile import mkstemp

from base import BaseTest
from utils import mock_stdout
from base64 import standard_b64encode, standard_b64decode

from lib import crypt
from lib.crypt import Crypter, CrypterKeyException

from Crypto.Util.randpool import RandomPool


class MockGID(object):
    def __init__(self):
        self.gr_gid = 1337


class TestCrypt(BaseTest):

    def setUp(self):
        super(TestCrypt, self).setUp()
        crypt.getgrnam = lambda x: MockGID()
        _, self.keylocation = mkstemp()
        _, self.passwordloc = mkstemp()
        _, self.configlocat = mkstemp()

        with open(self.configlocat, 'w') as f:
            configuration = '''[keyset]
path: %s
[password]
path: %s''' % (self.keylocation, self.passwordloc)
            f.write(configuration)
        crypt.SECURITY_CONF_FILE_PATH = self.configlocat

    def tearDown(self):
        for filename in (self.keylocation, self.passwordloc, self.configlocat):
            try:
                os.chmod(filename, 0o600)
            except Exception as err:
                print("Error: %s" % err)

            try:
                os.remove(filename)
            except Exception as err:
                print("Error: %s" % err)

    @mock_stdout
    def test_start_from_cli_help(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        args = ['-h']
        err = None
        try:
            crypter.run(args)
        except (Exception, SystemExit) as err:
            pass
        self.assertTrue(isinstance(err, SystemExit))

        out = self._mock_stdout.getvalue().strip()
        self.assertEqual(0, err.code)
        self.assertIn('show this help message and exit', out)

    def test_start_from_cli_set_get_password(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        crypter.set_key('')
        args = type('', (object,), {'service': 'criticalbackup',
                                    'user': 'criticalbackup', 'pass_prompt': True, 'password': False})

        mock_getpass = MagicMock(return_value="test_password")
        with patch("getpass.getpass", mock_getpass):
            crypter.set_password(args)
        self.assertEqual('test_password', crypter.get_password('criticalbackup','criticalbackup'))

    @mock_stdout
    def test_start_from_cli_get_password(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        crypter.set_key('')
        args = type('', (object,), {'service': 'criticalbackup',
                                    'user': 'criticalbackup', 'pass_prompt': True, 'password': False})
        mock_getpass = MagicMock(return_value="test_password")
        with patch("getpass.getpass", mock_getpass):
            crypter.set_password(args)
        args = type('', (object,), {'user': 'criticalbackup',
                                    'service': 'criticalbackup'})
        crypter.get_password_cli(args)
        out = self._mock_stdout.getvalue().strip()
        self.assertEqual('test_password', out)


    @patch.object(Crypter, 'read_key')
    def test_encrypt_password(self, read_key):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        key = Crypter.generate_key()
        read_key.return_value = key
        decpassword = 'test'
        encrypted = crypter._encrypt(decpassword)
        self.assertEqual(decpassword, Crypter.decrypt(key, encrypted))

    def test_generate_key(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        key = Crypter.generate_key()
        self.assertEquals(len(key), 32)

    def test_generate_unique_key(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        keys = []
        for _ in range(10):
            keys.append(Crypter.generate_key())
        self.assertEqual(len(keys), len(set(keys)))

    def test_write_key(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc

        key = Crypter.generate_key()
        Crypter.write_key(self.keylocation, key)
        with open(self.keylocation, 'r') as f:
            data = f.readlines()
            self.assertEqual(standard_b64encode(str(key)),
                             data[0].rstrip())

    def test_read_key(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc

        key = Crypter.generate_key()
        Crypter.write_key(self.keylocation, key)

        key = Crypter.read_key(self.keylocation)
        with open(self.keylocation, 'r') as f:
            data = f.readlines()
            self.assertEqual(standard_b64encode(str(key)),
                             data[0].rstrip())

    def test_read_key_exception(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc

        key = RandomPool().get_bytes(31)
        Crypter.write_key(self.keylocation, key)

        with self.assertRaises(CrypterKeyException):
            Crypter.read_key(self.keylocation)

    def test_check_key_does_exist(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        key = Crypter.generate_key()
        Crypter.write_key(self.keylocation, key)

        self.assertTrue(os.path.exists(self.keylocation))

    def test_generate_key_upgrade(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        crypter.set_key('')

        with open(self.keylocation, 'r') as f:
            data = f.readlines()
            origkey = standard_b64decode(str(data))

        crypter.set_key('')
        with open(self.keylocation, 'r') as f:
            data = f.readlines()
            otherkey = standard_b64decode(str(data))

        self.assertEqual(origkey, otherkey)

    @patch.object(Crypter, 'read_key')
    def test_invalid_key_encrypt(self, mock_readkey):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        mock_readkey.return_value = ''
        self.assertRaises(ValueError, crypter._encrypt, '')

    @patch.object(Crypter, 'read_key')
    def test_invalid_key_decrypt(self, mock_readkey):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        key = Crypter.generate_key()

        mock_readkey.return_value = key
        data = crypter._encrypt("NR-NSA")
        self.assertRaises(ValueError, Crypter.decrypt, '', data)

    def test_invalid_data_decrypt(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        key = Crypter.generate_key()

        self.assertRaises(TypeError, Crypter.decrypt, key, "testDecrypt")

    def test_decrypt_empty_data(self):
        crypter = Crypter()
        crypter.password_file_path = self.passwordloc
        key = Crypter.generate_key()

        result = Crypter.decrypt(key, "")

        self.assertEquals(result, "")
