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
from test_project import ProjectTest
from test_patterns import SimplePatternTest
from test_curves import SimpleCurveTest
from test_demands import SimpleDemandsTest
from test_sources import SimpleSourcesTest

my_suite = unittest.TestSuite()

# for MTP 1:
my_suite.addTest(SimpleTitleTest())
my_suite.addTest(SimpleOptionsTest())
my_suite.addTest(SimpleQualityTest())
my_suite.addTest(SimpleReactionsTest())
my_suite.addTest(SimpleTimesTest())
my_suite.addTest(SimpleEnergyTest())
my_suite.addTest(SimpleReportTest())
my_suite.addTest(SimpleBackdropTest())
my_suite.addTest(ProjectTest())

# will need for later MTPs:
my_suite.addTest(SimplePatternTest())
my_suite.addTest(SimpleCurveTest())
my_suite.addTest(SimpleDemandsTest())
my_suite.addTest(SimpleSourcesTest())

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
