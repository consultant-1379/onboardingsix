import requests
from mock import MagicMock
from mock import patch
from requests.models import Response
from common.network_utils import NetworkUtils
from common.nrnsa_exception import NRNSAException
from common.log import NRNSALogger
from base import BaseTest


class TESTNetworkUtils(BaseTest):


    def test_get_hostname_from_properties(self):
        expected_hostname = 'enmapache.athtem.eei.ericsson.se'
        with patch("common.network_utils.NetworkUtils.get_hostname_from_properties", return_value=expected_hostname) as get_hostname_properties_mock:
            actual_hostname = NetworkUtils.get_enm_hostname(NetworkUtils())
            assert get_hostname_properties_mock.call_count == 1
            self.assertEquals(expected_hostname, actual_hostname)

    def test_get_hostname_from_hosts(self):
        expected_hostname = 'enmapache.athtem.eei.ericsson.se'
        with patch("common.network_utils.NetworkUtils.get_hostname_from_properties", return_value=None) as get_hostname_properties_mock:
            with patch("common.network_utils.NetworkUtils.get_hostname_from_hosts", return_value=expected_hostname) as get_hostname_hosts_mock:

                get_hostname_hosts_mock.return_value = expected_hostname
                actual_hostname = NetworkUtils.get_enm_hostname(NetworkUtils())

                assert get_hostname_hosts_mock.call_count == 1
                self.assertEquals(expected_hostname, actual_hostname)

                msgs = NRNSALogger.logger.handlers[0].messages
                self.assertIn('Unable to retrieve host name from \'properties\' file. '
                              'Attempting to retrieve from \'hosts\' file',
                              msgs['info'])

    def test_get_hostname_cloud(self):
        with patch("common.network_utils.NetworkUtils.get_hostname_from_properties", return_value=None) as get_hostname_properties_mock:
            with patch("common.network_utils.NetworkUtils.get_hostname_from_hosts", return_value=None) as get_hostname_hosts_mock:

                expected_hostname = 'ieatenmc3b05-6.athtem.eei.ericsson.se'

                the_response = MagicMock(return_value=Response)
                the_response.text = expected_hostname
                requests.get = MagicMock(return_value=the_response)
                actual_hostname = NetworkUtils.get_enm_hostname(NetworkUtils())

                self.assertEquals(expected_hostname, actual_hostname)

                msgs = NRNSALogger.logger.handlers[0].messages
                self.assertIn('Unable to retrieve host name from \'properties\' file. '
                              'Attempting to retrieve from \'hosts\' file',
                              msgs['info'])
                self.assertIn('Unable to retrieve host name from \'hosts\' file. '
                              'Attempting to retrieve with Service Registry REST call',
                              msgs['info'])

    def test_unable_to_get_hostname(self):
        with patch("common.network_utils.NetworkUtils.get_hostname_from_properties", return_value=None) as get_hostname_properties_mock:
            with patch("common.network_utils.NetworkUtils.get_hostname_from_hosts", return_value=None) as get_hostname_hosts_mock:

                requests.get = MagicMock(
                    side_effect=requests.exceptions.ConnectionError)

                self.assertRaises(
                    NRNSAException, NetworkUtils.get_enm_hostname, NetworkUtils())
                msgs = NRNSALogger.logger.handlers[0].messages
                self.assertIn('Unable to retrieve host name from \'properties\' file. '
                              'Attempting to retrieve from \'hosts\' file',
                              msgs['info'])
                self.assertIn('Unable to retrieve host name from \'hosts\' file. '
                              'Attempting to retrieve with Service Registry REST call',
                              msgs['info'])
