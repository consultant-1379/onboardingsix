from base import BaseTest
import mock
from common.collection_utils import CollectionUtils
from common.log import NRNSALogger
from common.nrnsa_exception import NRNSAException

import mock_service
import mock_service_exception_response


class TestCollectionUtils(BaseTest):

    def setUp(self):
        super(TestCollectionUtils, self).setUp()
        self.post_patcher = mock.patch('common.rest_service.RestService.post',
                                       side_effect=mock_service.post)
        self.get_patcher = mock.patch('common.rest_service.RestService.get',
                                      side_effect=mock_service.get)
        self.init_patcher = mock.patch('common.nrnsa_cli.NRNSACli.__init__',
                                  return_value=None)
        self.post_patcher.start()
        self.init_patcher.start()
        self.get_patcher.start()

    def teardown(self):
        self.post_patcher.stop()
        self.get_patcher.stop()
        self.init_patcher.stop()

    def test_create_topology(self):
        response = CollectionUtils().create_topology("NR-NSA")
        msg = NRNSALogger.logger.handlers[0].messages

        assert response['id'] == str(9876543210)
        self.assertIn("NR-NSA script created NR-NSA Topology", msg['info'])

    def test_create_topology_exception(self):
        post_patcher = mock.patch('common.rest_service.RestService.post',
                                  side_effect=mock_service_exception_response.post)
        post_patcher.start()
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().create_topology("Invalid_Topology")
        self.assertEqual('NR-NSA script failed to create Invalid_Topology '
                         'Topology, cause: Invalid request',
                         str(context.exception.message))

    def test_create_system_collection(self):
        response = CollectionUtils().create_system_collection('LTE-ERBS')

        assert response['id'] == str(9876543213)

    def test_create_system_collection_exception(self):
        post_patcher = mock.patch('common.rest_service.RestService.post',
                                  side_effect=mock_service_exception_response.post)
        post_patcher.start()
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().create_system_collection("LTE-ERBS")
        self.assertEqual('NR-NSA script failed to create collection with '
                         'name: LTE-ERBS, cause: Invalid request',
                         str(context.exception.message))

    def test_create_leaf_collection(self):
        response = CollectionUtils().create_leaf_collection('Leaf1-NR-NSA',
                                                            9876543210)

        assert response['id'] == str(9876543211)

    def test_create_leaf_collection_exception(self):
        post_patcher = mock.patch('common.rest_service.RestService.post',
                                  side_effect=mock_service_exception_response.post)
        post_patcher.start()
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().create_leaf_collection("Leaf1-NR-NSA",
                                                     9876543210)
        self.assertEqual('NR-NSA script failed to create collection with '
                         'name: Leaf1-NR-NSA, cause: Invalid request',
                         str(context.exception.message))

    @mock.patch('common.rest_service.RestService.post',
                side_effect=mock_service_exception_response.post_duplicate)
    @mock.patch('common.collection_utils.CollectionUtils.'
                '_handle_duplicate_collection')
    def test_create_leaf_collection_duplicate(self, mock_duplicate, mock_post):
        mock_duplicate.return_value = {
            "id": "9876543211",
            "name": "Leaf1-NR-NSA",
            "category": "Public",
            "userId": None,
            "parentId": "9876543210"
        }
        collection = CollectionUtils().create_leaf_collection(
            "Leaf1-NR-NSA", 9876543210)
        msg = NRNSALogger.logger.handlers[0].messages

        assert collection['id'] == str(9876543211)
        self.assertIn('NR-NSA script failed to create collection, '
                      'collection name Leaf1-NR-NSA in use', msg['info'])

    def test_handle_duplicate_collection(self):
        collection = CollectionUtils()._handle_duplicate_collection(9876543210, "Leaf1-NR-NSA")
        assert collection
        assert collection['id'] == "9876543211"

    def test_handle_duplicate_collection_not_found(self):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils()._handle_duplicate_collection(9876543210, "Collection")
            self.assertEqual('NR-NSA script unable to find collection Collection',
                             str(context.exception.message))

    def test_get_collection_by_name(self):
        collection = CollectionUtils().get_collection_by_name("LTE-RadioNode")
        assert collection['id'] == str(9876543214)
        assert collection['name'] == 'LTE-RadioNode'

    def test_get_collection_by_name_Empty(self):
        collection = CollectionUtils().get_collection_by_name("Not_Found")
        assert collection is None

    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service_exception_response.get)
    def test_get_collection_by_name_exception(self, mock_get):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().get_collection_by_name("Invalid_Topology")
        self.assertEqual('NR-NSA script failed to get collection with '
                         'name: Invalid_Topology, cause: Invalid request',
                         str(context.exception.message))

    def test_get_collection_by_id(self):
        collection = CollectionUtils().get_collection_by_id(9876543211)
        assert collection['id'] == str(9876543211)

    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service_exception_response.get)
    def test_get_collection_by_id_exception(self, mock_get):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().get_collection_by_id(9876543210)
        self.assertEqual('NR-NSA script failed to get collection by id: '
                         '9876543210, cause: Invalid request',
                         str(context.exception.message))

    def test_get_custom_topology(self):
        topology = CollectionUtils().get_custom_topology("NR-NSA")
        assert topology['id'] == str(9876543210)

    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service_exception_response.get)
    def test_get_custom_topology_id_exception(self, mock_get):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().get_custom_topology("NR-NSA")
        self.assertEqual(
            'NR-NSA script failed to get collection with name: NR-NSA,'
            ' cause: Invalid request',
            str(context.exception.message))

    def test_get_children(self):
        collections = CollectionUtils().get_children(9876543210)
        assert len(collections) == 2
        assert collections[0]['id'] == "9876543211"
        assert collections[1]['id'] == "9876543212"

    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service_exception_response.get)
    def test_get_children_exception(self, mock_get):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().get_children(9876543210)
        self.assertEqual(
            'NR-NSA script failed to get children for parentId: '
            '9876543210, cause: Invalid request',
            str(context.exception.message))

    @mock.patch('common.rest_service.RestService.put',
                side_effect=mock_service.put)
    def test_update_collection(self, mock_put):
        CollectionUtils().update_collection(9876543211, ["1"])
        assert mock_put.call_count == 1

    @mock.patch('common.rest_service.RestService.put',
                side_effect=mock_service_exception_response.put)
    def test_update_collection_exception(self, mock_put):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().update_collection(9876543211, ["1"])
        self.assertEqual(
            'NR-NSA script failed to update collection with id: '
            '9876543211, cause: Invalid request',
            str(context.exception.message))
        assert mock_put.call_count == 1

    @mock.patch('common.rest_service.RestService.put',
                side_effect=mock_service.put)
    def test_remove_collection(self, mock_put):
        CollectionUtils().remove_collection(9876543211, 9876543210)
        msg = NRNSALogger.logger.handlers[0].messages

        assert mock_put.call_count == 1
        self.assertIn("NR-NSA script attempting to remove collection with "
                      "id '9876543211' from topology", msg['debug'])

    @mock.patch('common.rest_service.RestService.put',
                side_effect=mock_service_exception_response.put)
    def test_remove_collection_exception(self, mock_put):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().remove_collection(9876543211, 9876543210)
        self.assertEqual(
            'NR-NSA script failed to remove collection with id: '
            '9876543211 from NR-NSA topology, cause: Invalid request',
            str(context.exception.message))
        assert mock_put.call_count == 1

    @mock.patch('common.rest_service.RestService.delete',
                side_effect=mock_service.delete)
    def test_delete_collection(self, mock_delete):
        CollectionUtils().delete_collection(9876543211)
        assert mock_delete.call_count == 1

    @mock.patch('common.rest_service.RestService.delete',
                side_effect=mock_service_exception_response.delete)
    def test_delete_collection_exception(self, mock_delete):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().delete_collection(9876543211)
        self.assertEqual(
            "NR-NSA script Delete Action Failed, collection id:"
            " 9876543211, cause: Invalid request",
            str(context.exception.message))
        assert mock_delete.call_count == 1

    @mock.patch('common.rest_service.RestService.delete',
                side_effect=mock_service.delete)
    def test_delete_topology(self, mock_delete):
        CollectionUtils().delete_topology(9876543210)
        assert mock_delete.call_count == 1

    @mock.patch('common.rest_service.RestService.delete',
                side_effect=mock_service_exception_response.delete)
    def test_delete_topology_exception(self, mock_delete):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().delete_topology(9876543210)
        self.assertEqual(
            "NR-NSA script Delete Action Failed, collection "
            "id: 9876543210, cause: Invalid request",
            str(context.exception.message))
        assert mock_delete.call_count == 1

    def test_execute_query(self):
        result = CollectionUtils().execute_query('anyQuery')
        assert len(result) == 4
        assert result[0] == "281475095534910"
        assert result[3] == "281475095534913"

    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service_exception_response.get)
    def test_execute_query_exception(self, mock_get):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().execute_query('anyQuery')
        self.assertEqual(
            "NR-NSA script failed to run query: anyQuery, "
            "cause: Invalid request",
            str(context.exception.message))
        assert mock_get.call_count == 1

    def test_get_node_names(self):
        result = CollectionUtils().get_node_names(["1"])
        assert len(result) == 4
        assert result["LTE01dg2ERBS00001"] == "281475095534910"
        assert result["LTE01dg2ERBS00004"] == "281475095534913"

    @mock.patch('common.rest_service.RestService.post',
                side_effect=mock_service_exception_response.post)
    def test_get_node_names_exception(self, mock_post):
        with self.assertRaises(NRNSAException) as context:
            CollectionUtils().get_node_names(["1"])
        self.assertEqual(
            "NR-NSA script failed to get node names, "
            "cause: Invalid request",
            str(context.exception.message))
        assert mock_post.call_count == 1

    @mock.patch(
        'common.nrnsa_cli.NRNSACli')
    def test_get_relations_via_cli(self, mock_cli):
        mock_cli.get_relationships.return_value = "valid_relationships_with_warning"
        mock_cli.cli_error = True
        utils = CollectionUtils()
        utils.nrnsa_cli = mock_cli
        relationships = utils.get_relations_via_cli("name to poid")
        self.assertEqual("valid_relationships_with_warning", relationships)
        self.assertEqual(mock_cli.get_relationships.call_count, 1)
        self.assertTrue(utils.cli_error)
