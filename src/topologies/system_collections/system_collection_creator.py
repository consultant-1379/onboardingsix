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
from __future__ import print_function
import os

import urllib3

from topologies.topology import Topology
from common.nrnsa_exception import NRNSAException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SystemCollectionCreator(Topology):
    def __init__(self, key):
        Topology.__init__(self, os.path.dirname(os.path.abspath(__file__)))
        self.constants = self.constants[key]
        self.created_successfully = False
        self.collection = None

    def _handle_collection(self):
        """Handle the collection actions when it already exists.

        The collection will be updated if it is system created.
        The collection will be delete if it is non system created.
        The collection will be created if a duplicate is deleted.

        :return: A Valid Collection Id or None
        """
        if not self.collection:
            self.collection = self.collection_utils.create_system_collection(
                self.constants['name'])
        elif not self.is_system_created():
            self.collection_utils.delete_collection(self.collection['id'])
            self.collection = self.collection_utils.create_system_collection(
                self.constants['name'])

        return self.collection['id']

    def is_system_created(self):
        return 'userId' not in self.collection or \
               self.collection['userId'] is None

    def run(self):
        try:
            self.collection = self.collection_utils.get_collection_by_name(
                self.constants['name'])
            nodes = self.collection_utils.execute_query(
                self.constants['queries']['GET_NODES'])
            if len(nodes) > 25000:
                nodes = nodes[:24999]
                self.log.debug(
                    'NR-NSA script: Mo count exceeds the 25,000 limit for {}. '
                    'MO List has been reduced to 24,999'.format(
                        self.constants['name']))

            if nodes:
                collection_id = self._handle_collection()
                if collection_id:
                    self.created_successfully = True
                    self.collection_utils.update_collection(collection_id,
                                                            nodes)
                    self.log.info(
                        "NR-NSA script: {1} collection updated, containing "
                        "{0} mo's".format(len(nodes), self.constants['name']))
            else:
                self.created_successfully = False
                self.log.info(
                    "Failed to find "
                    "the correct nodes for {0}".format(self.constants['name']))
                self._clean_up()
        except NRNSAException as error:
            self.log.exception(error)
            self.created_successfully = False
            self._clean_up()
        self.print_on_completion(self.constants['name'])

    def print_on_completion(self, name):
        if self.created_successfully:
            print("{0} has been processed successfully".format(
                name))
        else:
            print("{0} has failed to process, check the logs at "
                  "/opt/ericsson/nr-nsa-systems-topology/log/nrnsa_log"
                  " for more details".format(name))

    def _clean_up(self):
        if self.collection and self.is_system_created():
            self.collection_utils.delete_collection(self.collection['id'])
