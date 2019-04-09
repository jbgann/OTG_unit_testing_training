import unittest
import nid_tools
import NodeDowner

from mock import patch,call

sinfo_output = """PARTITION       AVAIL  TIMELIMIT  NODES  STATE NODELIST
system             up 1-12:00:00      7 drain* nid[00371,01729-01730,01748,09558,09581,11038]
system             up 1-12:00:00     24  down* nid[00248,00420,02308,02594,03353,04005,04601,04674,06255,06370,06499,07518,07577,08330,09089,09204,09821,10168,10362,10409,10931,11169,11934,12042]
system             up 1-12:00:00     13   drng nid[00456,00459,00461,00463,00465,00471-00472,00486,00490-00491,00493,00505,00521]
system             up 1-12:00:00      1   comp nid10726
system             up 1-12:00:00     51  drain nid[00040-00063,00072-00075,00077-00096,03718,08885,09354]
system             up 1-12:00:00      2   resv nid[00039,05313]
system             up 1-12:00:00     13    mix nid[00443,00477,00488,00492,00495-00496,00499,00502,00504,00507,00510-00511,00522]"""

class TestNidTools(unittest.TestCase):
    def test_getNodeNumbersFromRange(self):
        self.assertTrue(413 in nid_tools.getNodeNumbersFromRange("410-415"))
        self.assertTrue(410 in nid_tools.getNodeNumbersFromRange("410-415"))
        self.assertTrue(415 in nid_tools.getNodeNumbersFromRange("410-415"))
        self.assertTrue(409 not in nid_tools.getNodeNumbersFromRange("410-415"))
        self.assertTrue(416 not in nid_tools.getNodeNumbersFromRange("410-415"))
        self.assertTrue(410 in nid_tools.getNodeNumbersFromRange("410"))

    @patch("nid_tools.getNodeNumbersFromRange")
    def test_get_node_list_from_pdsh_notation(self,mocked_getNodeNumbersFromRange):
        sample_multi_notation = "nid[00512,00514-00516]"
        sample_single_notation = "nid10726"
        #Sets the return values of the mocked function
        #note that if we wanted a single, consistent return value, we would
        #use mocked_getNodeNumbersFromRange.return_value
        mocked_getNodeNumbersFromRange.side_effect = iter([[512],[514,515,516]])
        #defines the calls we expect to be made to the mocked function
        expected_multi_calls =[call("00512"),call("00514-00516")]

        multi_nodelist = nid_tools.get_node_list_from_pdsh_notation(sample_multi_notation)
        mocked_getNodeNumbersFromRange.assert_has_calls(expected_multi_calls)
        self.assertTrue("nid00512" in multi_nodelist)
        self.assertTrue("nid00514" in multi_nodelist)
        self.assertTrue("nid00515" in multi_nodelist)
        self.assertTrue("nid00516" in multi_nodelist)

        mocked_getNodeNumbersFromRange.reset_mock()

        single_nodelist = nid_tools.get_node_list_from_pdsh_notation(sample_single_notation)

        mocked_getNodeNumbersFromRange.assert_not_called()
        self.assertTrue(single_nodelist == ["nid10726"])

    #not actually a unit test, as it relies on other functions working properly
    #but still useful
    @patch("subprocess.check_output")
    def test_get_state(self,mocked_check_output):
        mocked_check_output.return_value = sinfo_output
        self.assertTrue(nid_tools.get_state("nid10726") == "comp")
        self.assertTrue(nid_tools.get_state("nid00248") == "down*")
        self.assertRaises(NonexistentNodeError,nid_tools.get_state,("nid99999",))
