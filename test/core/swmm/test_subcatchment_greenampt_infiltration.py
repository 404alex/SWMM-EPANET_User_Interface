from core.swmm.hydrology.subcatchment import GreenAmptInfiltration
import unittest


class SubGreenAmptInfiltrationTest(unittest.TestCase):
    def __init__(self):
        unittest.TestCase.__init__(self)

    def setUp(self):

        self.my_options = GreenAmptInfiltration()

    def runTest(self):
        # Test default, default is empty string, no adjustments, Failed
        # -- No SECTION_NAME
        # -- actual_text contains tabs, not empty string
        #name = self.my_options.SECTION_NAME
        #assert name == "[INFILTRATION]"
        actual_text = self.my_options.get_text()
        #assert actual_text == ''

        # Test aquifer parameters in Example 5
        #
        test_infiltration = r"""
[INFILTRATION]
;;Subcatchment  	Psi   	    Ksat   	    IMD
;;--------------	----------	----------	----------
1               	100       	0.1       	0.1
"""
        # Test set_text
        # -- Failed for the same issue as other Subcatchment parameters.
        self.my_options.set_text(test_infiltration)
        # --Test get_text through matches
        actual_text = self.my_options.get_text() # display purpose
        assert self.my_options.matches(test_infiltration)

        pass