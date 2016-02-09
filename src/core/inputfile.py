﻿class InputFile(object):
    """Input File Reader and Writer"""

    def __init__(self):
        self.sections = []
        """List of sections in the file"""

    @property
    def text(self):
        section_text_list = []
        for section in self.sections:
            section_text_list.append(str(section.text))
        return '\n'.join(section_text_list)

    @text.setter
    def text(self, new_text):
        self.set_from_text_lines(new_text.splitlines())

    def read_file(self, filename):
        with open(filename, 'r') as inp_reader:
            self.set_from_text_lines(iter(inp_reader))

    def set_from_text_lines(self, lines_iterator):
        """Read as a project file from the lines of text in @param lines_iterator provides"""
        section_index = 1
        section_name = ""
        section_whole = ""
        for line in lines_iterator:
            if line.startswith('['):
                if section_name:
                    self.add_section(section_name, section_whole, section_index)
                    section_index += 1
                section_name = line.rstrip()
                section_whole = line
            else:
                section_whole += line
        if section_name:
            self.add_section(section_name, section_whole, section_index)
            section_index += 1

    def add_section(self, section_name, section_text, section_index):
        new_section = None
        attr_name = InputFile.printable_to_attribute(section_name)
        try:
            section_attr = self.__getattribute__(attr_name)
        except:
            section_attr = None

        if section_attr is None:  # if there is not a class associated with this name, read it as generic Section
            new_section = Section()
            new_section.name = section_name
            new_section.index = section_index
            new_section.value = section_text
            new_section.value_original = section_text
        else:
            section_class = type(section_attr)
            if section_class is list:
                section_list = []
                list_class = section_attr[0]
                for row in section_text.splitlines()[1:]:  # process each row after the one with the section name
                    if row.startswith(';'):                # if row starts with semicolon, the whole row is a comment
                        comment = Section()
                        comment.name = "Comment"
                        comment.index = section_index
                        comment.value = row
                        comment.value_original = row
                        section_list.append(comment)
                    else:
                        try:
                            if row.strip():
                                make_one = list_class()
                                make_one.text(row)
                                section_list.append(make_one)
                        except:
                            make_one = None
                new_section = Section()
                new_section.name = section_name
                new_section.index = section_index
                new_section.value = section_list
                new_section.value_original = section_text
            else:
                new_section = section_class()
                if hasattr(new_section, "index"):
                    new_section.index = section_index
                if hasattr(new_section, "value"):
                    new_section.value = section_text
                if hasattr(new_section, "value_original"):
                    new_section.value_original = section_text
                if hasattr(new_section, "text"):
                    new_section.text = section_text
        if new_section is not None:
            self.sections.append(new_section)
            if section_attr is not None:
                self.__setattr__(attr_name, new_section)

    def find_section(self, section_title):
        for section in self.sections:
            if hasattr(section, "SECTION_NAME"):
                this_section_name = section.SECTION_NAME
            else:
                this_section_name = section.name
            if str(this_section_name).replace('[', '').replace(']', '').lower() == section_title.lower():
                return section
        return None

    @staticmethod
    def printable_to_attribute(name):
        """@param name is as it appears in text input file, return it formatted as a class attribute name"""
        return name.lower().replace(' ', '_').replace('[', '').replace(']', '')


class Section(object):
    """Any section or sub-section or value in an input file"""

    field_format = " {:19}\t{}"

    def __init__(self):
        self.name = "Unnamed"
        """Name of the item"""

        if hasattr(self, "SECTION_NAME"):
            self.name = self.SECTION_NAME

        self.value = ""
        """Current value of the item as it appears in an InputFile"""

        self.value_original = None
        """Original value of the item as read from an InputFile during this session"""

        self.index = -1
        """Index indicating the order in which this item was read
           (used for keeping items in the same order when written)"""

        self.comment = ""
        """A user-specified header and/or comment about the section"""

    @property
    def text(self):
        """Contents of this section formatted for writing to file"""

        if hasattr(self, "field_dict") and self.field_dict:
            text_list = []
            if self.name and self.name.startswith('['):
                text_list.append(self.name)
            for label, attr_name in self.field_dict.items():
                if label and attr_name and hasattr(self, attr_name):
                    attr_value = str(getattr(self, attr_name))
                    if attr_value:
                        text_list.append(self.field_format.format(label, attr_value))
            if text_list:
                return '\n'.join(text_list)

        if isinstance(self.value, basestring):
            return self.value
        elif isinstance(self.value, (list, tuple)):
            text_list = [self.name]
            for item in self.value:
                if hasattr(item, "text"):
                    text_list.append(item.text)
                else:
                    text_list.append(str(item))
            return '\n'.join(text_list)
        elif self.value is None:
            return ''
        else:
            return str(self.value)

    @text.setter
    def text(self, new_text):
        """Read this section from the text representation"""

        self.value = new_text
        for line in new_text.splitlines():
            # first split out any comment after a semicolon
            comment_split = str.split(line, ';', 1)
            if len(comment_split) == 2:
                line = comment_split[0]
                if self.comment:
                    self.comment += '\n'
                self.comment += ';' + comment_split[1]

            if not line.startswith('[') and line.strip():
                # Set fields from field_dict if this section has one
                attr_name = ""
                tried_set = False
                if hasattr(self, "field_dict") and self.field_dict:
                    lower_line = line.lower().strip()
                    for dict_tuple in self.field_dict.items():
                        key = dict_tuple[0]
                        # if this line starts with this key followed by a space or tab
                        if lower_line.startswith(key.lower()) and lower_line[len(key)] in (' ', '\t'):
                            test_attr_name = dict_tuple[1]
                            if hasattr(self, test_attr_name):
                                attr_name = test_attr_name
                                attr_value = line[len(key) + 1:].strip()
                                break
                else:  # This section does not have a field_dict, try to set its fields anyway
                    line_list = line.split()
                    if len(line_list) > 1:
                        if len(line_list) == 2:
                            test_attr_name = line_list[0].lower()
                            if hasattr(self, test_attr_name):
                                attr_name = test_attr_name
                                attr_value = line_list[1]
                        else:
                            for value_start in (1, 2):
                                for connector in ('', '_'):
                                    test_attr_name = connector.join(line_list[:value_start]).lower()
                                    if hasattr(self, test_attr_name):
                                        attr_name = test_attr_name
                                        attr_value = ' '.join(line_list[value_start:])
                                        break
                if attr_name:
                    try:
                        tried_set = True
                        # If existing value is an int or float, make sure new value is too, else str
                        old_value = getattr(self, attr_name, "")
                        if isinstance(old_value, int):
                            setattr(self, attr_name, int(attr_value.replace(' ', '')))
                        elif isinstance(old_value, float):
                            setattr(self, attr_name, float(attr_value.replace(' ', '')))
                        else:
                            setattr(self, attr_name, attr_value)
                    except:
                        print("Section.text could not set " + attr_name)
                if not tried_set:
                    print("Section.text skipped: " + line)
