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
from __future__ import print_function
import os
import os.path
import json
import time
import requests
import common.constants as constants

from common.network_utils import NetworkUtils
from common.log import NRNSALogger
from common.sso_manager import SsoManager
from common.nrnsa_exception import NRNSAExportException


class NRNSAExportUtils(object):

    def __init__(self):
        self.log = NRNSALogger()
        sso = SsoManager()
        self.url = 'https://' + \
                   str(NetworkUtils.get_enm_hostname(NetworkUtils()))
        self.headers = {"content-type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                        "X-Tor-Application": "networkexplorer"}
        self.cookie = sso.get_cookie()

    def start(self, collection_id):
        self.log.info(
            "NR-NSA export: start collection export " +
            collection_id)

        destination = NRNSAExportUtils._create_target_destination()
        session_id = self._export_request(collection_id)
        self._waiting_export_end(session_id)
        self._download_exported_collections(session_id, destination)
        print("NR-NSA export Completed")
        self.log.info("NR-NSA export Completed")

    def _export_request(self, collection_id):
        try:
            response = requests.post(
                self.url + constants.NETEX_IMPORT_EXPORT_V1 +
                '/nested',
                data=json.dumps({"collections": [collection_id]}),
                cookies=self.cookie,
                headers=self.headers,
                verify=False)

        except requests.exceptions.ConnectionError:
            raise NRNSAExportException("Request to Server failure")

        if response.status_code != 202:
            error_message = json.loads(response.text)
            raise NRNSAExportException(
                "Received server error " +
                error_message["userMessage"]["title"] + ", " +
                error_message["userMessage"]["body"])

        return json.loads(response.text)["sessionId"]

    def _waiting_export_end(self, session_id):
        retry = 720
        while retry:
            time.sleep(5)
            response = self._get_export_status(session_id)
            if response in ["COMPLETED_WITH_SUCCESS", "COMPLETED_WITH_ERRORS"]:
                return

            if response == "FAILED":
                raise NRNSAExportException("Server error")

            if response == "ABORTED":
                raise NRNSAExportException("Request cancelled by user")

            retry -= 1

        raise NRNSAExportException(
            "Maximum execution time reached, aborting execution")

    def _get_export_status(self, session_id):
        retry = 3

        while retry:
            try:
                response = requests.get(
                    self.url + constants.NETEX_IMPORT_EXPORT_V1 +
                    '/status/' + session_id,
                    cookies=self.cookie,
                    headers=self.headers,
                    verify=False
                )
            except requests.exceptions.ConnectionError:
                self.log.info("NR-NSA export: status request fails")

            if response.status_code == 200:
                return json.loads(response.text)["status"]

            retry -= 1
            time.sleep(5)

        raise NRNSAExportException(
            "Maximum number of status request " +
            "attempts exceeded, aborting execution")

    def _download_exported_collections(self, session_id, destination):
        try:
            response = requests.get(
                self.url + constants.NETEX_IMPORT_EXPORT_V1 +
                '/download/' + session_id,
                cookies=self.cookie,
                headers=self.headers,
                verify=False,
                stream=True
            )
        except requests.exceptions.ConnectionError:
            raise NRNSAExportException('Unable to retrieve host name')

        self.delete()
        try:
            with open(destination, 'wb') as open_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        open_file.write(chunk)
        except (IOError, Exception) as exc:
            raise NRNSAExportException(
                "Can not write file " +
                destination + ", exception: " + str(exc))
        try:
            os.chmod(destination, 0o777)
        except IOError as exc:
            self.log.error(
                "NR-NSA export: Can not change permission to file " +
                destination + ", exception: " + str(exc))

    @staticmethod
    def _create_target_destination():
        if not os.path.isdir(constants.EXPORT_ROOT_DIRECTORY):
            raise NRNSAExportException(
                "Target destination directory does not exist")

        destination_path = os.path.join(
            constants.EXPORT_ROOT_DIRECTORY,
            constants.EXPORT_NRNSA_DIRECTORY)

        if not os.path.isdir(destination_path):
            try:
                os.makedirs(destination_path)
            except OSError:
                raise NRNSAExportException("Create " +
                                           constants.EXPORT_NRNSA_DIRECTORY +
                                           ": failure")

        return os.path.join(
            destination_path,
            constants.EXPORT_DESTINATION_FILE)

    def delete(self):
        export_file = os.path.join(
            constants.EXPORT_ROOT_DIRECTORY,
            constants.EXPORT_NRNSA_DIRECTORY,
            constants.EXPORT_DESTINATION_FILE)

        if os.path.isfile(export_file):
            try:
                os.remove(export_file)
                self.log.info("NR-NSA: delete file " + export_file)
            except OSError as exc:
                self.log.info("NR-NSA: Can not delete file " + export_file +
                              ", exception: " + str(exc))
