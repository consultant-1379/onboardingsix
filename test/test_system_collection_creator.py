from base import BaseTest
from mock import mock
from parameterized import parameterized

from topologies.system_collections.system_collection_creator \
    import SystemCollectionCreator
from common.log import NRNSALogger
import mock_service
import mock_service_exception_response


class TestSystemCollectionCreator(BaseTest):

    def setUp(self):
        super(TestSystemCollectionCreator, self)
        self.post_patcher = mock.patch('common.rest_service.RestService.post',
                                       side_effect=mock_service.post)
        self.get_patcher = mock.patch('common.rest_service.RestService.get',
                                      side_effect=mock_service.get)
        self.put_patcher = mock.patch('common.rest_service.RestService.put',
                                      side_effect=mock_service.put)
        self.delete_patcher = mock.patch(
            'common.rest_service.RestService.delete',
            side_effect=mock_service.delete)
        self.mock_post = self.post_patcher.start()
        self.mock_get = self.get_patcher.start()
        self.mock_put = self.put_patcher.start()
        self.mock_delete = self.delete_patcher.start()
        NRNSALogger.logger.handlers[0].reset()

    @parameterized.expand([("erbs", "9876543213", "LTE-ERBS",
                            "get all objects of type NetworkElement "
                            "from node type "
                            "ERBS&orderby=moName&orderdirection=asc"),
                           ("radioLTE", "9876543214", "LTE-RadioNode",
                            "select all objects of type ManagedElement where "
                            "ManagedElement has child EnodeBFunction from "
                            "node "
                            "type "
                            "RadioNode&orderby=moName&orderdirection=asc"),
                           ("radioNR", "9876543215", "NR-RadioNode",
                            "select all objects of type ManagedElement where "
                            "ManagedElement has child GNBDUFunction from node "
                            "type "
                            "RadioNode&orderby=moName&orderdirection=asc")])
    def test_run(self, key, collection_id, name, query):
        collection_creator = SystemCollectionCreator(key)
        collection_creator.run()
        msg = NRNSALogger.logger.handlers[0].messages
        assert not msg['debug']
        assert not msg['warning']
        assert not msg['error']
        self.assertIn("NR-NSA script: {0} collection updated, containing 4 "
                      "mo's".format(name), msg['info'])
        assert self.mock_get.call_count == 2
        assert self.mock_put.call_count == 1
        assert collection_creator.created_successfully == True
        get_args, kwargs = self.mock_get.call_args_list[1]
        assert get_args[0] == "/managedObjects/search/v2?query=" + query
        put_args, kwargs = self.mock_put.call_args_list[0]
        assert put_args[
                   0] == "/object-configuration/v1/collections/" + \
               collection_id
        assert put_args[
            1], '{"objects": [{"id": "281475095534910"}, {"id": ' \
                '"281475095534911"}, {"id": "281475095534912"}, {"id": ' \
                '"281475095534913"}]}'

    @mock.patch(
        'common.collection_utils.CollectionUtils.get_collection_by_name')
    def test_run_erbs_with_non_owned_collection(self, mock_get_name):
        mock_get_name.return_value = {
            "id": "9876543217",
            "name": "LTE-ERBS",
            "category": "Public",
            "userId": "administrator",
            "parentId": None
        }
        SystemCollectionCreator("erbs").run()
        msg = NRNSALogger.logger.handlers[0].messages
        assert len(msg['info']) == 3
        assert not msg['debug']
        assert not msg['warning']
        assert not msg['error']
        assert mock_get_name.call_count == 1
        assert self.mock_get.call_count == 1
        assert self.mock_put.call_count == 1
        assert self.mock_post.call_count == 1
        assert self.mock_delete.call_count == 2
        delete_args, kwargs = self.mock_delete.call_args_list[1]
        assert delete_args[
                   0] == "/object-configuration/v1/collections/9876543217"
        get_args, kwargs = self.mock_get.call_args_list[0]
        assert get_args[
                   0] == "/managedObjects/search/v2?query=get all objects of " \
                         "" \
                         "" \
                         "type NetworkElement from node type " \
                         "ERBS&orderby=moName&orderdirection=asc"
        put_args, kwargs = self.mock_put.call_args_list[0]
        assert put_args[0] == "/object-configuration/v1/collections/9876543213"
        assert put_args[
            1], '{"objects": [{"id": "281475095534910"}, {"id": ' \
                '"281475095534911"}, {"id": "281475095534912"}, {"id": ' \
                '"281475095534913"}]}'
        self.assertIn(
            "NR-NSA script: collection deleted with the given id 9876543217",
            msg['info'])
        self.assertIn("NR-NSA script: LTE-ERBS collection created",
                      msg['info'])
        self.assertIn(
            "NR-NSA script: LTE-ERBS collection updated, containing 4 mo's",
            msg['info'])

    @mock.patch(
        'common.collection_utils.CollectionUtils.get_collection_by_name',
        return_value=None)
    def test_run_erbs_collection_not_exist(self, mock_get_name):
        SystemCollectionCreator("erbs").run()
        msg = NRNSALogger.logger.handlers[0].messages
        assert len(msg['info']) == 2
        assert not msg['debug']
        assert not msg['warning']
        assert not msg['error']
        assert mock_get_name.call_count == 1
        assert self.mock_get.call_count == 1
        assert self.mock_put.call_count == 1
        assert self.mock_post.call_count == 1
        assert self.mock_delete.call_count == 0
        get_args, kwargs = self.mock_get.call_args_list[0]
        assert get_args[
                   0] == "/managedObjects/search/v2?query=get all objects of " \
                         "" \
                         "" \
                         "type NetworkElement from node type " \
                         "ERBS&orderby=moName&orderdirection=asc"
        put_args, kwargs = self.mock_put.call_args_list[0]
        assert put_args[0] == "/object-configuration/v1/collections/9876543213"
        assert put_args[
            1], '{"objects": [{"id": "281475095534910"}, {"id": ' \
                '"281475095534911"}, {"id": "281475095534912"}, {"id": ' \
                '"281475095534913"}]}'
        self.assertIn("NR-NSA script: LTE-ERBS collection created",
                      msg['info'])
        self.assertIn(
            "NR-NSA script: LTE-ERBS collection updated, containing 4 mo's",
            msg['info'])

    @mock.patch('common.collection_utils.CollectionUtils.execute_query',
                return_value=[])
    def test_run_empty_result(self, mock_execute_query):
        SystemCollectionCreator("erbs").run()
        msg = NRNSALogger.logger.handlers[0].messages
        assert len(msg['info']) == 2
        assert self.mock_delete.call_count == 2
        assert self.mock_get.call_count == 1
        assert mock_execute_query.call_count == 1
        delete_args, kwargs = self.mock_delete.call_args_list[1]
        assert delete_args[
                   0] == "/object-configuration/v1/collections/9876543213"
        args, kwargs = mock_execute_query.call_args_list[0]
        self.assertEquals(
            "get all objects of type NetworkElement from node type "
            "ERBS&orderby=moName&orderdirection=asc",
            args[0])
        self.assertIn('Failed to find the correct nodes for LTE-ERBS',
                      msg['info'])
        self.assertIn(
            'NR-NSA script: collection deleted with the given id 9876543213',
            msg['info'])

    @mock.patch('common.rest_service.RestService.get',
                side_effect=mock_service_exception_response.get)
    def test_run_exception(self, mock_get):
        collection_creator = SystemCollectionCreator("erbs")
        collection_creator.run()
        msg = NRNSALogger.logger.handlers[0].messages
        assert collection_creator.created_successfully == False
        self.assertIn(
            "NR-NSA script failed to run query: get all objects of type "
            "NetworkElement from node type "
            "ERBS&orderby=moName&orderdirection=asc, cause: Invalid request",
            msg['error'])
