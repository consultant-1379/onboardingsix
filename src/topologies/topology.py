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

import os
import json

from abc import ABCMeta, abstractmethod
from multiprocessing import Process

from common.log import NRNSALogger
from common.collection_utils import CollectionUtils


class Topology(Process):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, file_path):
        Process.__init__(self)
        self.collection_utils = CollectionUtils()
        self.log = NRNSALogger()
        self.constants = Topology.load_constants(file_path)

    @staticmethod
    def load_constants(file_path):
        filename = os.path.join(file_path, 'constants.json')
        with open(filename) as open_file:
            return json.load(open_file)
