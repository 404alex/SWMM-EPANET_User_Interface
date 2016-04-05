import traceback
from enum import Enum
from core.inputfile import Section
from core.metadata import Metadata


class Link(object):
    """A link in a SWMM model"""
    def __init__(self, name, inlet_node, outlet_node):
        self.name = name
        """Link Name"""

        self.description = None
        """Optional description of the Link"""

        self.tag = None
        """Optional label used to categorize or classify the Link"""

        self.inlet_node = inlet_node
        """Node on the inlet end of the Link"""

        self.outlet_node = outlet_node
        """Node on the outlet end of the Link"""

        self.vertices = {}
        """Collection of intermediate vertices along the length of the link"""


class Conduit(Link):
    """A conduit in a SWMM model"""
    def __init__(self, name, inlet_node, outlet_node):
        Link.__init__(self, name, inlet_node, outlet_node)
        self.length = 0.0
        """Conduit length (feet or meters)."""

        self.roughness = 0.0
        """Manning's roughness coefficient."""

        self.inlet_offset = 0.0
        """Depth or elevation of the conduit invert above the node invert
            at the upstream end of the conduit (feet or meters)."""

        self.outlet_offset = 0.0
        """Depth or elevation of the conduit invert above the node invert
            at the downstream end of the conduit (feet or meters)."""

        self.initial_flow = 0.0
        """Initial flow in the conduit (flow units)."""

        self.maximum_flow = 0.0
        """Maximum flow allowed in the conduit (flow units)."""

        self.cross_section = None
        """See class CrossSection"""

        self.entry_loss_coefficient = 0.0
        """Head loss coefficient associated with energy losses at the entrance of the conduit"""

        self.exit_loss_coefficient = 0.0
        """Head loss coefficient associated with energy losses at the exit of the conduit"""

        self.loss_coefficient = 0.0
        """Head loss coefficient associated with energy losses along the length of the conduit"""

        self.flap_gate = False
        """True if a flap gate exists that prevents backflow."""

        self.seepage = 0.0
        """Rate of seepage loss into surrounding soil (in/hr or mm/hr)."""


class Pump(Link):
    """A pump link in a SWMM model"""
    def __init__(self, name, inlet_node, outlet_node):
        Link.__init__(self, name, inlet_node, outlet_node)
        self.pump_curve = ""
        """str: Associated pump curve"""

        self.initial_status = 0.0
        """float: Initial status of the pump"""

        self.startup_depth = 0.0
        """float: Depth at inlet node when the pump turns on"""

        self.shutoff_depth = 0.0
        """float: Depth at inlet node when the pump turns off"""


class OrificeType(Enum):
    SIDE = 1
    BOTTOM = 2


class Orifice(Link):
    """An orifice link in a SWMM model"""
    def __init__(self, name, inlet_node, outlet_node):
        Link.__init__(self, name, inlet_node, outlet_node)
        self.type = OrificeType.SIDE
        """OrificeType: Type of orifice"""

        self.cross_section = None
        """See class CrossSection"""

        self.inlet_offset = 0.0
        """float: Depth of bottom of orifice opening from inlet node invert"""

        self.discharge_coefficient = 0.0
        """float: Discharge coefficient"""

        self.flap_gate = False
        """bool: True if a flap gate exists that prevents backflow."""

        self.o_rate = 0.0
        """float: Time to open/close a gated orifice"""


class WeirType(Enum):
    TRANSVERSE = 1
    SIDEFLOW = 2
    V_NOTCH = 3
    TRAPEZOIDAL = 4
    ROADWAY = 5


class RoadSurfaceType(Enum):
    PAVED = 1
    GRAVEL = 2


class Weir(Link):
    """A weir link in a SWMM model"""
    def __init__(self, name, inlet_node, outlet_node):
        Link.__init__(self, name, inlet_node, outlet_node)
        self.type = WeirType.TRANSVERSE
        """Type of weir"""

        self.cross_section = None
        """See class CrossSection"""

        self.inlet_offset = 0.0
        """float: Depth of bottom of weir opening from inlet node invert"""

        self.discharge_coefficient = 0.0
        """float: Discharge coefficient for central portion of weir"""

        self.flap_gate = False
        """bool: True if weir contains a flap gate to prevent backflow"""

        self.end_contractions = 0.0
        """float: Number of end contractions"""

        self.end_coefficient = 0.0
        """float: Discharge coefficient for flow through the triangular ends of a trapezoidal weir"""

        self.can_surcharge = False
        """bool: True if weir can surcharge"""

        self.road_width = 0.0
        """float: Width of road lanes and shoulders"""

        self.road_surface = RoadSurfaceType.PAVED
        """RoadSurfaceType: Type of road surface"""


class OutletCurveType(Enum):
    TABULAR_DEPTH = 1
    TABULAR_HEAD = 2
    FUNCTIONAL_DEPTH = 3
    FUNCTIONAL_HEAD = 4


class Outlet(Link):
    """An outlet link in a SWMM model"""
    def __init__(self, name, inlet_node, outlet_node):
        Link.__init__(self, name, inlet_node, outlet_node)
        self.inlet_offset = 0.0
        """float: Depth of outlet above inlet node invert"""

        self.flap_gate = False
        """bool: True if outlet contains a flap gate to prevent backflow"""

        self.coefficient = 0.0
        """float: Coefficient in outflow expression"""

        self.exponent = 0.0
        """float: Exponent in outflow expression"""

        self.curve_type = OutletCurveType.TABULAR_DEPTH
        """OutletCurveType: Method of defining flow as a function of either freeboard depth or head across the outlet"""

        self.rating_curve = ""
        """str: Name of rating curve that relates outflow to either depth or head"""


class CrossSectionShape(Enum):
    NotSet = 0
    CIRCULAR = 1            # Full Height = Diameter
    FORCE_MAIN = 2          # Full Height = Diameter, Roughness
    FILLED_CIRCULAR = 3     # Full Height = Diameter, Filled Depth
    RECT_CLOSED = 4         # Rectangular: Full Height, Top Width
    RECT_OPEN = 5           # Rectangular: Full Height, Top Width
    TRAPEZOIDAL = 6         # Full Height, Base Width, Side Slopes
    TRIANGULAR = 7          # Full Height, Top Width
    HORIZ_ELLIPSE = 8       # Full Height, Max. Width
    VERT_ELLIPSE = 9        # Full Height, Max. Width
    ARCH = 10               # Size Code or Full Height, Max. Width
    PARABOLIC = 11          # Full Height, Top Width
    POWER = 12              # Full Height, Top Width, Exponent
    RECT_TRIANGULAR = 13    # Full Height, Top Width, Triangle Height
    RECT_ROUND = 14         # Full Height, Top Width, Bottom Radius
    MODBASKETHANDLE = 15    # Full Height, Bottom Width, Top Radius
    EGG = 16                # Full Height
    HORSESHOE = 17          # Full Height Gothic Full Height
    GOTHIC = 18             # Full Height
    CATENARY = 19           # Full Height
    SEMIELLIPTICAL = 20     # Full Height
    BASKETHANDLE = 21       # Full Height
    SEMICIRCULAR = 22       # Full Height
    IRREGULAR = 23          # TransectCoordinates (Natural Channel)
    CUSTOM = 24             # Full Height, ShapeCurveCoordinates


class CrossSection(Section):
    """A cross section of a Conduit, Orifice, or Weir

    Attributes:
        link (str): name of the conduit, orifice, or weir this is a cross-section of.
        shape (CrossSectionShape): name of cross-section shape.
        geometry1 (str): full height of the cross-section (ft or m)
        geometry2 (str): auxiliary parameters (width, side slopes, etc.)
        geometry3 (str): auxiliary parameters (width, side slopes, etc.)
        geometry4 (str): auxiliary parameters (width, side slopes, etc.)
        barrels (str): number of barrels (i.e., number of parallel pipes of equal size, slope, and
                       roughness) associated with a conduit (default is 1).
        culvert_code (str): name of conduit inlet geometry if it is a culvert subject to possible inlet flow control
        curve (str): associated Shape Curve ID that defines how width varies with depth.
        transect (str): name of cross-section geometry of an irregular channel
    """

    field_format_shape =     "{:16}\t{:12}\t{:16}\t{:10}\t{:10}\t{:10}\t{:10}\t{:10}"
    field_format_custom =    "{:16}\t{:12}\t{:16}\t{:10}"
    field_format_irregular = "{:16}\t{:12}\t{:16}"

    def __init__(self, new_text=None):
        if new_text:
            self.set_text(new_text)  # set_text will call __init__ without new_text to do the initialization below
        else:
            Section.__init__(self)

            self.link = ''
            """name of the conduit, orifice, or weir this is a cross-section of."""

            self.shape = CrossSectionShape.NotSet
            """cross-section shape"""

            self.geometry1 = ''
            """float as str: full height of the cross-section (ft or m)"""

            self.geometry2 = ''
            """float as str: auxiliary parameters (width, side slopes, etc.)"""

            self.geometry3 = ''
            """float as str: auxiliary parameters (width, side slopes, etc.)"""

            self.geometry4 = ''
            """float as str: auxiliary parameters (width, side slopes, etc.)"""

            self.barrels = ''
            """float: number of barrels (i.e., number of parallel pipes of equal size, slope, and
            roughness) associated with a conduit (default is 1)."""

            self.culvert_code = ''
            """code number for the conduits inlet geometry if it is a culvert subject to possible inlet flow control"""

            self.curve = ''
            """str: associated Shape Curve ID that defines how width varies with depth."""

            self.transect = ''
            """str: name of cross-section geometry of an irregular channel"""

    def get_text(self):
        inp = ''
        if self.comment:
            inp = self.comment + '\n'
        if self.shape == CrossSectionShape.CUSTOM:
            inp += self.field_format_custom.format(self.link, self.shape.name, self.geometry1, self.curve, self.barrels)
        elif self.shape == CrossSectionShape.IRREGULAR:
            inp += self.field_format_irregular.format(self.link, self.shape.name, self.transect)
        else:
            inp += self.field_format_shape.format(self.link,
                                                  self.shape.name,
                                                  self.geometry1,
                                                  self.geometry2,
                                                  self.geometry3,
                                                  self.geometry4,
                                                  self.barrels,
                                                  self.culvert_code)
        return inp

    def set_text(self, new_text):
        self.__init__()
        new_text = self.set_comment_check_section(new_text)
        fields = new_text.split()
        if len(fields) > 0:
            self.link = fields[0]
        if len(fields) > 1:
            self.setattr_keep_type("shape", fields[1])
        if self.shape == CrossSectionShape.CUSTOM:
            if len(fields) > 2:
                self.geometry1 = fields[2]
            if len(fields) > 3:
                self.curve = fields[3]
            if len(fields) > 4:
                self.barrels = fields[4]
                if len(fields) > 6 and fields[6].isdigit():  # Old interface saves CUSTOM barrels in this field.
                    self.barrels = fields[6]
        elif self.shape == CrossSectionShape.IRREGULAR:
            if len(fields) > 2:
                self.transect = fields[2]
        else:
            if len(fields) > 2:
                self.geometry1 = fields[2]
            if len(fields) > 3:
                self.geometry2 = fields[3]
            if len(fields) > 4:
                self.geometry3 = fields[4]
            if len(fields) > 5:
                self.geometry4 = fields[5]
            if len(fields) > 6:
                self.barrels = fields[6]
            if len(fields) > 7:
                self.culvert_code = fields[7]


class Transects(Section):

    SECTION_NAME = "[TRANSECTS]"
    DEFAULT_COMMENT = ";;Transect Data in HEC-2 format"

    def __init__(self):
        Section.__init__(self)
        self.list_type = Transect

    def set_text(self, new_text):
        self.value = []
        item_lines = []
        found_non_comment = False
        for line in new_text.splitlines():
            if line.startswith(";;") or line.startswith('['):
                self.set_comment_check_section(line)
            elif line.startswith(';'):
                if found_non_comment:  # This comment must be the start of the next one, so build the previous one
                    try:
                        make_one = self.list_type()
                        make_one.set_text('\n'.join(item_lines))
                        self.value.append(make_one)
                        item_lines = []
                        found_non_comment = False
                    except Exception as e:
                        print("Could not create object from: " + line + '\n' + str(e) + '\n' + str(traceback.print_exc()))
                item_lines.append(line)
            elif not line.strip():  # add blank row as a comment item in self.value list
                comment = Section()
                comment.name = "Comment"
                comment.value = ''
                self.value.append(comment)
            else:
                item_lines.append(line)
                found_non_comment = True

        if found_non_comment:  # Found a final one that has not been built yet, build it now
            try:
                make_one = self.list_type()
                make_one.set_text('\n'.join(item_lines))
                self.value.append(make_one)
            except Exception as e:
                print("Could not create object from: " + line + '\n' + str(e) + '\n' + str(traceback.print_exc()))

    def get_text(self):
        """Contents of this section formatted for writing to file"""
        if self.value or (self.comment and self.comment != self.DEFAULT_COMMENT):
            text_list = [self.name]
            if self.comment:
                text_list.append(self.comment)
            else:
                text_list.append(self.DEFAULT_COMMENT)
            for item in self.value:
                item_str = str(item)
                text_list.append(item_str.rstrip('\n'))  # strip any newlines from end of each item
            return '\n'.join(text_list)
        else:
            return ''


class Transect(Section):
    """the cross-section geometry of a natural channel or conduit with irregular shapes"""

    field_format_nc = "NC\t{:8}\t{:8}\t{:8}"
    field_format_x1 = "X1\t{:16}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}\t{:8}"
    field_format_gr = "\t{:8}\t{:8}"

    def __init__(self, new_text=None):
        if new_text:
            self.set_text(new_text)  # set_text will call __init__ without new_text to do the initialization below
        else:
            Section.__init__(self)

            self.name = ''
            """Transect Name"""

            self.n_left = ''  # Manning's n of right overbank portion of channel. Use 0 if no change from previous NC line.
            self.n_right = ''  # Manning's n of right overbank portion of channel. Use 0 if no change from previous NC line.
            self.n_channel = ''  # Manning's n of main channel portion of channel. Use 0 if no change from previous NC line.
            self.overbank_left = ''   # station position which ends the left overbank portion of the channel (ft or m).
            self.overbank_right = ''  # station position which begins the right overbank portion of the channel (ft or m).
            self.stations_modifier = '0'  # factor by which distances between stations should be multiplied to increase (or decrease) the width of the channel (enter 0 if not applicable).
            self.elevations_modifier = '0'  # amount added (or subtracted) from the elevation of each station (ft or m).
            self.meander_modifier = '0'  # the ratio of the length of a meandering main channel to the length of the overbank area that surrounds it (use 0 if not applicable).
            self.stations = []          # list of (station, elevation) pairs

    def get_text(self):
        lines = []
        if len(self.stations) > 0:
            if self.comment:
                if self.comment.startswith(';'):
                    lines.append(self.comment)
                else:
                    lines.append(';' + self.comment.replace('\n', '\n;'))
            if self.n_left or self.n_right or self.n_channel:
                if len(self.n_left) == 0:
                    self.n_left = '0'
                if len(self.n_right) == 0:
                    self.n_right = '0'
                if len(self.n_channel) == 0:
                    self.n_channel = '0'
                if len((self.n_left + self.n_right + self.n_channel).replace('.', '').replace('0', '')) > 0:
                    lines.append(self.field_format_nc.format(self.n_left, self.n_right, self.n_channel))
            lines.append(self.field_format_x1.format(self.name,
                                                     len(self.stations),
                                                     self.overbank_left,
                                                     self.overbank_right,
                                                     "0.0", "0.0",
                                                     self.meander_modifier,
                                                     self.stations_modifier,
                                                     self.elevations_modifier))
            line = "GR"
            stations_this_line = 0
            for station in self.stations:
                line += self.field_format_gr.format(station[0], station[1])
                stations_this_line += 1
                if stations_this_line > 4:
                    lines.append(line)
                    line = "GR"
                    stations_this_line = 0
            if stations_this_line > 0:
                lines.append(line)

        return '\n'.join(lines)

    def set_text(self, new_text):
        self.__init__()
        for line in new_text.splitlines():
            line = self.set_comment_check_section(line)
            fields = line.split()
            if len(fields) > 2:
                if fields[0].upper() == "GR":
                    for elev_index in range(1, len(fields) - 1, 2):
                        self.stations.append((fields[elev_index], fields[elev_index + 1]))
                elif len(fields) > 3:
                    if fields[0].upper() == "NC":
                        (self.n_left, self.n_right, self.n_channel) = fields[1:4]
                    elif fields[0].upper() == "X1":
                        self.name = fields[1]
                        self.overbank_left = fields[3]
                        if len(fields) > 4:
                            self.overbank_right = fields[4]
                        if len(fields) > 7:
                            self.meander_modifier = fields[7]
                        if len(fields) > 8:
                            self.stations_modifier = fields[8]
                        if len(fields) > 9:
                            self.elevations_modifier = fields[9]
