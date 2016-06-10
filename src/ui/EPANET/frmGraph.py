import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
from PyQt4.QtGui import QMessageBox
import matplotlib.pyplot as plt
import core.epanet.project
from core.epanet.reports import Reports
from ui.convenience import all_list_items, selected_list_items
from ui.model_utility import transl8
from ui.EPANET.frmGraphDesigner import Ui_frmGraph
from Externals.epanet.outputapi.ENOutputWrapper import *
from Externals.epanet.outputapi.outputapi import ENR_demand, ENR_head, ENR_pressure, ENR_quality
from core.graph import EPANET as graphEPANET

class frmGraph(QtGui.QMainWindow, Ui_frmGraph):

    def __init__(self, main_form):
        QtGui.QMainWindow.__init__(self, main_form)
        self.help_topic = "epanet/src/src/Graph_Se.htm"
        self.setupUi(self)
        self.cmdAdd.setVisible(False)
        self.cmdDelete.setVisible(False)
        self.cmdUp.setVisible(False)
        self.cmdDown.setVisible(False)
        QtCore.QObject.connect(self.cmdOK, QtCore.SIGNAL("clicked()"), self.cmdOK_Clicked)
        QtCore.QObject.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"), self.cmdCancel_Clicked)
        QtCore.QObject.connect(self.rbnNodes, QtCore.SIGNAL("clicked()"), self.rbnNodes_Clicked)
        QtCore.QObject.connect(self.rbnLinks, QtCore.SIGNAL("clicked()"), self.rbnLinks_Clicked)

        QtCore.QObject.connect(self.rbnTime, QtCore.SIGNAL("clicked()"), self.rbnTime_Clicked)
        QtCore.QObject.connect(self.rbnProfile, QtCore.SIGNAL("clicked()"), self.rbnProfile_Clicked)
        QtCore.QObject.connect(self.rbnContour, QtCore.SIGNAL("clicked()"), self.rbnContour_Clicked)
        QtCore.QObject.connect(self.rbnFrequency, QtCore.SIGNAL("clicked()"), self.rbnFrequency_Clicked)
        QtCore.QObject.connect(self.rbnSystem, QtCore.SIGNAL("clicked()"), self.rbnSystem_Clicked)

        self.cboTime.currentIndexChanged.connect(self.cboTime_currentIndexChanged)

        self.lstToGraph.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self._main_form = main_form
        self.time_linked_graphs = []

    def set_from(self, project, output):
        self.project = project
        self.output = output
        self.report = Reports(project, output)
        self.cboTime.clear()
        if project and self.output:
            for time_index in range(0, self.output.numPeriods):
                self.cboTime.addItem(self.output.get_time_string(time_index))
            self.rbnNodes.setChecked(True)
            self.rbnNodes_Clicked()

    def rbnNodes_Clicked(self):
        if self.rbnNodes.isChecked():
            self.gbxToGraph.setTitle(transl8("frmGraph", "Nodes to Graph", None))
            self.cboParameter.clear()
            self.cboParameter.addItems(ENR_NodeAttributeNames)
            self.lstToGraph.clear()
            # for index in range(0, self.output.nodeCount - 1):
            #     self.lstToGraph.addItem(str(self.output.get_NodeID(index)))
            for node_id in self.report.all_node_ids():
                self.lstToGraph.addItem(node_id)

    def rbnLinks_Clicked(self):
        if self.rbnLinks.isChecked():
            self.gbxToGraph.setTitle(transl8("frmGraph", "Links to Graph", None))
            self.cboParameter.clear()
            self.cboParameter.addItems(ENR_LinkAttributeNames)
            self.lstToGraph.clear()
            self.lstToGraph.addItems(self.report.all_link_ids())

    def rbnTime_Clicked(self):
        self.cboParameter.setEnabled(True)
        self.gbxParameter.setEnabled(True)
        self.cboTime.setEnabled(False)
        self.gbxTime.setEnabled(False)
        self.gbxObject.setEnabled(True)
        self.rbnNodes.setEnabled(True)
        self.rbnLinks.setEnabled(True)
        self.gbxToGraph.setEnabled(True)
        self.lstToGraph.setEnabled(True)

    def rbnProfile_Clicked(self):
        self.cboParameter.setEnabled(True)
        self.gbxParameter.setEnabled(True)
        self.cboTime.setEnabled(True)
        self.gbxTime.setEnabled(True)
        self.gbxObject.setEnabled(False)
        # self.rbnNodes.setChecked(True)
        # self.rbnNodes.setEnabled(False)
        # self.rbnLinks.setEnabled(False)
        self.gbxToGraph.setEnabled(True)
        self.lstToGraph.setEnabled(True)

    def rbnContour_Clicked(self):
        self.cboParameter.setEnabled(True)
        self.gbxParameter.setEnabled(True)
        self.cboTime.setEnabled(True)
        self.gbxTime.setEnabled(True)
        self.gbxObject.setEnabled(False)
        self.rbnNodes.setEnabled(False)
        self.rbnLinks.setEnabled(False)
        self.gbxToGraph.setEnabled(False)
        self.lstToGraph.setEnabled(False)

    def rbnFrequency_Clicked(self):
        self.cboParameter.setEnabled(True)
        self.gbxParameter.setEnabled(True)
        self.cboTime.setEnabled(True)
        self.gbxTime.setEnabled(True)
        self.gbxObject.setEnabled(True)
        self.rbnNodes.setEnabled(True)
        self.rbnLinks.setEnabled(True)
        self.gbxToGraph.setEnabled(False)
        self.lstToGraph.setEnabled(False)

    def rbnSystem_Clicked(self):
        self.cboParameter.setEnabled(False)
        self.gbxParameter.setEnabled(False)
        self.cboTime.setEnabled(False)
        self.gbxTime.setEnabled(False)
        self.gbxObject.setEnabled(False)
        self.rbnNodes.setEnabled(False)
        self.rbnLinks.setEnabled(False)
        self.gbxToGraph.setEnabled(False)
        self.lstToGraph.setEnabled(False)

    def cboTime_currentIndexChanged(self):
        time_index = self.cboTime.currentIndex()
        if time_index >= 0:
            for graph in self.time_linked_graphs:
                graph[-1] = time_index
                graph[0](*graph[1:])

    def cmdOK_Clicked(self):
        attribute_index = self.cboParameter.currentIndex()
        if self.rbnNodes.isChecked():
            get_index = self.output.get_NodeIndex
            get_value = self.output.get_NodeValue
            get_series = self.output.get_NodeSeries
            parameter_code = ENR_NodeAttributes[attribute_index]
            units = ENR_NodeAttributeUnits[attribute_index][self.output.unit_system]

        else:
            get_index = self.output.get_LinkIndex
            get_value = self.output.get_LinkValue
            get_series = self.output.get_LinkSeries
            parameter_code = ENR_LinkAttributes[attribute_index]
            units = ENR_LinkAttributeUnits[attribute_index][self.output.unit_system]

        parameter_label = self.cboParameter.currentText()
        if units:
            parameter_label += ' (' + units + ')'
        time_index = self.cboTime.currentIndex()

        if self.rbnTime.isChecked():  # TODO: use get_series instead of get_value if it is more efficient
            graphEPANET.plot_time(self.output, get_index, get_value, parameter_code, parameter_label, selected_list_items(self.lstToGraph))

        if self.rbnSystem.isChecked():
            graphEPANET.plot_system_flow()

        if time_index < 0 and (self.rbnProfile.isChecked() or self.rbnFrequency.isChecked()):
            QMessageBox.information(None, self._main_form.model,
                                    "There is no time step currently selected.",
                                    QMessageBox.Ok)
        else:
            if self.rbnProfile.isChecked():
                graph_ids = selected_list_items(self.lstToGraph)
                if not graph_ids:
                    graph_ids = self.report.all_node_ids()
                self.plot_profile(get_index, get_value, parameter_code, parameter_label, time_index, graph_ids)
            if self.rbnFrequency.isChecked():
                graphEPANET.plot_freq(self.output, get_index, get_value, parameter_code, parameter_label,
                                      time_index, all_list_items(self.lstToGraph))

    def plot_profile(self, get_index, get_value, parameter_code, parameter_label, time_index, ids):
        fig = plt.figure()
        if self.rbnNodes.isChecked():
            x_values = self.report.node_distances(ids)
        else:
            x_values = range(0, len(ids))
        self.time_linked_graphs.append([graphEPANET.update_profile, self.output, ids, x_values,
             get_index, get_value, parameter_code, parameter_label, fig.number, time_index])
        graphEPANET.update_profile(self.output, ids, x_values,
                                   get_index, get_value, parameter_code, parameter_label, fig.number, time_index)

    def cmdCancel_Clicked(self):
        self.close()
