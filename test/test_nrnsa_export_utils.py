import unittest
import requests
import json
import shutil
from mock import MagicMock
from mock import patch
from mock import mock_open
from requests.models import Response
from common import constants
from common.log import NRNSALogger
from common.nrnsa_export_utils import NRNSAExportUtils
from common.nrnsa_exception import NRNSAExportException


class MOCKRequestsResponse():
    def __init__(self, response_details):
        self.response_details = response_details
        self.response_index = -1

    def response(self, *args, **kwargs):
        if len(self.response_details)-1 != self.response_index:
            self.response_index += 1

        response = MagicMock(return_value=Response)
        response.text = self.response_details[self.response_index]["text"]
        response.status_code = self.response_details[self.response_index]["statusCode"]

        return response


class ExportServerResponse():
    def __init__(self, status_response_list):
        self.post_response_mock = MOCKRequestsResponse([
            {
                "text": json.dumps({
                    "sessionId": "1234-1234-1234"
                }),
                "statusCode": 202
            }
        ])
        requests.post = MagicMock(wraps=self.post_response_mock.response)

        get_response_list = []
        for request in status_response_list:
            get_response_list.append(ExportServerResponse.status_message(request))

        get_response_list = get_response_list + [
            {
                "text": "bodyOfExport",
                "statusCode": 200
            }
        ]
        self.get_response_mock = MOCKRequestsResponse(get_response_list)
        requests.get = MagicMock(wraps=self.get_response_mock.response)

    @staticmethod
    def status_message(status):
        return {
            "text": json.dumps({
                "status": status
            }),
            "statusCode": 200
        }

class MockException():
    @staticmethod
    def raise_os_error(*args, **kwargs):
        raise OSError("Exception message")

    @staticmethod
    def raise_io_error(*args, **kwargs):
        raise IOError("Exception message")


class TESTNRNSAExportUtils(unittest.TestCase):
    exportFile = "/ericsson/tor/no_rollback/nr-nsa-systems-topology/export/NR-NSA_export.zip"

    @classmethod
    def setUp(cls):
        with patch("common.sso_manager.SsoManager.get_cookie",
                   return_value="cookie_test"):
            with patch("common.network_utils.NetworkUtils.get_enm_hostname",
                       return_value="localhost"):
                cls.export_utils = NRNSAExportUtils()

    def test_export_complete_with_success(self):
        exportServerResponse = ExportServerResponse(["IN_PROGRESS", "IN_PROGRESS", "COMPLETED_WITH_SUCCESS"])

        with patch("common.nrnsa_export_utils.NRNSAExportUtils._create_target_destination",
                   return_value="./test_export.zip") as create_target_destination_mock:
            self.export_utils.start("12345")

            self.assertTrue(create_target_destination_mock.called)

    def test_export_complete_with_error(self):
        exportServerResponse = ExportServerResponse(["IN_PROGRESS", "COMPLETED_WITH_ERRORS"])

        with patch("common.nrnsa_export_utils.NRNSAExportUtils._create_target_destination",
                   return_value="./test_export.zip") as create_target_destination_mock:
            self.export_utils.start("12345")

            self.assertTrue(create_target_destination_mock.called)

    def test_export_failed(self):
        exportServerResponse = ExportServerResponse(["IN_PROGRESS", "FAILED"])

        with patch("common.nrnsa_export_utils.NRNSAExportUtils._create_target_destination",
                   return_value="./test_export.zip") as create_target_destination_mock:
            try:
                self.export_utils.start("12345")
                self.assertTrue(False)
            except NRNSAExportException as err:
                self.assertEquals("NR-NSA export: Server error", str(err))

        self.assertTrue(create_target_destination_mock.called)

    def test_export_fail_get_status(self):
        post_response_mock = MOCKRequestsResponse([
            {
                "text": json.dumps({
                    "sessionId": "1234-1234-1234"
                }),
                "statusCode": 202
            }
        ])
        requests.post = MagicMock(wraps=post_response_mock.response)

        get_response_mock = MOCKRequestsResponse([
            {
                "text": json.dumps({
                    "status": "IN_PROGRESS"
                }),
                "statusCode": 200
            },{
                "text": "",
                "statusCode": 400
            },{
                "text": "",
                "statusCode": 400
            },{
                "text": "",
                "statusCode": 400
            }
        ])
        requests.get = MagicMock(wraps = get_response_mock.response)

        with patch("common.nrnsa_export_utils.NRNSAExportUtils._create_target_destination",
                   return_value="./test_export.zip") as create_target_destination_mock:
            try:
                self.export_utils.start("12345")
                self.assertTrue(False)
            except NRNSAExportException as err:
                self.assertEquals(
                    "NR-NSA export: Maximum number of status request attempts exceeded, aborting execution",
                    str(err))
        self.assertTrue(create_target_destination_mock.called)

    def test_export_requests_exceeded(self):
        post_response_mock = MOCKRequestsResponse([
            {
                "text": json.dumps({
                    "sessionId": "1234-1234-1234"
                }),
                "statusCode": 202
            }
        ])
        requests.post = MagicMock(wraps = post_response_mock.response)

        get_response_mock = MOCKRequestsResponse([
            {
                "text": json.dumps({
                    "status": "IN_PROGRESS"
                }),
                "statusCode": 200
            }
        ])
        requests.get = MagicMock(wraps=get_response_mock.response)

        with patch("time.sleep", return_value=None):
            with patch("common.nrnsa_export_utils.NRNSAExportUtils._create_target_destination",
                       return_value="./test_export.zip") as create_target_destination_mock:
                try:
                    self.export_utils.start("12345")
                    self.assertTrue(False)
                except NRNSAExportException as err:
                    self.assertEquals("NR-NSA export: Maximum execution time reached, aborting execution", str(err))
            self.assertTrue(create_target_destination_mock.called)

    def test_export_start_fail(self):
        post_response_mock = MOCKRequestsResponse([
            {
                "text": json.dumps({
                    "internalErrorCode": 10019,
                    "userMessage": {
                        "title": "Access Forbidden",
                        "body": "No user information was provided!"
                    }
                }),
                "statusCode": 401
            }
        ])
        requests.post = MagicMock(wraps = post_response_mock.response)

        with patch("common.nrnsa_export_utils.NRNSAExportUtils._create_target_destination",
                   return_value="./test_export.zip") as create_target_destination_mock:
            try:
                self.export_utils.start("12345")
                self.assertTrue(False)
            except NRNSAExportException as err:
                self.assertEquals("NR-NSA export: Received server error Access Forbidden, No user information was provided!", str(err))
        self.assertTrue(create_target_destination_mock.called)

    def test_download_exported_collections_failure(self):
        with patch("common.nrnsa_export_utils.NRNSAExportUtils.delete", return_value=None) as delete_mock:
            with patch("requests.get", return_value={}) as requests_get_mock:
                with patch("__builtin__.open", wraps=MockException().raise_os_error) as open_mock:
                    try:
                        self.export_utils._download_exported_collections("SessionId", "/NotWritingFile.zip")
                        self.assertTrue(False)
                    except NRNSAExportException as err:
                        self.assertEquals("NR-NSA export: Can not write file /NotWritingFile.zip, exception: Exception message", str(err))

                    self.assertEquals(requests_get_mock.call_count, 1)
                    self.assertEquals(delete_mock.call_count, 1)
                    self.assertEquals(open_mock.call_count, 1)

    def test_download_exported_collections_permission_failure(self):
        class Response_Mock:
            def iter_content(self, chunk_size):
                return []

        response_mock = Response_Mock()
        with patch("common.log.NRNSALogger.error", return_value=None) as logError_mock:
            with patch("common.nrnsa_export_utils.NRNSAExportUtils.delete", return_value=None) as delete_mock:
                with patch("requests.get", return_value=response_mock) as requests_get_mock:
                    with patch('__builtin__.open', mock_open(), create=True) as open_mock:
                        with patch("os.chmod", wraps=MockException().raise_io_error) as chmod_mock:
                            self.export_utils._download_exported_collections("SessionId", "./NotPermissionFile.zip")

                            self.assertEquals(requests_get_mock.call_count, 1)
                            self.assertEquals(delete_mock.call_count, 1)
                            self.assertEquals(chmod_mock.call_count, 1)
                            logError_mock.assert_called_with(
                                "NR-NSA export: Can not change permission to file ./NotPermissionFile.zip, exception: Exception message")

    def test_create_target_destination_all_already_present(self):
        with patch("os.path.isdir", return_value=True) as isdir_mock:
            result = NRNSAExportUtils._create_target_destination()

            self.assertEquals(isdir_mock.call_count, 2)
            self.assertEquals(self.exportFile, result)

    @patch('os.path.isdir', return_value=False)
    def test_create_target_destination_root_not_present(self, mock_isdir):
        try:
            NRNSAExportUtils._create_target_destination()
        except NRNSAExportException as err:
            self.assertEquals("NR-NSA export: Target destination directory does not exist", str(err))

    def test_create_target_destination_makedirs_failure(self):
        with patch("os.path.isdir", side_effect = [True, False]) as isdir_mock:
            with patch("os.makedirs", wraps=MockException().raise_os_error) as makedirs_mock:
                try:
                    NRNSAExportUtils._create_target_destination()
                    self.assertTrue(False)
                except NRNSAExportException as err:
                    self.assertEquals("NR-NSA export: Create export: failure", str(err))

                self.assertEquals(isdir_mock.call_count, 2)
                self.assertEquals(makedirs_mock.call_count, 1)

    def test_create_target_destination_create_nsnra_directory(self):
        with patch("os.path.isdir", side_effect = [True, False]) as isdir_mock:
            with patch("os.makedirs", return_value=None) as makedirs_mock:
                result = NRNSAExportUtils._create_target_destination()

                self.assertEquals(isdir_mock.call_count, 2)
                self.assertTrue(makedirs_mock.called)
                makedirs_mock.assert_called_with('/ericsson/tor/no_rollback/nr-nsa-systems-topology/export')
                self.assertEquals("/ericsson/tor/no_rollback/nr-nsa-systems-topology/export/NR-NSA_export.zip", result)

    def test_delete_when_file_present(self):
        with patch("os.path.isfile", return_value=True) as isfile_mock:
            with patch("os.remove", return_value=None) as remove_mock:
                self.export_utils.delete()

                self.assertEquals(isfile_mock.call_count, 1)
                self.assertEquals(remove_mock.call_count, 1)
                remove_mock.assert_called_with(self.exportFile)

    def test_delete_when_file_not_present(self):
        with patch("os.path.isfile", return_value=False) as isfile_mock:
            with patch("os.remove", return_value=None) as remove_mock:
                self.export_utils.delete()

                self.assertEquals(isfile_mock.call_count, 1)
                self.assertEquals(remove_mock.call_count, 0)

    def test_delete_when_file_not_deleting(self):
        with patch("common.log.NRNSALogger.info", return_value=None) as logInfo_mock:
            with patch("os.path.isfile", return_value=True) as isfile_mock:
                with patch("os.remove", wraps=MockException().raise_os_error) as remove_mock:
                    self.export_utils.delete()

                    self.assertEquals(isfile_mock.call_count, 1)
                    self.assertEquals(remove_mock.call_count, 1)
                    logInfo_mock.assert_called_with(
                        "NR-NSA: Can not delete file "+ self.exportFile +
                        ", exception: Exception message")

    def test_config(self):
        self.assertEquals(constants.NETEX_IMPORT_EXPORT_V1, '/network-explorer-import/v1/collection/export')
