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
LOGIN_ENDPOINT = '/login'
LOGOUT_ENDPOINT = '/logout'

MO_SEARCH_V2 = '/managedObjects/search/v2'
MO_GET_POS_BY_POID = '/managedObjects/getPosByPoIds'
CUSTOM_TOPOLOGY_V1 = '/object-configuration/custom-topology/v1'
COLLECTIONS_V3 = '/object-configuration/collections/v3'
COLLECTIONS_V2 = '/object-configuration/collections/v2'
COLLECTIONS_V1 = '/object-configuration/v1/collections'
NETEX_IMPORT_EXPORT_V1 = '/network-explorer-import/v1/collection/export'
PROPERTIES_FILE_PATH = '/ericsson/tor/data/global.properties'

TOPOLOGY_RELATIONSHIPS_V1 = '/topology-relationship-service/rest/' \
                                        'v1/relation/getRelations'
SERVICE_REGISTRY_URL = 'http://serviceregistry:8500/v1/kv/enm/deprecated/' \
                       'global_properties/web_host_default?raw'
EXPORT_ROOT_DIRECTORY = "/ericsson/tor/no_rollback/nr-nsa-systems-topology"
EXPORT_NRNSA_DIRECTORY = "export"
EXPORT_DESTINATION_FILE = "NR-NSA_export.zip"

CLI_GET_RADIO_NODE_ATTRIBUTES = 'cmedit get * ENodeBFunction.(enbid, ' \
                                'enodebplmnid) -ns=lrat'

# Changing back to -neType due to blacklist TORF-416490
CLI_GET_NR_RADIO_NODE_ATTRIBUTES = 'cmedit get * ' \
                                   'ExternalENodeBFunction.(' \
                                   'enodebid, enbplmnid) ' \
                                   '-neType=RadioNode'
CLI_GET_NR_RADIO_NODE_ATTRIBUTES_PLMNID = 'cmedit get * ' \
                                          'ExternalENodeBFunction.(' \
                                          'enodebid, pLMNId) ' \
                                          '-neType=RadioNode'
