from collections import defaultdict
from mock import MagicMock

from enmscripting import SessionTimeoutException
from base import BaseTest
from mocked_data import MockedCli as mock_cli
from common.nrnsa_cli import NRNSACli
from common.log import NRNSALogger

from common.nrnsa_exception import CMEditException


class TestNrnsaCli(BaseTest):

    def setUp(self):
        self.enode_attributes = mock_cli().mocked_enode_attributes
        self.gnode_attributes = mock_cli().mocked_gnode_attributes
        self.enode_attributes_single_digit_mnc = mock_cli().mocked_enode_attributes_single_digit_mnc
        self.gnode_attributes_zero_filled_mnc = mock_cli().mocked_gnode_attributes_zero_filled_mnc
        self.gnode_attributes_enbplmnid = mock_cli().mocked_gnode_attributes_deprecated_enbplmnid
        self.gnode_attributes_unknown_plmnid =  mock_cli().mocked_cli_unknown_plmnid
        self.gnode_attributes_null_plmnid =  mock_cli().mocked_cli_null_plmnid
        self.name_to_poids = mock_cli().mocked_name_to_poid_list
        self.relationships = mock_cli().mocked_created_relationships
        self.gnode_attributes_error = mock_cli().mocked_cli_node_error
        self.gnode_namspace_error = mock_cli().mocked_cli_namespace_error

    def test_get_node_attributes_timeout_error(self):
        terminal_mock = MagicMock()
        terminal_mock.execute.side_effect = SessionTimeoutException
        object_under_test = NRNSACli()
        self.init_nrnsa_cli(object_under_test)
        object_under_test.terminal = terminal_mock
        self.assertRaises(CMEditException, object_under_test._get_nodes_attributes, "")

    def test_get_relationships(self):
        object_under_test = NRNSACli()
        object_under_test._get_nodes_attributes = MagicMock(side_effect=[
            self.enode_attributes, self.gnode_attributes
        ])
        self.init_nrnsa_cli(object_under_test)
        actual_response = object_under_test.get_relationships(self.name_to_poids)

        self.assertEqual(self.relationships[0].fdn, actual_response[0].fdn)
        self.assertEqual(self.relationships[0].nodes, actual_response[0].nodes)

    def test_get_relationships_zero_filled_mnc(self):
        object_under_test = NRNSACli()
        object_under_test._get_nodes_attributes = MagicMock(side_effect=[
            self.enode_attributes_single_digit_mnc, self.gnode_attributes_zero_filled_mnc
        ])
        self.init_nrnsa_cli(object_under_test)
        actual_response = object_under_test.get_relationships(self.name_to_poids)

        self.assertEqual(self.relationships[0].fdn, actual_response[0].fdn)
        self.assertEqual(self.relationships[0].nodes, actual_response[0].nodes)

    def test_get_node_attributes_best_effort(self):
        object_under_test = NRNSACli()
        object_under_test._get_nodes_attributes = MagicMock(side_effect=[
            self.enode_attributes, self.gnode_attributes_error
        ])
        self.init_nrnsa_cli(object_under_test)
        actual_response = object_under_test.get_relationships(self.name_to_poids)

        self.assertEqual(self.relationships[0].fdn, actual_response[0].fdn)
        self.assertEqual(self.relationships[0].nodes, actual_response[0].nodes)

        msg = NRNSALogger.logger.handlers[0].messages
        self.assertIn('Error returned by CLI: {0}'.format('Execution Error (Node ID: svc-3-mscmce. Exception occurred: '
                                                          'ManagedObject READ command for Node ['
                                                          'ManagedElement=NR01gNodeBRadio00004,GNBCUCPFunction=1,'
                                                          'EUtraNetwork=1,ExternalENodeBFunction=1] has failed in <get>'
                                                          ' operation. RESPONSE ERROR MESSAGE FROM NODE: [Netconf '
                                                          'Connect operation has failed after 3 attempts])'),
                      msg['warning'])
        self.assertTrue(object_under_test.cli_error)

    def test_get_node_attributes_error(self):
        object_under_test = NRNSACli()
        object_under_test._get_nodes_attributes = MagicMock(side_effect=[
            self.enode_attributes, self.gnode_namspace_error,
            self.gnode_namspace_error
        ])
        self.init_nrnsa_cli(object_under_test)
        actual_response = object_under_test.get_relationships(self.name_to_poids)

        self.assertEqual([], actual_response)

    def test_get_node_attributes_unknown_plmnid(self):
        object_under_test = NRNSACli()
        object_under_test._get_nodes_attributes = MagicMock(side_effect=[
            self.enode_attributes, self.gnode_attributes_unknown_plmnid,
            self.gnode_attributes_enbplmnid
        ])
        self.init_nrnsa_cli(object_under_test)
        actual_response = object_under_test.get_relationships(self.name_to_poids)

        self.assertEqual(self.relationships[0].fdn, actual_response[0].fdn)
        self.assertEqual(self.relationships[0].nodes, actual_response[0].nodes)

    def test_get_node_attributes_null_plmnid(self):
        object_under_test = NRNSACli()
        object_under_test._get_nodes_attributes = MagicMock(side_effect=[
            self.enode_attributes, self.gnode_attributes_null_plmnid,
            self.gnode_attributes_enbplmnid
        ])
        self.init_nrnsa_cli(object_under_test)
        actual_response = object_under_test.get_relationships(self.name_to_poids)

        self.assertEqual(self.relationships[0].fdn, actual_response[0].fdn)
        self.assertEqual(self.relationships[0].nodes, actual_response[0].nodes)

    def test_parse_gnode_attributes_no_fdn(self):
        object_under_test = NRNSACli()
        object_under_test._get_nodes_attributes = MagicMock(side_effect=[
            self.enode_attributes, self.gnode_namspace_error,
            self.gnode_attributes
        ])
        self.init_nrnsa_cli(object_under_test)
        relationships = object_under_test.get_relationships(self.name_to_poids)
        self.assertEqual([], relationships)

    def init_nrnsa_cli(self, nrnsa_cli):
        nrnsa_cli.enode_list = []
        nrnsa_cli.gnode_list = defaultdict(list)
        nrnsa_cli.relationship_list = defaultdict(list)
        nrnsa_cli.log = NRNSALogger()
