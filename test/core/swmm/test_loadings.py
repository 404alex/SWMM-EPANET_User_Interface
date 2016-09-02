import unittest
from core.swmm.inp_reader_sections import InitialLoadingReader
from core.swmm.inp_writer_sections import InitialLoadingsWriter
from core.swmm.hydrology.subcatchment import InitialLoading
from core.swmm.inp_reader_project import ProjectReader
from core.swmm.inp_writer_project import ProjectWriter
from test.core.section_match import match, match_omit

class SimpleLoadingTest(unittest.TestCase):
    """Test LOADINGS section"""

    def setUp(self):
        """"""
        self.project_reader = ProjectReader()
        self.project_writer = ProjectWriter()

    def test_one_loading(self):
        """Test all options of one Loading"""
        test_text = "SB1   TSS         0.1"
        my_options = InitialLoadingReader.read(test_text)
        actual_text = InitialLoadingsWriter.as_text(my_options)
        msg = '\nSet:' + test_text + '\nGet:' + actual_text
        self.assertTrue(match(actual_text, test_text), msg)

    def test_loading_section(self):
        """Test LOADINGS section"""
        source_text = r"""
[LOADINGS]
;;Subcatchment     Pollutant   Loading  Pollutant   Loading
;;----------------------------------------------------------
SB1                TSS         0.1      Lead         0.01
        """
        section_from_text = self.project_reader.read_loadings.read(source_text)
        actual_text = self.project_writer.write_loadings.as_text(section_from_text)
        msg = '\nSet:\n' + source_text + '\nGet:\n' + actual_text
        self.assertTrue(match_omit(actual_text, source_text, " \t-;\n"), msg)

        project_section = section_from_text

        self.assertTrue(len(project_section.value) == 2, "Expected 2 loadings, found " + str(len(project_section.value)))
        tss = project_section.value[0]
        self.assertTrue(tss.pollutant_name == "TSS", "Expected pollutant name TSS, found " + tss.pollutant_name)
        self.assertTrue(str(tss.initial_buildup) == "0.1", "Expected TSS buildup = 0.1, found " + str(tss.initial_buildup))

        Lead = project_section.value[1]
        self.assertTrue(Lead.pollutant_name == "Lead", "Expected pollutant name Lead, found " + Lead.pollutant_name)
        self.assertTrue(str(Lead.initial_buildup) == "0.01", "Expected Lead buildup = 0.01, found " + str(Lead.initial_buildup))

def main():
    unittest.main()

if __name__ == "__main__":
    main()
