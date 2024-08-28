####################################################################
# COPYRIGHT Ericsson AB 2016
#
# The copyright to the computer program(s) herein is the property of
# Ericsson AB. The programs may be used and/or copied only with written
# permission from Ericsson AB. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
####################################################################

import re
from .data import FdnDataBuilder


class BaseParser(object):
    """ Base class to be extended by the parsers below.
    """

    def __init__(self, output):
        """ Just requires the output string.
        """
        self.output = output

    @property
    def lines(self):
        """ Just a helper property to return the lines of the ouput as a list.
        """
        return self.output.strip().splitlines()

    @property
    def blocks(self):
        """ Just a helper property to return the blocks of the ouput as a list.
        A block usually is separated by 2 "\n".
        """
        return self.output.split('\n\n')

    def parse(self, *args, **kwargs):
        """ This method must be implemented by the parsers.
        """
        raise NotImplementedError


class CmeditGetOutputParser(BaseParser):
    """ It gets the output information from the "cmedit get" command and parses
    returning a dict with the format described by the FdnDataBuilder class.
    """
    fdn_regex = re.compile(r'^\s*FDN\s*:\s*([\w\W%s,\-]+)$' %
                           FdnDataBuilder.attr_val_delimiter)
    attr_value_regex = re.compile(r'^\s*([\w\W\s]+)\s+:\s*(.*)$')
    instances_count_regex = re.compile(r'^\s*\d+\s+instance\(s\)\s*$')

    def parse(self, node=None):  # pylint: disable=I0011,W0221
        """ Separate the "cmedit get" output into block chunks, and for each
        block parses the FDNs and it attributes and values.

        Example of a "cmedit get" output below:
        -----------------------------------------------------------------------
        FDN : ManagedElement=LTE08dg2ERBS00013,ENodeBFunction=1
        nnsfMode : RPLMN_IF_SAME_AS_SPLMN
        timePhaseMaxDeviationMbms : 50

        FDN : ManagedElement=LTE08dg2ERBS00014,ENodeBFunction=1
        nnsfMode : RPLMN_IF_SAME_AS_SPLMN
        timePhaseMaxDeviationMbms : 50

        2 instance(s)
        -----------------------------------------------------------------------

        It parses the output and translate it into a dict format described on
        the docstring of the FdnDataBuilder class.
        """
        builder = FdnDataBuilder()
        for block in self.blocks:
            lines = [i.strip() for i in block.splitlines() if i.strip()]
            if not lines:
                # in case a block is empty, just continue
                continue
            if self.instances_count_regex.match(lines[0]):
                # this is possibly the last block of the output
                continue
            fdn_line = lines.pop(0)  # the first line is the FDN line
            match = self.fdn_regex.match(fdn_line)
            if match is not None and match.groups():
                fdn = str(match.groups()[0])
                attrs = dict(
                    [self.attr_value_regex.match(l).groups() for l in lines
                     if self.attr_value_regex.match(
                         l) is not None and self.attr_value_regex.match(
                             l).groups()])
                builder.set_fdn(fdn, attrs, node=node)
        return builder.data

    @staticmethod
    def parse_gnodes(input_value):
        regex = re.compile(r'^([\w\W=,\s]+)$')  # Complex Type format regex

        match = regex.match(input_value)
        if match is not None and match.groups():
            matching = match.groups()[0]
            return dict([i.strip().split('=') for i in matching.split(',')])
        return dict()
