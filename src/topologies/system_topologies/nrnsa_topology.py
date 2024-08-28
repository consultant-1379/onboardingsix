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
import sys
import os

from common.nrnsa_exception import NRNSAException, DeleteException

from topologies.topology import Topology
from topologies.system_topologies.system_topology_creator import \
    SystemTopologyCreator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class NrnsaTopology(Topology):

    def __init__(self):
        Topology.__init__(self, os.path.dirname(os.path.abspath(__file__)))
        self.relationships = None

    def _initialize_nodes(self):
        enodebs = self.collection_utils.execute_query(
            self.constants['queries']['get_radio_node'])
        name_to_poid_list = self.collection_utils.get_node_names(enodebs)

        self.relationships = self.collection_utils.get_relations_via_cli(
            name_to_poid_list)

    def _get_nrnsa_topology_id(self):
        topology = self.collection_utils.get_custom_topology(
            self.constants['name'])
        if topology:
            if NrnsaTopology.is_system_created(topology):
                return topology['id']
            else:
                self.collection_utils.delete_topology(topology['id'])
        return self.collection_utils.create_topology(self.constants['name'])[
            'id']

    @staticmethod
    def is_system_created(topology):
        return 'userId' not in topology or \
               topology['userId'] is None

    def run(self):
        try:
            self._initialize_nodes()
        except NRNSAException as error:
            self.log.exception(error)
            print('NR-NSA Topology has failed to process, check the logs at '
                  '/opt/ericsson/nr-nsa-systems-topology/log/nrnsa_log '
                  'for more details')
            return

        try:
            topology_creator = SystemTopologyCreator(
                self._get_nrnsa_topology_id())
        except DeleteException as error:
            self.log.exception(error)
            print("NR-NSA script failed to delete duplicate topology. "
                  "Please delete the topology and run the script again.")

        if not self.relationships:
            self.log.error(
                "NR-NSA topology not created due to missing relationships")
            topology_creator.delete_topology()
        else:
            if self.collection_utils.cli_error:
                topology_creator.completed_without_errors = False
            topology_creator.process_relationships(
                self.relationships, '-NR-NSA')
