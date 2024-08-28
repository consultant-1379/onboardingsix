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
    return get_response_data(test_data["error_response"])

def post_duplicate(endpoint, data):
    return get_response_data(test_data["error_response"], 409)

def put(endpoint, data):
    return get_response_data(test_data["error_response"])

def delete(endpoint):
    return get_response_data(test_data["error_response"])

def get(endpoint):
    if endpoint.find("LTE-ERBS") != -1:
        collection = {"collections": [test_data['collections_by_name']['LTE-ERBS-1']]}
        return get_response_data(collection, 200)
    else:
        return get_response_data(test_data["error_response"])


def get_response_data(text, status_code=400):
        the_response = MagicMock(return_value=Response)
        the_response.status_code = status_code
        the_response.text = json.dumps(text)
        return the_response
