from mock import Mock
from collections import OrderedDict

from base import BaseTest

from lib.parser import BaseParser, CmeditGetOutputParser
from lib.data import FdnDataBuilder


class TestCmeditGetOutputParser(BaseTest):
    mock_time = Mock()

    def setUp(self):
        self.cmedit_get_responses = """
FDN : ManagedElement=LTE08dg2ERBS00014,ENodeBFunction=1
eNodeBPlmnId : {mcc=353, mnc=57, mncLength=2}

FDN : ManagedElement=LTE08dg2ERBS00014,ENodeBFunction=1
userLabel : /sims/

FDN : ManagedElement=LTE07dg2ERBS00014,ENodeBFunction=1
eNodeBPlmnId : {mcc=353, mnc=57, mncLength=2}

FDN : ManagedElement=LTE07dg2ERBS00014,ENodeBFunction=1
userLabel : /sims/


4 instance(s)
"""

    def test_positve_parse(self):
        parser = CmeditGetOutputParser(self.cmedit_get_responses)
        data = parser.parse()
        expected_data = "OrderedDict([('LTE08dg2ERBS00014', {'" \
            "ManagedElement=LTE08dg2ERBS00014,ENodeBFunction=1': " \
            "{'userLabel': '/sims/', 'eNodeBPlmnId': " \
            "<ComplexType {mcc=353, mnc=57, mncLength=2}>}}), " \
            "('LTE07dg2ERBS00014', {'ManagedElement=LTE07dg2ERBS00014," \
            "ENodeBFunction=1': {'userLabel': " \
            "'/sims/', 'eNodeBPlmnId': <ComplexType {mcc=353, mnc=57, " \
            "mncLength=2}>}})])"
        self.assertEquals(expected_data, str(data))

    def test_positve_get_node_from_fdn(self):
        fdn = "MeContext=SGSN-15B-V611,ManagedElement=SGSN-15B-V611"
        builder = FdnDataBuilder()
        builder.set_fdn(fdn, {'userLabel': 'foo', 'release': '16B'})
        builder.set_fdn(fdn, {'productType': 'Node'})
        expected_data = OrderedDict([
            ('SGSN-15B-V611', {
                'MeContext=SGSN-15B-V611,ManagedElement=SGSN-15B-V611': {
                        'userLabel': 'foo',
                        'release': '16B',
                        'productType': 'Node'
                    }
                }
                )

        ])
        self.assertEquals(builder.data, expected_data)

    def test_empty_block_continue(self):
        cmedit_responses = """FDN : ManagedElement=LTE03dg2ERBS00014,ENodeBFunction=1
                        eNodeBPlmnId : {mcc=353, mnc=57, mncLength=2}

                        FDN : ManagedElement=LTE03dg2ERBS00014,ENodeBFunction=1
                        userLabel : /sims/



                        FDN : ManagedElement=LTE02dg2ERBS00014,ENodeBFunction=1
                        eNodeBPlmnId : {mcc=353, mnc=57, mncLength=2}

                        FDN : ManagedElement=LTE02dg2ERBS00014,ENodeBFunction=1
                        userLabel : /sims/


                        4 instance(s)
                        """
        parser = CmeditGetOutputParser(cmedit_responses+"\n")
        data = parser.parse()
        expected_data = "OrderedDict([('LTE03dg2ERBS00014', {'" \
                "ManagedElement=LTE03dg2ERBS00014,ENodeBFunction=1': " \
            "{'userLabel': '/sims/', 'eNodeBPlmnId': " \
            "<ComplexType {mcc=353, mnc=57, mncLength=2}>}}), " \
            "('LTE02dg2ERBS00014', {'ManagedElement=LTE02dg2ERBS00014," \
            "ENodeBFunction=1': {'userLabel': " \
            "'/sims/', 'eNodeBPlmnId': <ComplexType {mcc=353, mnc=57, " \
            "mncLength=2}>}})])"
        self.assertEquals(expected_data, str(data))



class TestBaseParser(BaseTest):

    def test_negative_base_parse_method_not_implemented(self):
        base = BaseParser("foo")
        self.assertRaises(NotImplementedError, base.parse)

    def test_lines_method_implemented(self):
        base = BaseParser("foo foo")
        self.assertEquals(base.lines, ['foo foo'])
