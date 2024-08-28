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

import json
import os
import urllib3

import common.constants as constants
from common.log import NRNSALogger
from common.nrnsa_cli import NRNSACli
from common.sso_manager import SsoManager
from common.rest_service import RestService
from common.nrnsa_exception import ExecuteQueryException, \
    CreateCollectionException, CreateTopologyException, \
    GetNodeNamesException, GetCollectionByNameException, \
    GetCollectionByIdException, GetChildrenException, \
    UpdateCollectionException, RemoveCollectionException, DeleteException, \
    NRNSAException, generate_error_message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Relationship(object):

    def __init__(self, poid=None, fdn=None, nodes=None):
        self.poid = poid
        self.fdn = fdn
        self.nodes = nodes


class CollectionUtils(object):

    def __init__(self):
        self.rest_services = RestService()
        self.sso = SsoManager()
        self.log = NRNSALogger()
        self.nrnsa_cli = NRNSACli()
        self.cli_error = False

    def get_children(self, parent_id):
        collections = {}
        endpoint = constants.CUSTOM_TOPOLOGY_V1
        if parent_id != '':
            endpoint = endpoint + '?parentId=' + str(parent_id)

        collection_response = self.rest_services.get(endpoint)
        collections = json.loads(collection_response.text)
        if collection_response.status_code != 200:
            message = generate_error_message(collections, endpoint)
            raise GetChildrenException(parent_id, message)

        return collections

    def get_custom_topology(self, name):
        endpoint = constants.CUSTOM_TOPOLOGY_V1 + '?customTopology=true'

        topology_response = self.rest_services.get(endpoint)

        topologies = json.loads(topology_response.text)
        if topology_response.status_code != 200:
            message = generate_error_message(topologies, endpoint)
            raise GetCollectionByNameException(name, message)

        collection = None
        for topology in topologies:
            if name in topology['name']:
                collection = topology
                break
        return collection

    def get_collection_by_id(self, collection_id):
        endpoint = constants.COLLECTIONS_V1 + '/' + str(collection_id)
        response = self.rest_services.get(endpoint)
        collection = json.loads(response.text)

        if response.status_code != 200:
            message = generate_error_message(collection, endpoint)
            raise GetCollectionByIdException(collection_id, message)

        return collection

    def get_collection_by_name(self, name):
        endpoint = constants.COLLECTIONS_V2 + '?collectionName=' + str(name)
        response = self.rest_services.get(endpoint)
        collection = json.loads(response.text)
        if response.status_code != 200:
            message = generate_error_message(collection, endpoint)
            raise GetCollectionByNameException(name, message)
        else:
            if 'collections' in collection and collection['collections']:
                collection = collection['collections'][0]
            else:
                collection = None

        return collection

    def create_leaf_collection(self, name, parent_id):
        endpoint = constants.CUSTOM_TOPOLOGY_V1 + "/" + str(parent_id)
        leaf_params = {
            'name': str(name),
            'type': 'LEAF',
            'category': 'Public',
            'isSystemCreated': 'true'
        }
        create_response = self.rest_services.post(endpoint, leaf_params)

        collection = json.loads(create_response.text)
        if create_response.status_code == 409:
            self.log.info("NR-NSA script failed to create " +
                          "collection, collection name {0} in use".format(
                              name))
            collection = self._handle_duplicate_collection(parent_id, name)

        elif create_response.status_code != 201:
            message = generate_error_message(collection, endpoint)
            raise CreateCollectionException(name, message)

        return collection

    def create_system_collection(self, name):
        endpoint = constants.COLLECTIONS_V3 + "?isSystemCreated=true"
        params = {
            'name': str(name),
            'category': 'Public',
            "userId": None
        }
        create_response = self.rest_services.post(endpoint, params)

        collection = json.loads(create_response.text)
        if create_response.status_code != 201:
            message = generate_error_message(collection, endpoint)
            raise CreateCollectionException(name, message)
#
        self.log.info("NR-NSA script: {0} collection created".format(name))
        return collection

    def _handle_duplicate_collection(self, parent_id, name):
        collection = self.get_collection_by_name(name)
        if collection:
            self.delete_collection(collection['id'])
            collection = self.create_leaf_collection(name, parent_id)
        else:
            raise NRNSAException("NR-NSA script unable to find "
                                 "collection {0}".format(name))
        return collection

    def create_topology(self, name):
        endpoint = constants.CUSTOM_TOPOLOGY_V1
        nrnsa_params = {
            'name': str(name),
            'isCustomTopology': 'true',
            'isSystemCreated': 'true'
        }

        create_response = self.rest_services.post(endpoint, nrnsa_params)
        create_response = json.loads(create_response.text)
        if "id" in create_response:
            self.log.info("NR-NSA script created {0} Topology".format(name))
        else:
            message = generate_error_message(create_response, endpoint)
            raise CreateTopologyException(name, message)

        return create_response

    def update_collection(self, collection_id, objects):
        endpoint = constants.COLLECTIONS_V1 + '/' + str(collection_id)
        objects = [{"id": "%s" % p} for p in objects]
        update_collection = self.rest_services.put(
            endpoint, {"objects": objects})
        update_response = json.loads(update_collection.text)
        if update_collection.status_code != 200:
            message = generate_error_message(update_response, endpoint)
            raise UpdateCollectionException(collection_id, message)
        return update_response

    def remove_collection(self, child_id, parent_id):
        endpoint = constants.CUSTOM_TOPOLOGY_V1 + "/" + str(child_id) + "/" \
                    + str(parent_id)
        self.log.debug(
            "NR-NSA script attempting to remove collection with id '%s' "
            "from topology" % child_id)

        response = self.rest_services.put(endpoint, {})
        if response.status_code != 200:
            response = json.loads(response.text)
            message = generate_error_message(response, endpoint)
            raise RemoveCollectionException(child_id, message)

    def delete_collection(self, collection_id):
        endpoint = constants.CUSTOM_TOPOLOGY_V1 + '/' + str(collection_id)
        delete_response = self.rest_services.delete(endpoint)
        if delete_response.status_code == 404:
            endpoint = constants.COLLECTIONS_V1 + '/' + str(collection_id)
            delete_response = self.rest_services.delete(endpoint)

        if delete_response.status_code not in [200, 204]:
            collection_deleted = json.loads(delete_response.text)
            message = generate_error_message(collection_deleted, endpoint)
            raise DeleteException(collection_id, message)
        else:
            self.log.info("NR-NSA script: collection deleted with the "
                          "given id {0}".format(collection_id))

    def delete_topology(self, topology_id):
        endpoint = constants.CUSTOM_TOPOLOGY_V1 + '/' + str(topology_id)
        if topology_id:
            delete_request = self.rest_services.delete(endpoint)
            if delete_request.status_code not in [200, 204]:
                response = json.loads(delete_request.text)
                message = generate_error_message(response, endpoint)
                raise DeleteException(topology_id, message)

    def execute_query(self, query):
        endpoint = constants.MO_SEARCH_V2 + '?query=' + query
        node_response = self.rest_services.get(endpoint)
        text = json.loads(node_response.text)
        if node_response.status_code != 200:
            message = generate_error_message(text, endpoint)
            raise ExecuteQueryException(query, message)

        node_response = [n['id']
                         for n in text.get('objects', [])]
        return node_response

    def get_node_names(self, nodes):
        endpoint = constants.MO_GET_POS_BY_POID
        node_list = CollectionUtils._get_node_list(nodes)
        name_to_poid_list = {}
        for batch in node_list:
            enodeb_response = self.rest_services.post(endpoint,
                                                      {"poList": batch})

            enodeb_details = json.loads(enodeb_response.text)
            if enodeb_response.status_code != 200:
                message = generate_error_message(enodeb_details, endpoint)
                raise GetNodeNamesException(message)

            for managed_object in enodeb_details:
                name_to_poid_list[managed_object['moName']] = \
                    managed_object['id']

        return name_to_poid_list

    @staticmethod
    def _split(list_to_split, number_of_splits):
        quotient, remainder = divmod(len(list_to_split), number_of_splits)
        return (
            list_to_split[i * quotient + min(i, remainder):
                          (i + 1) * quotient + min(i + 1, remainder)]
            for i in xrange(number_of_splits)
        )

    @staticmethod
    def _get_node_list(node_list):
        if len(list(node_list)) > 250:
            return CollectionUtils._split(
                node_list, (int(len(node_list) / 125)))
        return [node_list]

    def delete_cookie(self):
        """ Script Should remove the Cookie.txt file when completed.
        """
        path = self.sso.src_file_path
        if not os.stat(path + "/cookie.txt").st_size == 0:
            open(path + "/cookie.txt", 'w').close()

    def get_relations_via_cli(self, name_to_poid_list):
        relationships = self.nrnsa_cli.get_relationships(name_to_poid_list)
        self.cli_error = self.nrnsa_cli.cli_error
        return relationships
