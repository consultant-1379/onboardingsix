import StringIO
import json
import os
import sys

from base import BaseTest
from mock import mock
from common.nrnsa_cli import Relationship
from common.log import NRNSALogger
from topologies.system_topologies.system_topology_creator import \
    SystemTopologyCreator
import mock_service_exception_response
import mock_service


class TestSystemTopologyCreator(BaseTest):

    def setUp(self):
        super(TestSystemTopologyCreator, self)
        file_path = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(file_path, 'test_data.json')
        with open(filename) as f:
            test_data = json.load(f)
        relationship_data = test_data["relationships"]
        self.relationships = [Relationship(
            fdn=relationship_data["Leaf1"]["fdn"],
            nodes=relationship_data["Leaf1"]["nodes"]),
            Relationship(
                fdn=relationship_data["Leaf2"]["fdn"],
                nodes=relationship_data["Leaf2"]["nodes"]),
            Relationship(
                fdn=relationship_data["Leaf3"]["fdn"],
                nodes=relationship_data["Leaf3"]["nodes"]),
        ]
        NRNSALogger.logger.handlers[0].reset()

    @mock.patch('common.collection_utils.CollectionUtils.get_children')
    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service.get)
    def test_process_relationships_new_collections(self, mock_get,
                                                   get_children_mock):
        get_children_mock.side_effect = [[], mock_service.get]
        SystemTopologyCreator("1").process_relationships(
            self.relationships, '-NR-NSA')
        msg = NRNSALogger.logger.handlers[0].messages
        self.assertIn("NR-NSA Topology has been processed successfully",
                      msg['info'])
        assert len(msg['error']) == 0

    def test_process_relationships_existing_collections(self):
        SystemTopologyCreator("9876543210").process_relationships(
            self.relationships, '-NR-NSA')
        msg = NRNSALogger.logger.handlers[0].messages
        self.assertIn("NR-NSA script deleted duplicate user added collection "
                      "'Leaf2-NR-NSA'",
                      msg['info'])
        self.assertIn("NR-NSA Topology has been processed successfully",
                      msg['info'])
        assert len(msg['error']) == 0

    @mock.patch('common.rest_service.RestService.put',
                side_effect=mock_service_exception_response.put)
    def test_process_relationships_update_failure(self, put_mock):
        SystemTopologyCreator("9876543210").process_relationships(
            self.relationships, '-NR-NSA')
        msg = NRNSALogger.logger.handlers[0].messages
        self.assertIn("NR-NSA script failed to update collection with id: "
                      "9876543213, cause: Invalid request",
                      msg['warning'])
        assert len(msg['error']) == 0

    @mock.patch('common.collection_utils.CollectionUtils.get_children')
    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service.get)
    def test_process_relationships_error(self, mock_get, get_children_mock):
        captured_output = StringIO.StringIO()
        sys.stdout = captured_output
        get_children_mock.side_effect = [[], mock_service.get]
        object_under_test = SystemTopologyCreator("1")
        object_under_test.completed_without_errors = False
        object_under_test.process_relationships(
            self.relationships, '-NR-NSA')
        sys.stdout = sys.__stdout__
        self.assertIn("NR-NSA Systems Topology has been processed with "
                      "warnings, check the logs at /opt/ericsson/"
                      "nr-nsa-systems-topology/log/nrnsa_log "
                      "for more details",
                      captured_output.getvalue())





