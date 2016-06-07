##  This section is needed to run coverage from the command line ------TODO: change
## >> Run coverage from command line, navigate to test_all.py
## >> coverage run test_all.py
## >> coverage report >> Report_coverage_EPANET.txt
# import sys
# sp = sorted(sys.path)
# dnames = ', '.join(sp)
# print(dnames)
# sys.path.append("E:\\Code\\PyCharmProjects\\SWMM-EPANET_User_Interface")
# sys.path.append("E:\\Code\\PyCharmProjects\\SWMM-EPANET_User_Interface\\src")
# ---------------------------------------------------------------------------------
import webbrowser
import unittest
import test.HTMLTestRunner
from test_title import SimpleTitleTest
from test_options import SimpleOptionsTest
from test_quality import SimpleQualityTest
from test_reactions import SimpleReactionsTest
from test_times import SimpleTimesTest
from test_energy import SimpleEnergyTest
from test_report import SimpleReportTest
from test_backdrop import SimpleBackdropTest
# from test_project import ProjectTest  # Changes to a individual regression test
from test_patterns import SimplePatternTest
from test_curves import SimpleCurveTest
from test_demands import SimpleDemandsTest
from test_sources import SimpleSourcesTest

my_suite = unittest.TestSuite()

# Title - MTP 1:
my_suite.addTest(SimpleTitleTest('test_bare'))
my_suite.addTest(SimpleTitleTest('test_empty'))
my_suite.addTest(SimpleTitleTest('test_one_row'))
my_suite.addTest(SimpleTitleTest('test_multi_row'))
my_suite.addTest(SimpleTitleTest('test_rt_before_title'))

# Options and reporting - MTP 1:
my_suite.addTest(SimpleOptionsTest('test_get'))
my_suite.addTest(SimpleOptionsTest('test_setget'))
my_suite.addTest(SimpleTimesTest('test_get'))
my_suite.addTest(SimpleTimesTest('test_no_leading_space'))
my_suite.addTest(SimpleTimesTest('test_leading_space'))
my_suite.addTest(SimpleReportTest('test_simple'))
my_suite.addTest(SimpleReportTest('test_page'))
my_suite.addTest(SimpleReportTest('test_all'))

# Network components - MTP 3:
# junctions
# Reservoirs
# Tanks
# Pipes
# Pumps
# Valves
# Emitters

# System operation - MTP 2
my_suite.addTest(SimplePatternTest('test_pattern'))
my_suite.addTest(SimplePatternTest('test_patterns'))
my_suite.addTest(SimpleCurveTest('test_curve'))
my_suite.addTest(SimpleCurveTest('test_curves'))
my_suite.addTest(SimpleEnergyTest())
# Status - MTP 3
# Controls
# Rules
my_suite.addTest(SimpleDemandsTest())

# Water quality - MTP 2:
my_suite.addTest(SimpleQualityTest('test_get'))
my_suite.addTest(SimpleQualityTest('test_setget'))
my_suite.addTest(SimpleReactionsTest('test_get'))
my_suite.addTest(SimpleReactionsTest('test_setget'))
my_suite.addTest(SimpleSourcesTest())
# Mixing - MTP 3?

# Network Map/Tags - MTP 3:
# Coordinates
# Vertices
# Labels
# Backdrop - MTP2?
my_suite.addTest(SimpleBackdropTest())
# Tags

# Project test
# my_suite.addTest(ProjectTest())


if __name__ == "__main__":
    # execute only if run as a script
    # runner = unittest.TextTestRunner()
    report_filename = "test_results_epanet.html"
    fp = file(report_filename, 'wb')
    runner = test.HTMLTestRunner.HTMLTestRunner(
        stream=fp,
        title='EPANET Core Test Report',
        description='Unit test results')

    runner.run(my_suite)
    fp.close()
    try:
        webbrowser.open_new_tab(report_filename)
    except:
        print("Test results written to " + report_filename)
