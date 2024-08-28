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
from __future__ import print_function
from common.nrnsa_exception import NRNSAException, NRNSAExportException
from common.collection_utils import CollectionUtils
from common.nrnsa_export_utils import NRNSAExportUtils
from common.log import NRNSALogger


class SystemTopologyCreator(object):

    def __init__(self, topology_id):
        self.topology_id = topology_id
        self.collection_utils = CollectionUtils()
        self.log = NRNSALogger()
        self.export_utils = NRNSAExportUtils()
        self.completed_without_errors = True

    def process_relationships(self, relationships, suffix):
        try:
            collections = self.collection_utils.get_children(
                self.topology_id)
            collection_list = {}
            for instance in collections:
                collection_id = instance['id']
                collection = self.collection_utils.get_collection_by_id(
                    collection_id)
                collection_name = collection["name"]
                collection_list[collection_name] = {"collection": collection}

            for enodeb in relationships:
                collection_name = str(enodeb.fdn + suffix) if suffix \
                    else str(enodeb.fdn)

                if (not collection_list or
                        collection_name not in collection_list):
                    self._handle_new_collection(enodeb.nodes,
                                                self.topology_id,
                                                collection_name)
                else:
                    self._handle_collection_by_owner(
                        collection_list, collection_name,
                        enodeb.nodes)
            self._handle_remaining_collections(collection_list)
            collections = self.collection_utils.get_children(
                self.topology_id)

            if not collections:
                self.delete_topology()
            if not self.completed_without_errors:
                print("NR-NSA Systems Topology has been processed with "
                      "warnings, check the logs at /opt/ericsson/"
                      "nr-nsa-systems-topology/log/nrnsa_log "
                      "for more details")
            else:
                print("NR-NSA Systems Topology has been "
                      "processed successfully")
                self.log.info(
                    "NR-NSA Topology has been processed successfully")
                try:
                    self.export_utils.start(self.topology_id)
                except NRNSAExportException as exc:
                    self.log.warn(str(exc))
                    completed_message = \
                        "NR-NSA Topology updated successfully " + \
                        "but a failure occurred while trying to export"
                    print(completed_message)

        except NRNSAException as error:
            self.log.exception(error)
            print('NR-NSA Topology has failed to process relationships, '
                  'check the logs at /opt/ericsson/nr-nsa-systems-topology/'
                  'log/nrnsa_log for more details')
            self.delete_topology()

    def _handle_new_collection(self, objects, parent_id, collection_name):
        try:
            collection = self.collection_utils.create_leaf_collection(
                collection_name, parent_id)
            collection_id = collection['id']
            self.collection_utils.update_collection(collection_id, objects)
        except NRNSAException as exc:
            self.completed_without_errors = False
            self.log.warn(exc)

    def _handle_collection_by_owner(self, collection_list,
                                    collection_name, objects):
        collection = collection_list[collection_name]
        collection_category = collection['collection'][
            'category']
        if "userId" not in collection["collection"]:
            self._handle_existing_collection(
                objects, collection)
            collection_list.pop(collection_name)
        elif collection_category.lower() == "public":
            try:
                self.collection_utils.delete_collection(
                    collection['collection']['id'])
                self.log.info("NR-NSA script deleted duplicate user "
                              "added collection '%s'" %
                              collection['collection']['name'])
                self._handle_new_collection(objects, self.topology_id,
                                            collection_name)
            except NRNSAException as exc:
                self.completed_without_errors = False
                self.log.warn(exc)

    def _handle_existing_collection(self, poid_list, collection):
        existing_poids = [int(i['id'])
                          for i in collection['collection']['objects']]
        new_poids = [int(poid) for poid in poid_list]

        existing_poids.sort(key=int)
        new_poids.sort(key=int)
        collection_name = str(collection['collection']['name'])
        if hash(tuple(existing_poids)) == hash(tuple(new_poids)):
            self.log.info("NR-NSA script no update to the collection: {0} "
                          "".format(collection_name))
        else:
            collection_id = collection['collection']['id']
            try:
                self.collection_utils.update_collection(collection_id,
                                                        new_poids)
                self.log.info(
                    "NR-NSA script updated collection: '%s'" % collection_name)
            except NRNSAException as exc:
                self.completed_without_errors = False
                self.log.warn(exc)

    def _handle_remaining_collections(self, collections):
        for _, value in collections.iteritems():
            if "userId" not in value["collection"]:
                try:
                    self.collection_utils.delete_collection(
                        value['collection']['id'])
                    self.log.info("NR-NSA script deleted collection: '%s' " %
                                  value['collection']['name'])
                except NRNSAException as exc:
                    self.completed_without_errors = False
                    self.log.warn(exc)
            else:
                try:
                    self.collection_utils.remove_collection(
                        value['collection']['id'], self.topology_id)
                    self.log.info("NR-NSA script removed user "
                                  "added Collection '%s'" %
                                  value['collection']['name'])
                except NRNSAException as exc:
                    self.completed_without_errors = False
                    self.log.warn("NR-NSA script failed to remove user "
                                  "added Collection '%s'" %
                                  value['collection']['name'])

    def delete_topology(self):
        """ Invalid Conditions for NR-NSA, the topology_id
            and collections will be removed.
        """
        if self.topology_id:
            try:
                collections = self.collection_utils.get_children(
                    self.topology_id)
                for instance in collections:
                    collection_id = instance['id']
                    self.collection_utils.delete_collection(collection_id)
                self.collection_utils.delete_topology(self.topology_id)
                self.log.info(
                    "NR-NSA Systems Topology and Collections deleted "
                    "successfully")
            except NRNSAException as exc:
                self.log.warn("NR-NSA failed to delete NR-NSA topology, "
                              "Cause: {0}".format(str(exc)))
        else:
            self.log.info("No Topology to be deleted")
        self.export_utils.delete()
