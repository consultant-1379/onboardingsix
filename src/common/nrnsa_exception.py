#!/usr/bin/env python
####################################################################
# COPYRIGHT Ericsson AB 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
####################################################################


class NRNSAException(Exception):
    pass


class NRNSAExportException(Exception):
    def __str__(self):
        return "NR-NSA export: " + Exception.__str__(self)


class ExecuteQueryException(NRNSAException):
    def __init__(self, query, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to run query: {"
                                      "0}, cause: {1}".format(query, cause))


class CreateCollectionException(NRNSAException):
    def __init__(self, name, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to create "
                                      "collection with name: {0}, cause:"
                                      " {1}".format(name, cause))


class CreateTopologyException(NRNSAException):
    def __init__(self, name, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to create {0} "
                                      "Topology, cause: {1}".format(name,
                                                                    cause))


class CMEditException(NRNSAException):
    def __init__(self, query, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to parse cm "
                                      "edit output for query '{0}', cause: "
                                      "{1}".format(query, cause))


class GetNodeNamesException(NRNSAException):
    def __init__(self, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to get node names,"
                                      " cause: {0}".format(cause))


class GetCollectionByNameException(NRNSAException):
    def __init__(self, name, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to get collection "
                                      "with name: {0}, cause: "
                                      "{1}".format(name, cause))


class GetCollectionByIdException(NRNSAException):
    def __init__(self, collection_id, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to get collection "
                                      "by id: {0}, cause: "
                                      "{1}".format(collection_id, cause))


class GetChildrenException(NRNSAException):
    def __init__(self, parent_id, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to get children "
                                      "for parentId: {0}, cause: "
                                      "{1}".format(parent_id, cause))


class UpdateCollectionException(NRNSAException):
    def __init__(self, collection_id, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to update "
                                      "collection with id: {0}, cause: {"
                                      "1}".format(collection_id, cause))


class RemoveCollectionException(NRNSAException):
    def __init__(self, collection_id, cause):
        NRNSAException.__init__(self, "NR-NSA script failed to remove "
                                      "collection with id: {0} from NR-NSA "
                                      "topology, cause: "
                                      "{1}".format(collection_id, cause))


class DeleteException(NRNSAException):
    def __init__(self, collection_id, cause):
        NRNSAException.__init__(self, "NR-NSA script Delete Action Failed, "
                                      "collection id: {0}, cause: "
                                      "{1}".format(collection_id, cause))


def generate_error_message(response_message, endpoint):
    if 'userMessage' in response_message:
        message = response_message['userMessage']
        if 'body' in message:
            return message['body']
        elif 'title' in message:
            return message['title']
    elif 'title' in response_message:
        return response_message['title']
    return 'Error occurred while executing the REST service. ' + \
           endpoint
