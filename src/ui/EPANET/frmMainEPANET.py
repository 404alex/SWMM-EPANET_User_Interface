import os, sys
os.environ['QT_API'] = 'pyqt'
import sip
for typ in ["QString","QVariant", "QDate", "QDateTime", "QTextStream", "QTime", "QUrl"]:
    sip.setapi(typ, 2)
import traceback
import webbrowser
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox, QFileDialog, QColor

from ui.model_utility import QString, from_utf8, transl8, process_events
from ui.help import HelpHandler
from ui.frmMain import frmMain, ModelLayers
from ui.EPANET.frmEnergyOptions import frmEnergyOptions
from ui.EPANET.frmHydraulicsOptions import frmHydraulicsOptions
from ui.EPANET.frmMapBackdropOptions import frmMapBackdropOptions
from ui.EPANET.frmQualityOptions import frmQualityOptions
from ui.EPANET.frmReactionsOptions import frmReactionsOptions
from ui.EPANET.frmReportOptions import frmReportOptions
from ui.EPANET.frmTimesOptions import frmTimesOptions
from ui.EPANET.frmTitle import frmTitle

from ui.EPANET.frmAbout import frmAbout
from ui.EPANET.frmControls import frmControls
from ui.EPANET.frmJunction import frmJunction
from ui.EPANET.frmReservoir import frmReservior
from ui.EPANET.frmTank import frmTank
from ui.EPANET.frmPipe import frmPipe
from ui.EPANET.frmPump import frmPump
from ui.EPANET.frmValve import frmValve
from ui.EPANET.frmCurveEditor import frmCurveEditor
from ui.EPANET.frmPatternEditor import frmPatternEditor
from ui.EPANET.frmSourcesQuality import frmSourcesQuality
from ui.EPANET.frmDemands import frmDemands
from ui.EPANET.frmGraph import frmGraph
from ui.EPANET.frmTable import frmTable
from ui.EPANET.frmEnergyReport import frmEnergyReport
from ui.EPANET.frmCalibrationData import frmCalibrationData
from ui.EPANET.frmCalibrationReportOptions import frmCalibrationReportOptions
from ui.frmGenericPropertyEditor import frmGenericPropertyEditor

from core.epanet.epanet_project import EpanetProject as Project
from core.epanet.inp_reader_project import ProjectReader
from core.epanet.inp_writer_project import ProjectWriter
from core.epanet.hydraulics.node import Junction
from core.epanet.hydraulics.node import Reservoir
from core.epanet.hydraulics.node import Tank
from core.epanet.hydraulics.link import Pipe
from core.epanet.hydraulics.link import Pump
from core.epanet.hydraulics.link import Valve
from core.epanet.labels import Label

from core.epanet.patterns import Pattern
from core.epanet.curves import Curve

import core.epanet.reports as reports
from Externals.epanet.model.epanet2 import ENepanet
from Externals.epanet.outputapi import ENOutputWrapper
from frmRunEPANET import frmRunEPANET

import Externals.epanet.outputapi.ENOutputWrapper as ENO
import ui.convenience


class frmMainEPANET(frmMain):
    """Main form for EPANET user interface, based on frmMain which is shared with SWMM."""

    # Variables used to populate the tree control
    # Each item is a list: label plus either editing form for this section or a child list.
    # Special cases may just have a label and no editing form or children.
    # *_items are a lists of items in a section
    tree_options_Hydraulics = ["Hydraulics", frmHydraulicsOptions]
    tree_options_Quality = ["Quality", frmQualityOptions]
    tree_options_Reactions = ["Reactions", frmReactionsOptions]
    tree_options_Times = ["Times", frmTimesOptions]
    tree_options_Energy = ["Energy", frmEnergyOptions]
    tree_options_Report = ["Report", frmReportOptions]
    tree_options_MapBackdrop = ["Map/Backdrop", frmMapBackdropOptions]
    tree_options_items = [tree_options_Hydraulics,
                          tree_options_Quality,
                          tree_options_Reactions,
                          tree_options_Times,
                          tree_options_Energy,
                          tree_options_Report,
                          tree_options_MapBackdrop]

    tree_controls_Simple = ["Simple", frmControls, ["EPANET Simple Controls", "CONTROLS"]]
    tree_controls_RuleBased = ["Rule-Based", frmControls, ["EPANET Rule-Based Controls", "RULES"]]
    tree_controls_items = [tree_controls_Simple,
                           tree_controls_RuleBased]

    tree_TitleNotes = ["Title/Notes", frmTitle]
    tree_Options = ["Options", tree_options_items]
    tree_Junctions = ["Junctions", frmJunction]
    tree_Reservoirs = ["Reservoirs", frmReservior]
    tree_Tanks = ["Tanks", frmTank]
    tree_Pipes = ["Pipes", frmPipe]
    tree_Pumps = ["Pumps", frmPump]
    tree_Valves = ["Valves", frmValve]
    tree_Labels = ["Labels", None]
    tree_Patterns = ["Patterns", frmPatternEditor]
    tree_Curves = ["Curves", frmCurveEditor]
    tree_Controls = ["Controls", tree_controls_items]
    tree_top_items = [tree_TitleNotes,
                      tree_Options,
                      tree_Junctions,
                      tree_Reservoirs,
                      tree_Tanks,
                      tree_Pipes,
                      tree_Pumps,
                      tree_Valves,
                      tree_Labels,
                      tree_Patterns,
                      tree_Curves,
                      tree_Controls]

    def __init__(self, q_application):
        frmMain.__init__(self, q_application)
        self.model = "EPANET"
        self.model_path = ''  # Set this only if needed later when running model
        self.output = None    # Set this when model output is available
        self.status_suffix = "_status.txt"
        self.status_file_name = ''  # Set this when model status is available
        self.output_filename = ''   # Set this when model output is available
        self.project_type = Project  # Use the model-specific Project as defined in core.epanet.project
        self.project_reader_type = ProjectReader
        self.project_writer_type = ProjectWriter
        self.project = Project()
        self.assembly_path = os.path.dirname(os.path.abspath(__file__))
        self.on_load(tree_top_item_list=self.tree_top_items)
        if self.map_widget:  # initialize empty model map layers, ready to have model elements added
            self.model_layers = ModelLayersEPANET(self.map_widget)

        HelpHandler.init_class(os.path.join(self.assembly_path, "epanet.qhc"))
        self.help_topic = ""  # TODO: specify topic to open when Help key is pressed on main form
        self.helper = HelpHandler(self)

        self.actionStatus_ReportMenu = QtGui.QAction(self)
        self.actionStatus_ReportMenu.setObjectName(from_utf8("actionStatus_ReportMenu"))
        self.actionStatus_ReportMenu.setText(transl8("frmMain", "Status", None))
        self.actionStatus_ReportMenu.setToolTip(transl8("frmMain", "Display Simulation Status", None))
        self.menuReport.addAction(self.actionStatus_ReportMenu)
        QtCore.QObject.connect(self.actionStatus_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_status)

        self.actionEnergy_ReportMenu = QtGui.QAction(self)
        self.actionEnergy_ReportMenu.setObjectName(from_utf8("actionEnergy_ReportMenu"))
        self.actionEnergy_ReportMenu.setText(transl8("frmMain", "Energy", None))
        self.actionEnergy_ReportMenu.setToolTip(transl8("frmMain", "Display Simulation Energy", None))
        self.menuReport.addAction(self.actionEnergy_ReportMenu)
        QtCore.QObject.connect(self.actionEnergy_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_energy)

        self.actionCalibration_ReportMenu = QtGui.QAction(self)
        self.actionCalibration_ReportMenu.setObjectName(from_utf8("actionCalibration_ReportMenu"))
        self.actionCalibration_ReportMenu.setText(transl8("frmMain", "Calibration", None))
        self.actionCalibration_ReportMenu.setToolTip(transl8("frmMain", "Display Simulation Calibration", None))
        self.menuReport.addAction(self.actionCalibration_ReportMenu)
        QtCore.QObject.connect(self.actionCalibration_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_calibration)

        self.actionReaction_ReportMenu = QtGui.QAction(self)
        self.actionReaction_ReportMenu.setObjectName(from_utf8("actionReaction_ReportMenu"))
        self.actionReaction_ReportMenu.setText(transl8("frmMain", "Reaction", None))
        self.actionReaction_ReportMenu.setToolTip(transl8("frmMain", "Display Simulation Reaction", None))
        self.menuReport.addAction(self.actionReaction_ReportMenu)
        QtCore.QObject.connect(self.actionReaction_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_reaction)

        self.actionFull_ReportMenu = QtGui.QAction(self)
        self.actionFull_ReportMenu.setObjectName(from_utf8("actionFull_ReportMenu"))
        self.actionFull_ReportMenu.setText(transl8("frmMain", "Full...", None))
        self.actionFull_ReportMenu.setToolTip(transl8("frmMain", "Save full report as text file", None))
        self.menuReport.addAction(self.actionFull_ReportMenu)
        QtCore.QObject.connect(self.actionFull_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_full)

        self.actionGraph_ReportMenu = QtGui.QAction(self)
        self.actionGraph_ReportMenu.setObjectName(from_utf8("actionGraph_ReportMenu"))
        self.actionGraph_ReportMenu.setText(transl8("frmMain", "Graph...", None))
        self.actionGraph_ReportMenu.setToolTip(transl8("frmMain", "Display graph selection options", None))
        self.menuReport.addAction(self.actionGraph_ReportMenu)
        QtCore.QObject.connect(self.actionGraph_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_graph)

        self.actionTable_ReportMenu = QtGui.QAction(self)
        self.actionTable_ReportMenu.setObjectName(from_utf8("actionTable_ReportMenu"))
        self.actionTable_ReportMenu.setText(transl8("frmMain", "Table...", None))
        self.actionTable_ReportMenu.setToolTip(transl8("frmMain", "Display table selection options", None))
        self.menuReport.addAction(self.actionTable_ReportMenu)
        QtCore.QObject.connect(self.actionTable_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_table)

        self.Help_Topics_Menu = QtGui.QAction(self)
        self.Help_Topics_Menu.setObjectName(from_utf8("Help_Topics_Menu"))
        self.Help_Topics_Menu.setText(transl8("frmMain", "Help Topics", None))
        self.Help_Topics_Menu.setToolTip(transl8("frmMain", "Display Help Topics", None))
        self.menuHelp.addAction(self.Help_Topics_Menu)
        QtCore.QObject.connect(self.Help_Topics_Menu, QtCore.SIGNAL('triggered()'), self.help_topics)

        self.Help_About_Menu = QtGui.QAction(self)
        self.Help_About_Menu.setObjectName(from_utf8("Help_About_Menu"))
        self.Help_About_Menu.setText(transl8("frmMain", "About", None))
        self.Help_About_Menu.setToolTip(transl8("frmMain", "About EPANET", None))
        self.menuHelp.addAction(self.Help_About_Menu)
        QtCore.QObject.connect(self.Help_About_Menu, QtCore.SIGNAL('triggered()'), self.help_about)

        self.cbFlowUnits.clear()
        self.cbFlowUnits.addItems(['Flow Units: CFS','Flow Units: GPM','Flow Units: MGD','Flow Units: IMGD',
                                   'Flow Units: AFD','Flow Units: LPS','Flow Units: LPM','Flow Units: MLD',
                                   'Flow Units: CMH','Flow Units: CMD'])
        self.cbFlowUnits.currentIndexChanged.connect(self.cbFlowUnits_currentIndexChanged)
        self.cbOffset.setVisible(False)

        self.cboMapSubcatchments.setVisible(False)
        self.lblMapSubcatchments.setVisible(False)
        self.add_map_constituents()
        self.cboMapNodes.currentIndexChanged.connect(self.cboMap_currentIndexChanged)
        self.cboMapLinks.currentIndexChanged.connect(self.cboMap_currentIndexChanged)

    def add_map_constituents(self):
        self.cboMapNodes.clear()
        self.cboMapNodes.addItems(['None','Elevation','Base Demand','Initial Quality'])
        self.cboMapLinks.clear()
        self.cboMapLinks.addItems(['None','Length','Diameter','Roughness','Bulk Coeff.','Wall Coeff.'])
        if self.output:
            # Add object type labels to map combos if there are any of each type in output
            object_type = ENO.swmm_output_get_object_type('Nodes')
            if object_type:
                attribute_names = [attribute.name for attribute in object_type.attributes]
                for item in attribute_names:
                    self.cboMapNodes.addItem(item)
            object_type = ENO.swmm_output_get_object_type('Links')
            if object_type:
                attribute_names = [attribute.name for attribute in object_type.attributes]
                for item in attribute_names:
                    self.cboMapLinks.addItem(item)

    def cboMap_currentIndexChanged(self):
        pass

    def cbFlowUnits_currentIndexChanged(self):
        import core.epanet.options.hydraulics
        self.project.options.hydraulics.flow_units = core.epanet.options.hydraulics.FlowUnits[self.cbFlowUnits.currentText()[12:]]

    def report_status(self):
        print "report_status"
        if not os.path.isfile(self.status_file_name):
            prefix, extension = os.path.splitext(self.project.file_name)
            if os.path.isfile(prefix + self.status_suffix):
                self.status_file_name = prefix + self.status_suffix
        if os.path.isfile(self.status_file_name):
            webbrowser.open_new_tab(self.status_file_name)
        else:
            QMessageBox.information(None, self.model,
                                    "Model status not found.\n"
                                    "Run the model to generate model status.",
                                    QMessageBox.Ok)

    def report_energy(self):
        if self.output:
            self._frmEnergyReport = frmEnergyReport(self)
            self._frmEnergyReport.set_data(self.project, self.output)
            self._frmEnergyReport.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_calibration(self):
        if self.output:
            self._frmCalibrationReportOptions = frmCalibrationReportOptions(self,
                                                                            self.project,
                                                                            self.output)
            self._frmCalibrationReportOptions.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_reaction(self):
        self.reaction_report()
        pass

    def report_full(self):
        if self.output:
            directory = os.path.dirname(self.project.file_name)
            report_file_name = QtGui.QFileDialog.getSaveFileName(self, "Save Full Report As...", directory, "Text files (*.txt)")
            if report_file_name:
                try:
                    reporter = reports.Reports(self.project, self.output)
                    reporter.write_report(report_file_name)
                    webbrowser.open_new_tab(report_file_name)
                except Exception as e1:
                    msg = str(e1) + '\n' + str(traceback.print_exc())
                    print(msg)
                    QMessageBox.information(None, self.model,
                                            "Error writing report to \n" + report_file_name + '\n' + msg,
                                            QMessageBox.Ok)

        else:
            QMessageBox.information(None, self.model,
                                    "There is no model output currently open.\n"
                                    "Model output is automatically opened after model is run.",
                                    QMessageBox.Ok)

    def report_graph(self):
        if self.output:
            self._frmGraph = frmGraph(self)
            self._frmGraph.set_from(self.project, self.output)
            self._frmGraph.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_table(self):
        if self.output:
            self._frmTable = frmTable(self)
            self._frmTable.set_from(self.project, self.output)
            self._frmTable.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def reaction_report(self):
        # Reaction Report'
        if self.output:
            # Find conversion factor to kilograms/day
            ucf = 1.0e6/24
            quality_options = self.project.options.quality
            if 'ug' in str(quality_options.mass_units):
                ucf = 1.0e9/24

            # Get average reaction rates from output file
            bulk, wall, tank, source = self.output.get_reaction_summary()
            bulk /= ucf
            wall /= ucf
            tank /= ucf
            source /= ucf

            if bulk > 0 or wall > 0 or tank > 0 or source > 0:
                footer_text = "Inflow Rate = " + format(source,'0.1f')
            else:
                footer_text = 'No reactions occurred'

            import matplotlib.pyplot as plt

            labels = "%10.1f Tanks" % tank, "%10.1f Bulk" % bulk, "%10.1f Wall" % wall
            sum_reaction = bulk + wall + tank
            size_bulk = bulk / sum_reaction
            size_wall = wall / sum_reaction
            size_tank = tank / sum_reaction
            sizes = [size_tank, size_bulk, size_wall]
            colors = ['green', 'blue', 'red']
            explode = (0, 0, 0)

            plt.figure("Reaction Report")

            plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct='%1.2f%%', shadow=True, startangle=180)

            plt.axis('equal')
            plt.suptitle("Average Reaction Rates (kg/day)", fontsize=16)
            plt.text(0.9,-0.9,footer_text)

            plt.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def calibration_data(self):
        self._frmCalibrationData = frmCalibrationData(self)
        self._frmCalibrationData.show()
        pass

    def get_editor(self, edit_name):
        frm = None
        # First handle special cases where forms need more than simply being created

        # the following items will respond to a click on a node form, not the tree diagram
        if edit_name == 'Labels':
            edit_these = []
            if self.project and self.project.labels:
                if not isinstance(self.project.labels.value, basestring):
                    if isinstance(self.project.labels.value, list):
                        edit_these.extend(self.project.labels.value)
                if len(edit_these) == 0:
                    new_item = Label()
                    new_item.name = "NewLabel"
                    edit_these.append(new_item)
                    self.project.labels.value = edit_these
                else:
                    self.new_item = False
            frm = frmGenericPropertyEditor(self, edit_these, "EPANET Map Label Editor")
            frm.helper = HelpHandler(frm)
            frm.help_topic = "epanet/src/src/maplabeleditordialog.htm"
        elif edit_name == 'Patterns' or edit_name == 'Curves':
            # in these cases the click on the tree diagram populates the lower left list, not directly to an editor
            return None
        elif edit_name == self.tree_Junctions[0] and len(self.project.junctions.value) == 0:
            return None
        elif edit_name == self.tree_Reservoirs[0] and len(self.project.reservoirs.value) == 0:
            return None
        elif edit_name == self.tree_Tanks[0] and len(self.project.tanks.value) == 0:
            return None
        elif edit_name == self.tree_Pipes[0] and len(self.project.pipes.value) == 0:
            return None
        elif edit_name == self.tree_Pumps[0] and len(self.project.pumps.value) == 0:
            return None
        elif edit_name == self.tree_Valves[0] and len(self.project.valves.value) == 0:
            return None
        elif edit_name == self.tree_Labels[0] and len(self.project.labels.value) == 0:
            return None
        else:  # General-purpose case finds most editors from tree information
            frm = self.make_editor_from_tree(edit_name, self.tree_top_items)
        return frm

    def get_editor_with_selected_items(self, edit_name, selected_items):
        return self.make_editor_from_tree(edit_name, self.tree_top_items, selected_items)

    def get_object_list(self, category):
        section = self.project.find_section(category)
        if category == 'Quality' or category == 'Controls':
            return None
        if section and isinstance(section.value, list):
            return [item.name for item in section.value]
        else:
            return None

    def add_object_clicked(self, section_name):
        if section_name == "Patterns":
            new_item = Pattern()
            new_item.name = "NewPattern"
            self.project.patterns.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == "Curves":
            new_item = Curve()
            new_item.name = "NewCurve"
            self.project.curves.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == "Junctions":
            new_item = Junction()
            new_item.name = "New"
            self.project.junctions.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == 'Reservoirs':
            new_item = Reservoir()
            new_item.name = "New"
            self.project.reservoirs.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == 'Tanks':
            new_item = Tank()
            new_item.name = "New"
            self.project.tanks.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == 'Pipes':
            new_item = Pipe()
            new_item.name = "New"
            self.project.pipes.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == 'Pumps':
            new_item = Pump()
            new_item.name = "New"
            self.project.pumps.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == 'Valves':
            new_item = Valve()
            new_item.name = "New"
            self.project.valves.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))
        elif section_name == 'Labels':
            new_item = Label()
            new_item.name = "New"
            self.project.labels.value.append(new_item)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))

    def delete_object_clicked(self, section_name, item_name):
        if section_name == "Patterns":
            for value in self.project.patterns.value:
                if value.name == item_name:
                    self.project.patterns.value.remove(value)
        elif section_name == "Curves":
            for value in self.project.curves.value:
                if value.name == item_name:
                    self.project.curves.value.remove(value)
        elif section_name == "Junctions":
            for value in self.project.junctions.value:
                if value.name == item_name:
                    self.project.junctions.value.remove(value)
        elif section_name == 'Reservoirs':
            for value in self.project.reservoirs.value:
                if value.name == item_name:
                    self.project.reservoirs.value.remove(value)
        elif section_name == 'Tanks':
            for value in self.project.tanks.value:
                if value.name == item_name:
                    self.project.tanks.value.remove(value)
        elif section_name == 'Pipes':
            for value in self.project.pipes.value:
                if value.name == item_name:
                    self.project.pipes.value.remove(value)
        elif section_name == 'Pumps':
            for value in self.project.pumps.value:
                if value.name == item_name:
                    self.project.pumps.value.remove(value)
        elif section_name == 'Valves':
            for value in self.project.valves.value:
                if value.name == item_name:
                    self.project.valves.value.remove(value)
        elif section_name == 'Labels':
            for value in self.project.labels.value:
                if value.name == item_name:
                    self.project.labels.value.remove(value)

    def run_simulation(self):
        # Find input file to run
        file_name = ''
        use_existing = self.project and self.project.file_name and os.path.exists(self.project.file_name)
        if use_existing:
            file_name = self.project.file_name
            # TODO: save if needed, decide whether to save to temp location as previous version did.
        else:
            self.open_project()

        if self.project:
            file_name = self.project.file_name

        if os.path.exists(file_name):
            if not os.path.exists(self.model_path):
                if 'darwin' in sys.platform:
                    lib_name = 'libepanet.dylib.dylib'
                elif 'win' in sys.platform:
                    lib_name = 'epanet2_amd64.dll'
                else:  # Linux
                    lib_name = 'libepanet2_amd64.so'
                self.model_path = self.find_external(lib_name)
            if os.path.exists(self.model_path):
                try:
                    prefix, extension = os.path.splitext(file_name)
                    self.status_file_name = prefix + self.status_suffix
                    self.output_filename = prefix + '.out'
                    if self.output:
                        self.output.close()
                        self.output = None
                    model_api = ENepanet(file_name, self.status_file_name, self.output_filename, self.model_path)
                    frmRun = frmRunEPANET(model_api, self.project, self)
                    self._forms.append(frmRun)
                    frmRun.Execute()
                    self.report_status()
                    self.add_map_constituents()
                    try:
                        self.output = ENOutputWrapper.OutputObject(self.output_filename)
                        return
                    except Exception as e1:
                        print(str(e1) + '\n' + str(traceback.print_exc()))
                        QMessageBox.information(None, self.model,
                                                "Error opening model output:\n {0}\n{1}\n{2}".format(
                                                    self.output_filename, str(e1), str(traceback.print_exc())),
                                                QMessageBox.Ok)
                except Exception as e1:
                    print(str(e1) + '\n' + str(traceback.print_exc()))
                    QMessageBox.information(None, self.model,
                                            "Error running model with library:\n {0}\n{1}\n{2}".format(
                                                self.model_path, str(e1), str(traceback.print_exc())),
                                            QMessageBox.Ok)
                finally:
                    try:
                        if model_api and model_api.isOpen():
                            model_api.ENclose()
                    except:
                        pass
                    return

            # # Could not run with library, try running with executable
            # # Run executable with StatusMonitor0
            # args = []
            # self.modelenv1 = 'EXE_EPANET'
            # program = os.environ[self.modelenv1]
            #
            # exe_name = "epanet2d.exe"
            # exe_path = os.path.join(self.assembly_path, exe_name)
            # if not os.path.exists(exe_path):
            #     pp = os.path.dirname(os.path.dirname(self.assembly_path))
            #     exe_path = os.path.join(pp, "Externals", exe_name)
            # if not os.path.exists(exe_path):
            #     exe_path = QFileDialog.getOpenFileName(self, 'Locate EPANET Executable', '/',
            #                                              'exe files (*.exe)')
            # if os.path.exists(exe_path):
            #     os.environ[self.modelenv1] = exe_path
            # else:
            #     os.environ[self.modelenv1] = ''
            #
            # if not os.path.exists(program):
            #     QMessageBox.information(None, "EPANET", "EPANET Executable not found", QMessageBox.Ok)
            #     return -1
            #
            # args.append(file_name)
            # args.append(prefix + '.txt')
            # args.append(prefix + '.out')
            # status = model_utility.StatusMonitor0(program, args, self, model='EPANET')
            # status.show()
        else:
            QMessageBox.information(None, self.model, self.model + " input file not found", QMessageBox.Ok)

    def help_topics(self):
        self.helper.show_help()

    def help_about(self):
        self._frmAbout = frmAbout(self)
        self._frmAbout.show()

    def open_project_quiet(self, file_name, gui_settings, directory):
        frmMain.open_project_quiet(self, file_name, gui_settings, directory)
        ui.convenience.set_combo(self.cbFlowUnits, 'Flow Units: ' + self.project.options.hydraulics.flow_units.name)

        if self.map_widget:
            try:
                self.model_layers.create_layers_from_project(self.project)
                self.map_widget.zoomfull()
            except Exception as ex:
                print(str(ex) + '\n' + str(traceback.print_exc()))


class ModelLayersEPANET(ModelLayers):
    """
    This class creates and manages the map layers that are directly linked to SWMM model elements.
    Layer names must match the text in the tree control for the corresponding model section.
    """
    def __init__(self, map_widget):
        ModelLayers.__init__(self, map_widget)
        addCoordinates = self.map_widget.addCoordinates
        addLinks = self.map_widget.addLinks
        self.junctions = addCoordinates(None, "Junctions")
        self.reservoirs = addCoordinates(None, "Reservoirs")
        self.tanks = addCoordinates(None, "Tanks")
        self.sources = addCoordinates(None, "Sources")
        self.labels = addCoordinates(None, "Labels")
        self.pumps = addLinks(None, None, "Pumps", "name", QColor('red'), 1)
        self.valves = addLinks(None, None, "Valves", "name", QColor('green'), 2)
        self.pipes = addLinks(None, None, "Pipes", "name", QColor('gray'), 3)
        self.set_lists()

    def set_lists(self):
        self.nodes_layers = [self.junctions, self.reservoirs, self.tanks, self.sources]
        self.all_layers = [self.labels, self.pumps, self.valves, self.pipes]
        self.all_layers.extend(self.nodes_layers)

    def create_layers_from_project(self, project):
        ModelLayers.create_layers_from_project(self, project)
        addCoordinates = self.map_widget.addCoordinates
        addLinks = self.map_widget.addLinks

        # Add new layers containing objects from this project
        self.junctions = addCoordinates(project.junctions.value, "Junctions")
        self.reservoirs = addCoordinates(project.reservoirs.value, "Reservoirs")
        self.tanks = addCoordinates(project.tanks.value, "Tanks")
        self.sources = addCoordinates(project.sources.value, "Sources")
        self.labels = addCoordinates(project.labels.value, "Labels")

        coordinates = project.all_coordinates()
        self.pumps = addLinks(coordinates, project.pumps.value, "Pumps", "name", QColor('red'), 1)
        self.valves = addLinks(coordinates, project.valves.value, "Valves", "name", QColor('green'), 2)
        self.pipes = addLinks(coordinates, project.pipes.value, "Pipes", "name", QColor('gray'), 3)
        self.set_lists()


if __name__ == '__main__':
    application = QtGui.QApplication(sys.argv)
    main_form = frmMainEPANET(application)
    main_form.show()
    sys.exit(application.exec_())
