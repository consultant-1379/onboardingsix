#!/usr/bin/env python
####################################################################
# COPYRIGHT Ericsson AB 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
####################################################################
from __future__ import print_function
import pickle
import os
import os.path
import requests
import urllib3
import common.constants as constants

from common.log import NRNSALogger
from common.nrnsa_exception import NRNSAException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SsoManager(object):

    def __init__(self):
        self.log = NRNSALogger()
        self.src_file_path = os.path.dirname(os.path.abspath(__file__))

    def create_cookie(self, url, username, password):
        endpoint = constants.LOGIN_ENDPOINT
        session = requests.session()
        credentials = {"IDToken1": username, "IDToken2": password}

        login_response = session.post(url + endpoint, data=credentials,
                                      verify=False, allow_redirects=False)
        if login_response.status_code == 302:
            self._store_cookie_to_file(login_response.cookies)
            self._store_session_token(login_response.cookies, username)
            return True
        elif login_response.status_code == 401:
            print('Authorization failed. Please check your credentials')
            return False
        else:
            custom_msg = 'Error occurred while getting the cookie'
            raise NRNSAException(custom_msg)

    def _store_cookie_to_file(self, cookie):
        filename = os.path.join(self.src_file_path, 'cookie.txt')
        with open(filename, 'w') as open_file:
            pickle.dump(requests.utils.dict_from_cookiejar(cookie), open_file)
            open_file.close()

    @staticmethod
    def _store_session_token(cookie, username):
        filename = os.path.join(
            os.path.expanduser('~' + username), '.enm_login')
        with open(filename, 'w') as open_file:
            open_file.write(requests.utils.dict_from_cookiejar(cookie)
                            ['iPlanetDirectoryPro'])
            open_file.close()

    def get_cookie(self):
        filename = os.path.join(self.src_file_path, 'cookie.txt')
        cookie = {}

        with open(filename) as open_file:
            cookie = requests.utils.cookiejar_from_dict(pickle.load(open_file))
            open_file.close()

        return cookie
