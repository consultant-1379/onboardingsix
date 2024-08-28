import os
import requests
from requests.models import Response
from mock import MagicMock
from base import BaseTest

from common import constants
from common.sso_manager import SsoManager


class TestSSOManager(BaseTest):

    def setUp(self):
        super(TestSSOManager, self).setUp()
        self.session_token_dir = os.path.expanduser('~' + 'Username')
        self.session_token_file = os.path.join(self.session_token_dir, '.enm_login')
        if not os.path.exists(self.session_token_dir):
            os.mkdir(self.session_token_dir)
        open(self.session_token_file, 'w').close()

    def tearDown(self):
        os.remove(self.session_token_file)
        os.rmdir(self.session_token_dir)

    def test_generate_cookie(self):
        the_response = MagicMock(return_value=Response)
        the_response.status_code = 302
        cookie_session = requests.Session()
        cookie_session.cookies["iPlanetDirectoryPro"] = "ValidCookie"
        the_response.cookies = cookie_session.cookies
        session = requests.Session()
        requests.session = MagicMock(return_value=session)
        session.post = MagicMock(return_value=the_response)

        SsoManager().create_cookie('https://testUrl.com', 'Username',
                                    'Password')
        result = SsoManager().get_cookie()
        self.assertEquals(result, the_response.cookies)
        open(SsoManager().src_file_path + '/cookie.txt', 'w').close()

    def test_generate_invalid_user(self):
        the_response = MagicMock(return_value=Response)
        the_response.status_code = 401
        session = requests.Session()
        requests.session = MagicMock(return_value=session)
        session.post = MagicMock(return_value=the_response)

        self.assertFalse(
            SsoManager().create_cookie('https://testUrl.com', 'Username',
                                        'Password'))

    def test_store_cookie_to_file(self):
        cookie_session = requests.Session()
        cookie_session.cookies["iPlanetDirectoryPro"] = "ValidCookie"
        SsoManager()._store_cookie_to_file(cookie_session.cookies)
        assert os.stat(
            SsoManager().src_file_path + "/cookie.txt").st_size != 0
        open(SsoManager().src_file_path + '/cookie.txt', 'w').close()

    def test_store_session_token(self):
        cookie_session = requests.Session()
        cookie_session.cookies["iPlanetDirectoryPro"] = "ValidCookie"
        SsoManager()._store_session_token(cookie_session.cookies, 'Username')
        assert os.stat(
            self.session_token_file).st_size != 0
        open(self.session_token_file, 'w').close()

    def test_config_manager(self):
        self.assertEquals(constants.LOGIN_ENDPOINT, '/login')
        self.assertEquals(constants.LOGOUT_ENDPOINT, '/logout')
        self.assertEquals(constants.MO_SEARCH_V2, '/managedObjects/search/v2')
        self.assertEquals(constants.MO_GET_POS_BY_POID,
                          '/managedObjects/getPosByPoIds')
        self.assertEquals(constants.CUSTOM_TOPOLOGY_V1,
                          '/object-configuration/custom-topology/v1')
        self.assertEquals(constants.COLLECTIONS_V3,
                          '/object-configuration/collections/v3')
        self.assertEquals(constants.COLLECTIONS_V2,
                          '/object-configuration/collections/v2')
        self.assertEquals(constants.COLLECTIONS_V1,
                          '/object-configuration/v1/collections')
        self.assertEquals(constants.NETEX_IMPORT_EXPORT_V1,
                          '/network-explorer-import/v1/collection/export')
        self.assertEquals(constants.PROPERTIES_FILE_PATH,
                          '/ericsson/tor/data/global.properties')
        self.assertEquals(constants.TOPOLOGY_RELATIONSHIPS_V1,
                          '/topology-relationship-service/rest/' \
                          'v1/relation/getRelations')
        self.assertEquals(constants.SERVICE_REGISTRY_URL,
                          'http://serviceregistry:8500/v1/kv/enm/deprecated/' \
                          'global_properties/web_host_default?raw')
        self.assertEquals(constants.EXPORT_ROOT_DIRECTORY,
                          '/ericsson/tor/no_rollback/nr-nsa-systems-topology')
        self.assertEquals(constants.EXPORT_NRNSA_DIRECTORY, 'export')
        self.assertEquals(constants.EXPORT_DESTINATION_FILE,
                          'NR-NSA_export.zip')
        self.assertEquals(constants.CLI_GET_RADIO_NODE_ATTRIBUTES,
                          'cmedit get * ENodeBFunction.(enbid, ' \
                          'enodebplmnid) -ns=lrat')
        self.assertEquals(constants.CLI_GET_NR_RADIO_NODE_ATTRIBUTES,
                          'cmedit get * ExternalENodeBFunction.(' \
                          'enodebid, enbplmnid) ' \
                          '-neType=RadioNode')
        self.assertEquals(constants.CLI_GET_NR_RADIO_NODE_ATTRIBUTES_PLMNID,
                          'cmedit get * ExternalENodeBFunction.(' \
                          'enodebid, pLMNId) ' \
                          '-neType=RadioNode')
