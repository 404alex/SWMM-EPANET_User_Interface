import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import core.epanet.project
from ui.EPANET.frmDemandsDesigner import Ui_frmDemands


class frmDemands(QtGui.QMainWindow, Ui_frmDemands):

    def __init__(self, main_form=None):
        QtGui.QMainWindow.__init__(self, main_form)
        self.setupUi(self)
        QtCore.QObject.connect(self.cmdOK, QtCore.SIGNAL("clicked()"), self.cmdOK_Clicked)
        QtCore.QObject.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"), self.cmdCancel_Clicked)
        # self.set_from(parent.project)
        self._main_form = main_form
        self.node_id = ''

    def set_from(self, project, node_id):
        self.node_id = node_id
        # find demands in demands table and junctions table
        # section = core.epanet.project.Junction()
        section = project.find_section('JUNCTIONS')
        junctions_list = section.value[0:]
        # assume we want to edit the first one
        # look in demand table first
        # section = core.epanet.project.Demand()
        section = project.find_section('DEMANDS')
        demands_list = section.value[0:]
        # assume we want to edit the first one
        row_count = -1
        for demand in demands_list:
            if demand.junction_id == node_id:
                row_count += 1
                led = QtGui.QLineEdit(str(demand.base_demand))
                self.tblDemands.setItem(row_count,0,QtGui.QTableWidgetItem(led.text()))
                led = QtGui.QLineEdit(str(demand.demand_pattern))
                self.tblDemands.setItem(row_count,1,QtGui.QTableWidgetItem(led.text()))
                led = QtGui.QLineEdit(str(demand.category[1:]))
                self.tblDemands.setItem(row_count,2,QtGui.QTableWidgetItem(led.text()))
                self.junction_only = False
        if row_count == -1:
            # did not find any in demands table, so use whats in junction table
            for junction in junctions_list:
                if junction.id == node_id:
                    row_count += 1
                    led = QtGui.QLineEdit(str(junction.base_demand_flow))
                    self.tblDemands.setItem(row_count,0,QtGui.QTableWidgetItem(led.text()))
                    led = QtGui.QLineEdit(str(junction.demand_pattern))
                    self.tblDemands.setItem(row_count,1,QtGui.QTableWidgetItem(led.text()))
                    self.junction_only = True

    def cmdOK_Clicked(self):
        section = self._main_form.project.find_section('JUNCTIONS')
        junctions_list = section.value[0:]
        # assume we want to edit the first one
        # count how many demands are associated with this junction
        demand_count = 0
        for row in range(self.tblDemands.rowCount()):
            if self.tblDemands.item(row,0):
                x = self.tblDemands.item(row,0).text()
                if len(x) > 0:
                 demand_count += 1
        if demand_count == 1 and self.junction_only:
            # put this demand back into the junction table
            for junction in junctions_list:
                if junction.id == self.node_id:
                    for row in range(self.tblDemands.rowCount()):
                        if self.tblDemands.item(row,0):
                            x = self.tblDemands.item(row,0).text()
                            if len(x) > 0:
                                junction.base_demand_flow = self.tblDemands.item(row,0).text()
                                junction.demand_pattern = self.tblDemands.item(row,1).text()
        else:
            # write these as demands
            section = self._main_form.project.find_section('DEMANDS')
            demands_list = section.value[0:]
            # first clear out any demands associated with this node
            for demand in section.value[0:]:
                if demand.junction_id == self.node_id:
                    section.value.remove(demand)
            # add demands
            for row in range(self.tblDemands.rowCount()):
                if self.tblDemands.item(row,0):
                    x = self.tblDemands.item(row,0).text()
                    if len(x) > 0:
                        new_demand = core.epanet.project.Demand()
                        new_demand.junction_id = self.node_id
                        new_demand.base_demand = self.tblDemands.item(row,0).text()
                        new_demand.demand_pattern = self.tblDemands.item(row,1).text()
                        new_demand.category = ';' + self.tblDemands.item(row,2).text()
                        section.value.append(new_demand)
        self.close()

    def cmdCancel_Clicked(self):
        self.close()
