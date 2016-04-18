from core.swmm.hydrology.lidcontrol import LIDControl
import unittest


class SubLIDControlTest(unittest.TestCase):
    def __init__(self):
        unittest.TestCase.__init__(self)

    def setUp(self):

        self.my_options = LIDControl()

    def runTest(self):
        # Test LID parameters from Example 4a, examined according to SWMM 5.1 manual
        # Modified on test purposes
        # This test passed for an individual LID control.
        # However, a data structure for LID_CONTROLS has not yet created.
        # Case 1: test all LID controls
        test_lid_control_all = r"""
;;Name           Type
;;BC bio-retention cell
;;RG rain garden
;;GR green roof
;;IT infiltration trench
;;PP permeable pavement
;;RB rain barrel
;;RD rooftop disconnection
;;VS vegetative swale
;;Name           Type/Layer Parameters
;;Name           SURFACE    StorHt    VegFrac     Rough      Slope     Xslope
;;Name           SOIL       Thick     Por         FC         WP        Ksat        Kcoeff     Suct
;;Name           PAVEMENT   Thick     Vratio      FracImp    Perm      Vclog
;;Name           STORAGE    Height    Vratio      Seepage    Vclog
;;Name           DRAIN      Coeff     Expon       Offset     Delay
;;Name           DRAINMAT   Thick     Vratio      Rough
;;-------------- ---------- ----------
PorousPave       PP
PorousPave       SURFACE    0.0        0.0        0.02       2          5
PorousPave       SOIL       3          0.5        0.2        0.1        0.5        10.0       3.5
PorousPave       PAVEMENT   6          0.15       0          100        0
PorousPave       STORAGE    12         0.75       0.2        0
PorousPave       DRAIN      0          0.5        0          6
PorousPave       DRAINMAT   1          0.4        0.01
        """
        # --Test set_text
        self.my_options.set_text(test_lid_control_all)
        # --Test get_text through matches
        actual_text = self.my_options.get_text() # display purpose
        assert self.my_options.matches(test_lid_control_all)
        pass
        test_lid_control_surface_only = """
Swale            VS
Swale            SURFACE    36         0.0        0.24       1.0        5"""
        # --Test set_text
        self.my_options.set_text(test_lid_control_surface_only)
        #  --Test get_text through matches
        actual_text = self.my_options.get_text()  # display purpose
        assert self.my_options.matches(test_lid_control_surface_only)
        pass

test_lid_control_example4a = r"""
[LID_CONTROLS]
GreenRoof        BC
GreenRoof        SURFACE    0.0        0.0        0.1        1.0        5
GreenRoof        SOIL       3          0.5        0.2        0.1        0.5        10.0       3.5
GreenRoof        STORAGE    1          0.75       0          0
GreenRoof        DRAIN      1          0.5        0          6

PorousPave       PP
PorousPave       SURFACE    0.0        0.0        0.02       2          5
PorousPave       PAVEMENT   6          0.15       0          100        0
PorousPave       STORAGE    12         0.75       0.2        0
PorousPave       DRAIN      0          0.5        0          6

Planters         BC
Planters         SURFACE    6          0.0        0.0        0.0        5
Planters         SOIL       12         0.5        0.2        0.1        0.5        10.0       3.5
Planters         STORAGE    12         0.5        0.2        0
Planters         DRAIN      0          1          0.5        6

InfilTrench      IT
InfilTrench      SURFACE    0.0        0.0        0.24       0.4        5
InfilTrench      STORAGE    36         0.40       0.2        0
InfilTrench      DRAIN      0          0.5        0          6

RainBarrels      RB
RainBarrels      STORAGE    48         1          0          0
RainBarrels      DRAIN      1          0.5        0          6

Swale            VS
Swale            SURFACE    36         0.0        0.24       1.0        5"""