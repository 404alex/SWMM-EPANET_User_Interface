import unittest
from core.epanet.epanet_project import EpanetProject
from core.epanet.inp_reader_project import ProjectReader
from core.epanet.inp_writer_project import ProjectWriter
from core.epanet.inp_reader_sections import *
from core.epanet.inp_writer_sections import *
from test.core.section_match import match, match_omit
from core.epanet.hydraulics.node import SourceType


class SimpleSourcesTest(unittest.TestCase):
    """Test Sources section"""
    TEST_TEXT = ("[SOURCES]",
                 ";Node         \tType         \tQuality \tPattern",
                 " JUNCTION-9090\tCONCEN       \t8330    \tPattern-A",
                 " JUNCTION-9091\tMASS         \t8331    \tPattern-B",
                 " JUNCTION-9092\tFLOWPACED    \t8332    \tPattern-C",
                 " JUNCTION-9093\tSETPOINT     \t8333    \tPattern-D",
                 " JUNCTION-9094\tCONCEN       \t8334")

    def runTest(self):
        """Test set_text and get_text"""
        source_text = '\n'.join(self.TEST_TEXT)
        project_sources = ProjectReader().read_sources(source_text)

        assert match_omit(SourceWriter.as_text(project_sources), source_text, " \t-;\n")

        assert match_omit(project_sources.get_text(), source_text, " \t-;\n")

        assert project_sources.value[0].name == "JUNCTION-9090"
        assert project_sources.value[0].source_type == SourceType.CONCEN
        assert project_sources.value[0].baseline_strength == "8330"
        assert project_sources.value[0].pattern_name == "Pattern-A"

        assert project_sources.value[1].name == "JUNCTION-9091"
        assert project_sources.value[1].source_type == SourceType.MASS
        assert project_sources.value[1].baseline_strength == "8331"
        assert project_sources.value[1].pattern_name == "Pattern-B"

        assert project_sources.value[2].name == "JUNCTION-9092"
        assert project_sources.value[2].source_type == SourceType.FLOWPACED
        assert project_sources.value[2].baseline_strength == "8332"
        assert project_sources.value[2].pattern_name == "Pattern-C"

        assert project_sources.value[3].name == "JUNCTION-9093"
        assert project_sources.value[3].source_type == SourceType.SETPOINT
        assert project_sources.value[3].baseline_strength == "8333"
        assert project_sources.value[3].pattern_name == "Pattern-D"

        assert project_sources.value[4].name == "JUNCTION-9094"
        assert project_sources.value[4].source_type == SourceType.CONCEN
        assert project_sources.value[4].baseline_strength == "8334"
        assert project_sources.value[4].pattern_name == ""

