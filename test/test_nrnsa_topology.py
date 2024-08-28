from base import BaseTest
from mock import mock
from topologies.system_topologies.nrnsa_topology import NrnsaTopology
from common.log import NRNSALogger
import mock_service_exception_response
from common.nrnsa_exception import NRNSAException


class TestNrnsaTopology(BaseTest):

    def setUp(self):
        super(TestNrnsaTopology, self)

    @mock.patch(
        'common.collection_utils.CollectionUtils.get_relations_via_cli',
        return_value=None)
    def test_run_no_relationships(self, get_relations_mock):
        NrnsaTopology().run()
        msg = NRNSALogger.logger.handlers[0].messages
        self.assertIn(
            'NR-NSA topology not created due to missing relationships',
            msg['error'])

    @mock.patch(
        'common.collection_utils.CollectionUtils.get_custom_topology',
        return_value=None)
    @mock.patch(
        'topologies.system_topologies.system_topology_creator'
        '.SystemTopologyCreator.process_relationships',
        return_value=None)
    @mock.patch(
        'common.collection_utils.CollectionUtils.get_relations_via_cli',
        return_value="valid_relationships")
    def test_run_success(self, relationships_mock, process_relationships_mock,
                         get_topology_id_mock):
        NrnsaTopology().run()
        msg = NRNSALogger.logger.handlers[0].messages

        assert process_relationships_mock.call_count == 1
        self.assertIn("NR-NSA script created NR-NSA Topology", msg['info'])

    @mock.patch(
        'common.collection_utils.CollectionUtils.get_custom_topology')
    @mock.patch(
        'common.collection_utils.CollectionUtils.delete_topology',
        return_value=None)
    def test_get_nrnsa_topology_id_user_created_topology(
            self, delete_topology_mock, get_topology_id_mock):
        get_topology_id_mock.return_value = {
            "id": "9876543217",
            "name": "NR-NSA",
            "category": "Public",
            "userId": "administrator",
            "parentId": None
        }
        topology_id = NrnsaTopology()._get_nrnsa_topology_id()
        msg = NRNSALogger.logger.handlers[0].messages
        self.assertIsNotNone(topology_id)
        self.assertTrue(delete_topology_mock.called)
        self.assertIn("NR-NSA script created NR-NSA Topology", msg['info'])

    @mock.patch(
        'common.collection_utils.CollectionUtils.get_custom_topology',
        return_value=None)
    @mock.patch(
        'topologies.system_topologies.system_topology_creator'
        '.SystemTopologyCreator.process_relationships',
        return_value=None)
    @mock.patch(
        'common.collection_utils.CollectionUtils.get_relations_via_cli',
        return_value="valid_relationships")
    def test_run_cli_error(self, relationships_mock, process_relationships_mock,
                         get_topology_id_mock):
        object_under_test = NrnsaTopology()
        object_under_test.collection_utils.cli_error = True
        object_under_test.run()
        msg = NRNSALogger.logger.handlers[0].messages
        assert process_relationships_mock.call_count == 1
        self.assertIn("NR-NSA script created NR-NSA Topology", msg['info'])
