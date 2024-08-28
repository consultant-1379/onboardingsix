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

from collections import defaultdict
from common import constants
from common.log import NRNSALogger
from common.nrnsa_exception import CMEditException
from lib.parser import CmeditGetOutputParser
import enmscripting


class Relationship(object):
    """
        @:param poid is unused for the new relationship implementation.
    """

    def __init__(self, poid=None, fdn=None, nodes=None):
        self.poid = poid
        self.fdn = fdn
        self.nodes = nodes


class NRNSACli(object):

    def __init__(self, server=None, username=None, password=None):
        self.session = enmscripting.open(server, username, password)
        self.terminal = self.session.terminal()
        self.enode_list = []
        self.gnode_list = defaultdict(list)
        self.relationship_list = defaultdict(list)
        self.log = NRNSALogger()
        self.cli_error = False

    def _get_nodes_attributes(self, cmd):
        """Execute Cli command and return cli output
        """
        try:
            node_attributes = self.terminal.execute(cmd)
            if any('Error' in block for block in node_attributes.get_output()):
                cli_error = [block for block in node_attributes.get_output() if
                             'Error' in block]
                self.log.warn(
                    "Cli returned the following error: {0}".format(cli_error))
        except Exception as error:
            raise CMEditException(cmd, str(error))

        return '\n'.join(node_attributes.get_output())

    def get_relationships(self, name_to_poid_list):
        """Return List of Relationship objects
        """
        self._parse_enode_attributes(self._get_nodes_attributes(
            constants.CLI_GET_RADIO_NODE_ATTRIBUTES))
        self._get_gnode_attributes()
        return self._compare_node_lists(name_to_poid_list)

    def _get_gnode_attributes(self):
        """Gets gnode attributes for either pLMNId or enbplmnid
           If 'cmedit get' command using pLMNId returns an Error 1010
           (unknown attribute), or either pLMNId value is returned null,
           then 'cmedit get' will be executed again using enbplmnid
        """
        gnode_response = self._get_nodes_attributes(
            constants.CLI_GET_NR_RADIO_NODE_ATTRIBUTES_PLMNID)
        if ('Error 1010' in gnode_response or
                'pLMNId : null' in gnode_response):
            self._parse_gnode_attributes(self._get_nodes_attributes(
                constants.CLI_GET_NR_RADIO_NODE_ATTRIBUTES))
        else:
            self._parse_gnode_attributes(gnode_response)

    def _parse_gnode_attributes(self, gnode_response):
        """Parse Gnode cli output data to usable dictionary
        """
        gnodes_parser = CmeditGetOutputParser(gnode_response)
        gnodes = gnodes_parser.parse()
        for gnode_name, attributes in gnodes.items():
            for gnode_fdn in attributes:
                enode_attribute = CmeditGetOutputParser.parse_gnodes(
                    gnode_fdn)
                if 'Error 9999' in attributes[gnode_fdn]:
                    self.log.warn('Error returned by CLI: {0}'
                                  .format(attributes[gnode_fdn]['Error 9999']))
                    self.cli_error = True
                elif 'ExternalENodeBFunction' in enode_attribute:
                    if 'pLMNId' in attributes[gnode_fdn]:
                        key = str(
                            attributes[gnode_fdn]['pLMNId'].data[
                                'mcc'] + ":" +
                            attributes[gnode_fdn]['pLMNId'].data[
                                'mnc'] + ":" + attributes[gnode_fdn][
                                    'eNodeBId'])
                        self.gnode_list[key].append(gnode_name)
                    else:
                        key = str(attributes[gnode_fdn]['eNBPlmnId'] +
                                  ":" + attributes[gnode_fdn]['eNodeBId'])
                        self.gnode_list[key].append(gnode_name)
                else:
                    self.log.warn(
                        'Current Node does not contain an '
                        'ExternalEnodeBFunction: {0}'.format(enode_attribute))

    def _parse_enode_attributes(self, enode_response):
        """Parse Enode cli output data to usable dictionary
        """
        enode_list = {}
        enodes = CmeditGetOutputParser(enode_response)
        enodes = enodes.parse()
        for enode_name, attributes in enodes.items():
            for enode_fdn in attributes:
                key = str(
                    attributes[enode_fdn]['eNodeBPlmnId'].data[
                        'mcc'] + ':' +
                    self._get_zero_filled_mnc(attributes[enode_fdn][
                        'eNodeBPlmnId'].data['mnc'], attributes[enode_fdn][
                            'eNodeBPlmnId'].data['mncLength']) + ':' +
                    attributes[enode_fdn]['eNBId'])
                enode_list[key] = enode_name
        self.enode_list = enode_list

    def _compare_node_lists(self, name_to_poid_list):
        """Compare Node Attributes to find relationships,
           These matches should then be passed onto the
           _create_relationships method
        """
        self.relationship_list = defaultdict(list)
        for key in self.gnode_list:
            gnode_fdns = self.gnode_list[key]
            if key in self.enode_list:
                enode_fdn = self.enode_list[key]
                for gnode in gnode_fdns:
                    if enode_fdn not in self.relationship_list:
                        self.relationship_list[enode_fdn].append(
                            name_to_poid_list[enode_fdn])
                        self.relationship_list[enode_fdn].append(
                            name_to_poid_list[gnode])
                    else:
                        self.relationship_list[enode_fdn].append(
                            name_to_poid_list[gnode])
        return self._create_relationships(self.relationship_list)

    @staticmethod
    def _get_zero_filled_mnc(mnc, mnc_length):
        """Adds leading zeroes to mnc, if needed
        """
        return mnc.zfill(int(mnc_length))

    @staticmethod
    def _create_relationships(relationships):
        """Create Relationship Objects from the relationships found during
        the matching process.
        These relationships are used to create the collections needed for
        the NR-NSA Topology
        """
        relationship_list = []
        for relationship in relationships:
            new_relationship = Relationship(
                fdn=relationship, nodes=relationships[relationship])
            relationship_list.append(new_relationship)
        return relationship_list
