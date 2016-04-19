from core.inputfile import Section
from core.swmm.project import Project
from core.swmm.hydrology.aquifer import Aquifer
import unittest


class SimpleAquifersTest(unittest.TestCase):

    TEST_TEXT = ("[AQUIFERS]",
                 ";;Aquifer       \tPhi   \tWP    \tFC    \tHydCon\tKslope\tTslope\tUEF   \tLED   \tLGLR  \tBEL   \tWTEL  \tUZM   \tUEF Pat",
                 ";;--------------\t------\t------\t------\t------\t------\t------\t------\t------\t------\t------\t------\t------\t------",
                 " 1              \t0.5   \t0.15  \t0.30  \t0.1   \t12    \t15.0  \t0.35  \t14.0  \t0.002 \t0.0   \t3.5   \t0.40  \t      ",
                 "1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13\t14")

    def runTest(self):
        from_text = Project()
        source_text = '\n'.join(self.TEST_TEXT)
        from_text.set_text(source_text)
        project_section = from_text.aquifers

        assert Section.match_omit(project_section.get_text(), source_text, " \t-;\n")

        val = project_section.value[0]

        assert val.name == "1"
        assert val.porosity == "0.5"
        assert val.wilting_point == "0.15"
        assert val.field_capacity == "0.30"
        assert val.conductivity == "0.1"
        assert val.conductivity_slope == "12"
        assert val.tension_slope == "15.0"
        assert val.upper_evaporation_fraction == "0.35"
        assert val.lower_evaporation_depth == "14.0"
        assert val.lower_groundwater_loss_rate == "0.002"
        assert val.bottom_elevation == "0.0"
        assert val.water_table_elevation == "3.5"
        assert val.unsaturated_zone_moisture == "0.40"
        assert val.upper_evaporation_pattern == ""

        val = project_section.value[1]

        assert val.name == "1"
        assert val.porosity == "2"
        assert val.wilting_point == "3"
        assert val.field_capacity == "4"
        assert val.conductivity == "5"
        assert val.conductivity_slope == "6"
        assert val.tension_slope == "7"
        assert val.upper_evaporation_fraction == "8"
        assert val.lower_evaporation_depth == "9"
        assert val.lower_groundwater_loss_rate == "10"
        assert val.bottom_elevation == "11"
        assert val.water_table_elevation == "12"
        assert val.unsaturated_zone_moisture == "13"
        assert val.upper_evaporation_pattern == "14"

        assert Aquifer.metadata.label_of("name") == "Aquifer Name"
        assert Aquifer.metadata.hint_of("name") == "User-assigned aquifer name."


class SingleAquiferTest(unittest.TestCase):

    def setUp(self):

        self.my_options = Aquifer()

    def runTest(self):
        # Test aquifer parameters in Example 5
        test_aquifer = r"""
        ;;Aquifer       	Phi   	WP    	FC    	HydCon	Kslope	Tslope	UEF   	LED   	LGLR  	BEL   	WTEL  	UZM   	UEF Pat
        ;;--------------	------	------	------	------	------	------	------	------	------	------	------	------	------
               1            	0.5   	0.15  	0.30  	0.1   	12    	15.0  	0.35  	14.0  	0.002 	0.0   	3.5   	0.40
        """
        # --Test set_text
        self.my_options.set_text(test_aquifer)
        # --Test get_text through matches
        # --Failed, this data structure appears to be messy
        # --Error:Session name [AQUIFER] is after the parameters
        actual_text = self.my_options.get_text() # display purpose
        assert self.my_options.matches(test_aquifer)
