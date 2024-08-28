import requests

from mock import MagicMock, patch, mock
from behave import given, when, then
from contextlib import nested
from common import constants
from common.collection_utils import CollectionUtils
from topologies.system_collections.system_collection_creator \
    import SystemCollectionCreator

utils = CollectionUtils()
query = {
    "RadioNodes": "select all objects of type ManagedElement where ManagedElement has child EnodeBFunction from node type RadioNode&orderby=moName&orderdirection=asc",
    "NR-RadioNodes": "select all objects of type ManagedElement where ManagedElement has child GNBDUFunction from node type RadioNode&orderby=moName&orderdirection=asc",
    "ERBS Nodes": "get all objects of type NetworkElement from node type ERBS&orderby=moName&orderdirection=asc"
}


@given('there are {nodes} in the system and {key} is passed')
def step_impl(context, nodes, key):
    context.nodes = utils.execute_query(query[nodes])
    context.sys_instance = SystemCollectionCreator(key)


@when('{collection_name} collection doesnt exist')
def step_impl(context, collection_name):
    with patch('common.collection_utils.CollectionUtils'
               '.get_collection_by_name') as mock_get:
        mock_get.return_value = None
        context.sys_instance.run()


@then('{collection_name} collection should be created')
def step_impl(context, collection_name):
    collection = utils.get_collection_by_name(collection_name)
    url = "https://localhost:4000{0}/{1}".format(constants.COLLECTIONS_V1,
                                                 collection['id'])
    collection_contents = requests.get(url, verify=False).json()
    assert collection_contents['objects'] is not None
    assert len(collection_contents['objects']) == len(context.nodes)
    assert "{0} has been processed successfully".format(
        collection_name) in context.stdout_capture.getvalue()


@when('{collection_name} collection does exist')
def step_impl(context, collection_name):
    context.sys_instance.run()


@then('{collection_name} collection should be updated')
def step_impl(context, collection_name):
    assert "{} has been processed successfully".format(
        collection_name) in context.stdout_capture.getvalue()
    assert "NR-NSA script: {0} collection updated, containing {1} mo's".format(
        collection_name, len(context.nodes)) in logs(
        context.log_capture.buffer)


"""The system does not contain RadioNodes
"""


@given('the system does not contain {nodes} and {key} is passed')
def step_impl(context, nodes, key):
    context.sys_instance = SystemCollectionCreator(key)


@when('{collection_name} collection does not exist')
def step_impl(context, collection_name):
    with nested(
            patch('common.collection_utils.CollectionUtils.execute_query',
                  return_value=[]),
            patch(
                'common.collection_utils.CollectionUtils.get_collection_by_name',
                return_value=None)
    ):
        context.sys_instance.run()


@then('the script should not create the {collection_name} collection')
def step_impl(context, collection_name):
    assert "{} has failed to process, check the logs at " \
           "/opt/ericsson/nr-nsa-systems-topology/log/nrnsa_log " \
           "for more details".format(
        collection_name) in context.stdout_capture.getvalue()
    assert "Failed to find the correct nodes for {0}".format(
        collection_name) in logs(
        context.log_capture.buffer)


@when('{collection_name} collection does exist and no nodes')
@patch('common.collection_utils.CollectionUtils.execute_query', return_value=[])
def step_impl(context, mock_method, collection_name):
    context.sys_instance.run()


@then('{collection_name} collection should be deleted')
def step_impl(context, collection_name):
    collection = utils.get_collection_by_name(collection_name)
    log_entries = logs(context.log_capture.buffer)
    assert any(
        "NR-NSA script: collection deleted with the given id {0}".format(
            collection['id']) in log for log in log_entries)


"""Duplicate Collection
"""


@given('{nodes} are in the system and a collection with the name {'
       'collection_name} exists and {key} is passed')
def step_impl(context, nodes, collection_name, key):
    context.collection = {
        "id": "2814749753457653",
        "name": collection_name,
        "category": "Public",
        "userId": "administrator",
        "timeCreated": 1555579360871
    }
    context.sys_instance = SystemCollectionCreator(key)
    context.nodes = utils.execute_query(query[nodes])


@when(
    'the script attempts to create the system defined {collection_name} '
    'collection')
@mock.patch('common.collection_utils.CollectionUtils.get_collection_by_name')
def step_impl(context, mock_get_by_name, collection_name):
    mock_get_by_name.return_value = context.collection
    context.sys_instance.run()


@step('the non system created collection {collection_name} should be deleted')
def step_impl(context, collection_name):
    log_entries = logs(context.log_capture.buffer)
    assert any(
        "NR-NSA script: collection deleted with the given id {0}".format(
            context.collection['id']) in log for log in log_entries)


@step('{collection_name} collection should be created')
def step_impl(context, collection_name):
    assert "NR-NSA script: {0} collection created".format(
        collection_name) in logs(context.log_capture.buffer)


@step('the {collection_name} should be updated')
def step_impl(context, collection_name):
    assert "NR-NSA script: {0} collection updated, containing {1} mo's".format(
        collection_name, len(context.nodes)) in logs(
        context.log_capture.buffer)


def logs(log_buffer):
    return [entry.getMessage() for entry in log_buffer]
