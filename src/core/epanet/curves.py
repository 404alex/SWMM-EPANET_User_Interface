from enum import Enum


class CurveType(Enum):
    """Curve Type"""
    PUMP = 1
    EFFICIENCY = 2
    VOLUME = 3
    HEAD_LOSS = 4


class Curve:
    """Defines data curves and their X,Y points"""

    field_format = " {:16}\t{:12}\t{:12}\n"

    def __init__(self):
        self.curve_id = ""			# string
        """Curve ID Label"""

        self.description = ""   # string
        """Curve description"""

        self.curve_type = CurveType.PUMP			# PUMP, EFFICIENCY, VOLUME, or HEAD_LOSS
        """Curve type"""

        self.curve_xy = []		# list of (x, y) tuples
        """X, Y Values"""

    @property
    def text(self):
        """format contents of this item for writing to file"""
        inp = ";{}: {}".format(self.curve_type.name, self.description)
        for xy in self.curve_xy:
            inp += Curve.field_format.format(self.curve_id, xy[0], xy[1])
        return inp

    @text.setter
    def text(self, new_text):
        comment_split = str.split(new_text, ';', 1)
        if len(comment_split) == 2:
            # TODO: split on colon and set self.curve_type = CurveType[colon_split[0]]
            new_text = comment_split[0]
            self.description = comment_split[1]
        fields = new_text.split()
        self.curve_id = fields[0]
        self.curve_xy.append((fields[1], fields[2]))

