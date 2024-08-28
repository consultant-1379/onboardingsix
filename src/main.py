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
import getpass
import sys
import json
import os
import urllib3

from bin.setup import Setup

from lib.crypt import Crypter
from common.log import NRNSALogger
from common.nrnsa_exception import NRNSAException
from common.network_utils import NetworkUtils
from common.sso_manager import SsoManager
from common.collection_utils import CollectionUtils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Main(object):
    @staticmethod
    def return_classname_from_path(path):
        path_entries = path.split(".")
        return path_entries[-1]

    @staticmethod
    def get_camel_case(class_name):
        words = class_name.split("_")
        new_word = ""
        for word in words:
            new_word += word.title()
        return new_word

    @staticmethod
    def execute_topology():
        # read the configuration file.
        log = NRNSALogger()
        file_path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(file_path, 'topologies/topology.json')
        tasks = []
        with open(filename) as open_file:
            for topology in json.load(open_file)['topologies']:
                module = __import__(topology['module'], fromlist=[None])
                class_name = getattr(module, Main().get_camel_case(
                    Main().return_classname_from_path(topology['module'])))
                try:
                    if 'constantKey' in topology:
                        process = class_name(topology['constantKey'])
                    else:
                        process = class_name()
                    process.start()
                    tasks.append(process)
                except NRNSAException as error:
                    log.exception(error)
                    print('NR-NSA script failed to process some of the '
                          'collections, check the logs at '
                          '/opt/ericsson/nr-nsa-systems-topology/log/'
                          'nrnsa_log for more details')
        for task in tasks:
            task.join()
        CollectionUtils().delete_cookie()
        log.info("NR-NSA script Completed")
        print("NR-NSA script Completed")

    @staticmethod
    def init_run():
        username = getpass.getuser()
        password = ""
        crypt = Crypter()
        setup = Setup()

        if len(sys.argv) > 1:
            if sys.argv[1] == "cron":
                password = crypt.get_password(
                    'nr-nsa-systems-topology', username)
        else:
            setup.set_password()
            password = crypt.get_password(
                'nr-nsa-systems-topology', username)
        hostname = NetworkUtils().get_enm_hostname()
        url = 'https://' + str(hostname)
        return SsoManager().create_cookie(url, username, password)


if __name__ == "__main__":
    NRNSALogger().setup_log()
    COOKIE_CREATED = Main.init_run()
    if COOKIE_CREATED:
        NRNSALogger().info("NR-NSA script started")
        print("NR-NSA script started....")
        Main().execute_topology()
