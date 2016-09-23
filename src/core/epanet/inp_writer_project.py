from core.inp_writer_base import InputFileWriterBase, SectionWriterAsList, SectionAsList
from core.epanet.options.times import TimesOptions
from core.epanet.patterns import Pattern
from core.epanet.title import Title
from core.epanet.vertex import Vertex

from core.epanet.inp_writer_sections import *

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str,bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


class ProjectWriter(InputFileWriterBase):
    """Read an EPANET input file into in-memory data structures"""

    def __init__(self):
        """Initialize the sections of an EPANET input file.
           Any sections not initialized here will be handled by the generic core.project_base.Section class."""
        self.write_title = TitleWriter()
        self.write_junctions = SectionWriterAsList("[JUNCTIONS]", JunctionWriter,
                                                   ";ID             \tElev  \tDemand\tPattern\n"
                                                   ";---------------\t------\t------\t-------")
        self.write_emitters = SectionWriterAsList("[EMITTERS]", EmittersWriter,
                                                ";Junction       \tCoefficient\n"
                                                ";---------------\t------------")

        self.write_reservoirs = SectionWriterAsList("[RESERVOIRS]", ReservoirWriter,
                                                    ";ID             \tHead        \tPattern\n"
                                                    ";---------------\t------------\t-------")
        self.write_tanks = SectionWriterAsList("[TANKS]", TankWriter,
            ";ID              \tElevation   \tInitLevel   \tMinLevel    \tMaxLevel    \tDiameter    \tMinVol      \tVolCurve")

        self.write_mixing = SectionWriterAsList("[MIXING]", MixingWriter,
                                                ";Tank           \tModel       \tMixing Volume Fraction\n"
                                                ";---------------\t------------\t----------------------")
        self.write_pipes = SectionWriterAsList("[PIPES]", PipeWriter,
                                               ";ID             \tNode1           \tNode2           \t"
                                                 "Length      \tDiameter    \tRoughness   \tMinorLoss   \tStatus")
        self.write_pumps = SectionWriterAsList("[PUMPS]", PumpWriter,
                                               ";ID             \tNode1           \tNode2           \tParameters")
        self.write_valves = SectionWriterAsList("[VALVES]", ValveWriter,
            ";ID              \tNode1           \tNode2           \tDiameter    \tType\tSetting     \tMinorLoss   ")
        self.write_patterns = SectionWriterAsList("[PATTERNS]", PatternWriter,
                                                  ";ID              \tMultipliers\n"
                                                  ";----------------\t-----------")
        self.write_curves = SectionWriterAsList("[CURVES]", CurveWriter,
                                                ";ID              \tX-Value     \tY-Value\n"
                                                ";----------------\t------------\t-------")
        self.write_energy = EnergyOptionsWriter()
        self.write_status = SectionWriterAsList("[STATUS]", StatusWriter, ";ID             \tStatus/Setting")
        self.write_controls = ControlWriter()
        self.write_rules = RuleWriter()
        self.write_demands = SectionWriterAsList("[DEMANDS]", DemandWriter,
                                                 ";ID             \tDemand   \tPattern   \tCategory\n"
                                                 ";---------------\t---------\t----------\t--------")

        self.write_quality = SectionWriterAsList("[QUALITY]", QualityWriter,
                                                 ";Node           \tInitQuality\n"
                                                 ";---------------\t-----------")
        self.write_reactions = ReactionsWriter()
        self.write_sources = SectionWriterAsList("[SOURCES]", SourceWriter,
                                                 ";Node           \tType          \tStrength    \tPattern\n"
                                                 ";---------------\t--------------\t------------\t-------")
        self.write_options = OptionsWriter()
        self.write_times = SectionWriter()
        self.write_report = ReportOptionsWriter()
        self.write_coordinates = SectionWriterAsList("[COORDINATES]", CoordinateWriter,
                                                     ";Node            \tX-Coord   \tY-Coord")
        self.write_vertices = SectionWriterAsList("[VERTICES]", CoordinateWriter,
                                                  ";Link            \tX-Coord   \tY-Coord")
        self.write_labels = SectionWriterAsList("[LABELS]", LabelWriter,
                                                ";X-Coord        \tY-Coord         \tLabel & Anchor Node")
        self.write_backdrop = BackdropOptionsWriter()
        self.write_tags = TagsWriter()

    def as_text(self, project):

        inp = InputFileWriterBase.as_text(self, project)

        quality_text = QualityWriter.as_text(project)
        if quality_text:
            inp += '\n' + quality_text + '\n'

        tags_text = self.write_tags.as_text(project)
        if tags_text:
            inp += '\n' + tags_text + '\n'

        mixing = SectionAsList('[MIXING]')
        mixing.value = project.tanks.value
        mixing_text = self.write_mixing.as_text(mixing)
        if mixing_text:
            inp += '\n' + mixing_text + '\n'

        emitters = SectionAsList('[EMITTERS]')
        emitters.value = project.junctions.value
        emitters_text = self.write_emitters.as_text(emitters)
        if emitters_text:
            inp += '\n' + emitters_text + '\n'

        inp += '\n' + '[END]' + '\n'

        return inp