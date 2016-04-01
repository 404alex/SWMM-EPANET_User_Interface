import os
import core.swmm.project
import unittest
import inspect

class ProjectTest(unittest.TestCase):
    def __init__(self):
        unittest.TestCase.__init__(self)
        self.my_project = core.swmm.project.Project()

    def runTest(self):
        directory = os.path.dirname(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename))
        for inp_filename in ["Examples/Example1.inp"]:
            self.my_project.read_file(os.path.join(directory, inp_filename))
            assert len(self.my_project.sections) == 43

            # with open(inp_filename + ".written.txt", 'w') as writer:
            #     writer.writelines(self.my_project.get_text())
            # with open(inp_filename + ".written_inp_spaces.inp", 'w') as writer:
            #     writer.writelines('\n'.join(self.my_project.get_text().split()))
            # with open(inp_filename + ".written_orig_spaces.inp", 'w') as writer:
            #     with open(inp_filename, 'r') as read_inp:
            #         writer.writelines('\n'.join(read_inp.read().split()))

            # with open(inp_filename, 'r') as read_inp:
            #     assert ' '.join(self.my_project.get_text().split()) == ' '.join(read_inp.read().split())
