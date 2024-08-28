#!/usr/bin/env python
####################################################################
# COPYRIGHT Ericsson AB 2019
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
####################################################################

import json
import requests

from common.sso_manager import SsoManager
from common.network_utils import NetworkUtils
from common.nrnsa_exception import NRNSAException, generate_error_message


class RestService(object):
    """
        A Simple implementation of common TCS services that all topologies
        can make use of
    """

    def __init__(self):
        self.sso = SsoManager()
        self.hostname = NetworkUtils().get_enm_hostname()
        self.url = "https://" + str(self.hostname)
        self.cookie = self.sso.get_cookie()
        self.headers = {
            "content-type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "X-Tor-Application": "networkexplorer"
        }

    def post(self, endpoint, data):
        try:
            return requests.post(
                self.url + endpoint,
                data=json.dumps(data),
                cookies=self.cookie,
                headers=self.headers,
                verify=False)
        except requests.exceptions.RequestException, exc:
            RestService._handle_error(exc, endpoint)

    def put(self, endpoint, data):
        """Update an existing collection

        :param endpoint: the update endpoint needed
        :param data: any body data to consider
        :return: response code
        """
        try:
            return requests.put(
                self.url + endpoint,
                data=json.dumps(data),
                cookies=self.cookie,
                headers=self.headers,
                verify=False)
        except requests.exceptions.RequestException, exc:
            RestService._handle_error(exc, endpoint)

    def delete(self, endpoint):
        """Delete an existing collection

        :param endpoint: the necessary delete endpoint
        :return:
        """
        try:
            return requests.delete(
                self.url + endpoint,
                headers=self.headers,
                cookies=self.cookie,
                verify=False)
        except requests.exceptions.RequestException, exc:
            RestService._handle_error(exc, endpoint)

    def get(self, endpoint):
        """Delete an existing collection

        :param endpoint: the necessary delete endpoint
        :return:
        """
        try:
            return requests.get(
                self.url + endpoint,
                cookies=self.cookie,
                headers=self.headers,
                verify=False)
        except requests.exceptions.RequestException, exc:
            RestService._handle_error(exc, endpoint)

    @staticmethod
    def _handle_error(error, endpoint):
        custom_msg = generate_error_message(error, endpoint)
        raise NRNSAException(custom_msg)
