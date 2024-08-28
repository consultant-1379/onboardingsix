import unittest

from mock import MagicMock
from mocked_data import MockedData as mocked_data

from common.log import NRNSALogger
from common.network_utils import NetworkUtils
from common.sso_manager import SsoManager

from utils import MockLoggingHandler


class BaseTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)
        NRNSALogger.create_handlers = MagicMock()
        NRNSALogger.setup_log()
        NRNSALogger.logger.handlers = [MockLoggingHandler()]
        NRNSALogger.logger.handlers[0].reset()
        self.setUp()

    def setUp(self):
        NRNSALogger.logger.handlers[0].reset()
        SsoManager.get_cookie = MagicMock(
                return_value=mocked_data().get_mocked_cookie())
        NetworkUtils.get_hostname_from_hosts = MagicMock(
            return_value='enmapache.athtem.eei.ericsson.se')
        NetworkUtils.get_hostname_from_properties = MagicMock(
                return_value='enmapache.athtem.eei.ericsson.se')

    def assertIn(self, expected, text, msg=""):
        self.assertTrue(expected in text,
                        '"%s" not in "%s". %s' % (expected, text, msg))

    def assertNotIn(self, expected, text, msg=""):
        self.assertTrue(expected not in text,
                        '"%s" in "%s". %s' % (expected, text, msg))
