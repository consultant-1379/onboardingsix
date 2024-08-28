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
from collections import OrderedDict


class ComplexType(object):
    """ This class abstracts the ENM know Complex Type as it is displayed
    by the output of the "cmedit get" command as a different format than
    the format used in arguments of the "cmedit set".
     - "cmedit get" output returns the format: {aaa=111, bbb=222}
     - "cmedit set" arguments must be in the format: (aaa=111,bbb=222)

    >>> ct = ComplexType('{aaa=111, bbb=222, ccc=333}')
    >>> ct
    <ComplexType {aaa=111, bbb=222, ccc=333}>
    >>> ct.cmedit_set_format
    '(aaa=111,bbb=222,ccc=333)'
    >>> ComplexType.test('{x=1, y=9, zzz=8}')
    True
    >>> ComplexType.test('{x: 1, y: 2}')
    False
    >>> ComplexType.test('any string')
    False
    """

    regex = re.compile(r'^{([\w=,\s]+)}$')  # Complex Type format regex
    regex_list = re.compile(r'^\[{([\w=,\s]+)}\]$')  # with square brackets

    def __init__(self, real_value):
        """ The real_value is considered a string in the "cmedit get" output
        format, e.g.: {aaa=111, bbb=222, ccc=333}.
        """
        self.real_value = real_value

    def __str__(self):
        """ The str representation of this obj is just the real_value itself.
        """
        return self.real_value

    def __repr__(self):
        """ Just the object representation.
        """
        return "<ComplexType %s>" % str(self)

    @property
    def data(self):
        match = self.regex.match(self.real_value)
        if not match:
            match = self.regex_list.match(self.real_value)
        matching = match.groups()[0]
        return dict([i.strip().split('=') for i in matching.split(',')])

    @property
    def cmedit_set_format(self):
        base = "[(%s)]" if self.real_value.startswith('[') else "(%s)"
        return base % ','.join(["%s=%s" % (k, v) for k, v in self.data])

    @classmethod
    def test(cls, value):
        """ It return True if the value is of the ENM Complex Type format.
        """
        return bool(cls.regex.match(value) or cls.regex_list.match(value))


class FdnDataBuilder(object):
    """ This class encapsulates the methods to build the data related to the
    FDN MOs that could be retrieved either from the "cmedit get" CLI output
    or from a CSV format.

    The data built by this class is in the following format:

    data = {
        <NODE_NAME_1>: {
            <FDN_1>: {<ATTRIBUTE1>: <VALUE1>,
                      <ATTRIBUTE2>: <VALUE2>},
            <FDN_2>: {<ATTRIBUTE1>: <VALUE1>,
                      <ATTRIBUTE2>: <VALUE2>}
        },
        ... and so on
    }

    >>> builder = FdnDataBuilder()
    >>> builder.set_fdn("MeContext=SGSN-15B-V611,ManagedElement=SGSN-15B-V611",
    ...                 {'userLabel': 'foo', 'release': '16B'})
    ...
    >>> builder.set_fdn("MeContext=LTE01ERBS00059,ManagedElement=1",
    ...                 {'userLabel': 'bar', 'productType': 'Node'})
    ...
    >>> builder.data
    OrderedDict([('SGSN-15B-V611', {'MeContext=SGSN-15B-V611,\
ManagedElement=SGSN-15B-V611': {'userLabel': 'foo', 'release': \
'16B'}}), ('LTE01ERBS00059', {'MeContext=LTE01ERBS00059,\
ManagedElement=1': {'userLabel': 'bar', 'productType': 'Node'}})])

    """
    mo_fdn_delimiter = ','
    attr_val_delimiter = '='
    actions = ['set', 'create', 'delete']

    def __init__(self):
        """ It just instantiate the data dict to be populated by the add_fdn
        method.
        """
        self.data = OrderedDict()

    def set_fdn(self, fdn, attrs, node=None):
        """ It populates the self.data dict given a fdn, a list containing
        tuples of attributes and values for the FDN. The data is built as
        described on the docstring of this class.
        If the action argument is provided,  it includes that value into the
        self.data[node]['action'] level.
        """
        if node is None:
            node = self.get_node_from_fdn(fdn)
        self.data.setdefault(node, {})
        self.data[node].setdefault(fdn, {})

        for attr, value in attrs.items():
            if not isinstance(value, ComplexType):
                value = value.strip()
                # checks if the value is an ENM Complex Type format
                if ComplexType.test(value):
                    # the value is transformed into a ComplexType instance then
                    value = ComplexType(value)
                elif value == 'null':
                    value = str('')
            attrs[str(attr)] = value
        self.data[node][fdn].update(attrs)

    @classmethod
    def get_node_from_fdn(cls, fdn):
        """ Look for a node name giving a FDN. First parses the FDN MOs
        separated by "cls.mo_fdn_delimiter" into a dict:
        E.g.: ManagedElement=LTE08dg2ERBS00013,ENodeBFunction=1     =>
              {'ManagedElement': LTE08dg2ERBS00013, 'ENodeBFunction': '1'}

        The node name is get either from the the MeContext MO or the
        ManagementElement MO.
        """
        node_details = dict([tuple(i.split(cls.attr_val_delimiter))
                             for i in fdn.split(cls.mo_fdn_delimiter)
                             if cls.attr_val_delimiter in i])
        node = node_details.get('MeContext', node_details.get(
            'ManagedElement', node_details.get('NetworkElement')))
        return node.strip() if node is not None else ""
