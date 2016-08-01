﻿from core.project_base import Project, Section
from enum import Enum


class BackdropUnits(Enum):
    """units of map dimensions"""
    NONE = 0
    FEET = 1
    METERS = 2
    DEGREES = 3


class BackdropOptions(Section):
    """Identifies a backdrop image and dimensions for the network map"""

    SECTION_NAME = "[BACKDROP]"

    def __init__(self):
        Section.__init__(self)
        self.dimensions = ("0.0", "0.0", "10000.0", "10000.0")  # lst:X_Southwest, Y_Southwest, X_northeast, Y_northeast
        """X and Y coordinates of the lower-left and upper-right corners of the map's bounding rectangle"""

        self.units = BackdropUnits.NONE			# FEET/METERS/DEGREES/NONE
        """specifies the units that the map's dimensions are given in"""

        self.file = '' 		                    # str
        """Name of the file that contains the backdrop image"""

        self.offset = ("0.0", "0.0")            # lst of str (X_offset, Y_offset)
        """Distance the upper-left corner of the backdrop image is offset from the map's bounding rectangle (X, Y)"""

    def get_text(self):
        if self.file:
            text_list = [BackdropOptions.SECTION_NAME]
            if self.dimensions:
                text_list.append(" {:17}\t{:16}\t{:16}\t{:16}\t{:16}".format("DIMENSIONS",
                                 self.dimensions[0], self.dimensions[1], self.dimensions[2], self.dimensions[3]))
            if self.units is not None:
                if isinstance(self.units, Enum):
                    units_name = self.units.name
                else:
                    units_name = str(self.units)
                text_list.append(" {:17}\t{}".format("UNITS", units_name))
            if self.file:
                text_list.append(" {:17}\t{}".format("FILE", self.file))
            if self.offset and len(self.offset) > 1:
                text_list.append(" {:17}\t{:16}\t{:16}".format("OFFSET", self.offset[0], self.offset[1]))
            return '\n'.join(text_list)
        else:
            return ''

    def set_text(self, new_text):
        self.__init__()
        for line in new_text.splitlines():
            try:
                line = self.set_comment_check_section(line)
                fields = line.split()
                if len(fields) > 1:
                    if fields[0].lower() == "dimensions" and len(fields) > 4:
                        self.dimensions = fields[1:5]
                    elif fields[0].lower() == "offset" and len(fields) > 2:
                        self.offset = (fields[1], fields[2])
                    else:
                        self.setattr_keep_type(Project.format_as_attribute_name(fields[0]), fields[1])
            except:
                print("BackdropOptions skipping input line: " + line)
