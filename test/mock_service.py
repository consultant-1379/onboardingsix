import json
import os
from mock import MagicMock
from requests.models import Response

file_path = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(file_path, 'test_data.json')
test_data = {}
with open(filename) as f:
    test_data = json.load(f)

def post(endpoint, data):
    if endpoint.find("/object-configuration/collections/v3") != -1:
        if endpoint.find("isSystemCreated") != -1:
            return create(data)
    elif endpoint.find("/object-configuration/custom-topology/v1/") != -1:
        return create(data)
    elif endpoint.find("/object-configuration/custom-topology/v1") != -1:
        return create(data)
    elif endpoint.find("/managedObjects/getPosByPoIds") != -1:
        return get_pos_by_po_ids()

def put(endpoint, data):
    if not data:
        verify_remove_request(endpoint)
    return get_by_id(endpoint)

def delete(endpoint):
    if endpoint.find("object-configuration/custom-topology/v1") != -1:
        collection_id = endpoint.split("/")
        collection_id = collection_id[len(collection_id) - 1]
        collection = [test_data['collections_by_id'][collection_id]]
        if collection[0]['parentId'] is None and collection[0]['name'] != 'NR-NSA':
            return get_response_data({}, 404)
    return get_response_data({}, 200)

def get(endpoint):
    if endpoint.find("/object-configuration/collections/v2") != -1:
        if endpoint.find("collectionName") != -1:
            return get_by_name(endpoint)
    elif endpoint.find("/object-configuration/v1/collections/") != -1:
        return get_by_id(endpoint)
    elif endpoint.find("/object-configuration/custom-topology/v1") != -1:
        if endpoint.find("customTopology") != -1:
            return get_custom_topologies()
        elif endpoint.find("parentId") != -1:
            return get_children()
    elif endpoint.find("/managedObjects/search/v2") != -1:
        objects = test_data['node_list']
        return get_response_data({"objects":objects}, 200)

def verify_remove_request(endpoint):
    collection_id = endpoint.split("/")
    child_id = collection_id[len(collection_id) - 1]
    parent_id = collection_id[len(collection_id) - 2]

    if not child_id.isdigit() or not parent_id.isdigit():
        return get_response_data(test_data["error_response"], 400)

def get_by_name(endpoint):
    name = endpoint.split("=")
    name = name[len(name)-1]
    if name in test_data['collections_by_name']:
        collection = {"collections": [test_data['collections_by_name'][name]]}
    else:
        collection = {"collections":[]}

    return get_response_data(collection, 200)

def get_by_id(endpoint):
    collection_id = endpoint.split("/")
    collection_id = collection_id[len(collection_id)-1]
    if collection_id in test_data['collections_by_id']:
        collection = test_data['collections_by_id'][collection_id]
    else:
        collection = None

    return get_response_data(collection, 200)

def get_custom_topologies():
    collection = test_data['collections_by_name']["NR-NSA"]
    return get_response_data([collection], 200)

def get_children():
    collections = [test_data['collections_by_id']["9876543211"],
                   test_data['collections_by_id']["9876543212"]]
    return get_response_data(collections, 200)

def get_no_children():
    collections = []
    return get_response_data(collections, 200)

def create(data):
    collection = test_data['collections_by_name'][data['name']]
    return get_response_data(collection, 201)

def get_pos_by_po_ids():
    collection = test_data['node_list']
    return get_response_data(collection, 200)

def get_response_data(text, status_code=201):
        the_response = MagicMock(return_value=Response)
        the_response.status_code = status_code
        the_response.text = json.dumps(text)
        return the_response
