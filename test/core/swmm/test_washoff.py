import unittest
from core.swmm.inp_reader_sections import WashoffReader
from core.swmm.inp_writer_sections import WashoffWriter
from test.core.section_match import match
from core.swmm.quality import Washoff
from core.swmm.inp_reader_project import ProjectReader
from core.swmm.inp_writer_project import ProjectWriter
from test.core.section_match import match, match_omit

class SimpleWashoffTest(unittest.TestCase):
    """Test WASHOFF section"""

    def setUp(self):
        """"""
        self.project_reader = ProjectReader()
        self.project_writer = ProjectWriter()

    def test_one_washoff(self):
        """Test all options"""
        test_text = "Residential      TSS              EXP        0.1      1        0        0  "
        my_options = WashoffReader.read(test_text)
        actual_text = WashoffWriter.as_text(my_options)
        msg = '\nSet:' + test_text + '\nGet:' + actual_text
        self.assertTrue(match(actual_text, test_text), msg)

    def test_washoff_section(self):
        """Test WASHOFF section"""
        source_text = r"""
[WASHOFF]
;;                                                               Clean.   BMP
;;LandUse          Pollutant        Function   Coeff1   Coeff2   Effic.   Effic.
;;------------------------------------------------------------------------------
  Residential      TSS              EXP        0.1      1        0        0
  Residential      Lead             EMC        0        0        0        0
  Undeveloped      TSS              EXP        0.1      0.7      0        0
  Undeveloped      Lead             EMC        0        0        0        0
        """
        section_from_text = self.project_reader.read_washoff.read(source_text)
        actual_text = self.project_writer.write_washoff.as_text(section_from_text)
        msg = '\nSet:\n' + source_text + '\nGet:\n' + actual_text
        self.assertTrue(match(actual_text, source_text), msg)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
