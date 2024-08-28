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
import urllib3
import requests

from common.log import NRNSALogger
import common.constants as constants
from common.nrnsa_exception import NRNSAException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NetworkUtils(object):

    def __init__(self):
        self.log = NRNSALogger()

    def get_enm_hostname(self):
        hostname = NetworkUtils.get_hostname_from_properties()
        if hostname:
            return hostname

        self.log.info('Unable to retrieve host name from \'properties\' file. '
                      'Attempting to retrieve from \'hosts\' file')
        hostname = NetworkUtils.get_hostname_from_hosts()
        if hostname:
            return hostname

        self.log.info('Unable to retrieve host name from \'hosts\' file. '
                      'Attempting to retrieve with Service Registry REST call')

        try:
            return requests.get(constants.SERVICE_REGISTRY_URL).text
        except requests.exceptions.ConnectionError:
            raise NRNSAException('Unable to retrieve host name')

    @staticmethod
    def get_hostname_from_properties():
        try:
            with open(constants.PROPERTIES_FILE_PATH, 'r') as config_file:
                if config_file:
                    for line in config_file:
                        if 'web_host_default' in line:
                            return \
                                line.replace('web_host_default=', '').rstrip()
                return None
        except IOError:
            return None

    @staticmethod
    def get_hostname_from_hosts():
        try:
            with open('/etc/hosts', 'r') as hosts:
                if hosts:
                    for line in hosts:
                        splitted_line = line.split()
                        if len(splitted_line) > 2 and \
                                'iorfile.' in splitted_line[2]:
                            return splitted_line[2].replace('iorfile.', '')
                return None
        except IOError:
            return None
