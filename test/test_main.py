from mock import MagicMock
from mock import patch

from common.nrnsa_exception import NRNSAException
from common.log import NRNSALogger

from main import Main
from base import BaseTest


class TestMain(BaseTest):

    @patch('topologies.system_collections.system_collection_creator'
           '.SystemCollectionCreator')
    @patch('topologies.system_topologies.nrnsa_topology'
           '.NrnsaTopology')
    def test_execute_topology(self, mock_run1, mock_run2):
        mock_run1.start = MagicMock(return_value=None)
        Main.execute_topology()
        assert mock_run1.call_count == 1
        assert mock_run2.call_count == 3

    @patch('topologies.system_collections.system_collection_creator'
           '.SystemCollectionCreator')
    @patch('topologies.system_topologies.nrnsa_topology'
           '.NrnsaTopology.__init__', return_value=None)
    @patch('topologies.system_topologies.nrnsa_topology'
           '.NrnsaTopology.start')
    def test_execute_topology(self, mock_run1, mock_init, mock_run2):
        mock_run1.side_effect = self.raise_exception
        Main.execute_topology()
        msg = NRNSALogger.logger.handlers[0].messages
        assert mock_run1.call_count == 1
        assert mock_run2.call_count == 3
        self.assertIn('Some error occurred', msg['error'])

    def raise_exception(self):
        raise NRNSAException('Some error occurred')
