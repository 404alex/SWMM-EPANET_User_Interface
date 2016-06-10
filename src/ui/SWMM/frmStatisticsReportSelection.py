import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import core.swmm.project
from ui.SWMM.frmStatisticsReportSelectionDesigner import Ui_frmStatisticsReportSelection
from ui.SWMM.frmStatisticsReport import frmStatisticsReport
from ui.help import HelpHandler
import Externals.swmm.outputapi.SMOutputWrapper as SMO


class frmStatisticsReportSelection(QtGui.QMainWindow, Ui_frmStatisticsReportSelection):

    def __init__(self, main_form):
        QtGui.QMainWindow.__init__(self, main_form)
        self.help_topic = "swmm/src/src/statisticsselectiondialog.htm"
        self.setupUi(self)
        QtCore.QObject.connect(self.cmdOK, QtCore.SIGNAL("clicked()"), self.cmdOK_Clicked)
        QtCore.QObject.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"), self.cmdCancel_Clicked)

        self._main_form = main_form
        self.cboCategory.addItems(["Subcatchment", "Node", "Link", "System"])
        self.cboCategory.currentIndexChanged.connect(self.cboCategory_currentIndexChanged)
        self.cboVariable.currentIndexChanged.connect(self.cboVariable_currentIndexChanged)
        self.cboEvent.addItems(["Event-Dependent","Daily","Monthly","Annual"])
        self.cboEvent.currentIndexChanged.connect(self.cboEvent_currentIndexChanged)
        self.txtPrecip.setText('0')
        self.txtVolume.setText('0')
        self.txtSeparation.setText('6')

    def set_from(self, project, output):
        self.project = project
        self.output = output
        self.cboCategory.setCurrentIndex(1)
        self.cboCategory.setCurrentIndex(0)
        self.cboEvent.setCurrentIndex(1)

    def cboCategory_currentIndexChanged(self, newIndex):
        object_type = SMO.SMO_objectTypes[newIndex]
        self.lstName.clear()
        if newIndex <> 3:
            for item in self.output.all_items[newIndex]:
                self.lstName.addItem(item.id)
            self.lstName.setItemSelected(self.lstName.item(0),True)
            self.cboVariable.clear()
            for variable in object_type.AttributeNames:
                self.cboVariable.addItem(variable)
        else:
            self.cboVariable.clear()
            self.cboVariable.addItems(['Temperature','Precipitation','Snow Depth','Infiltration','Runoff','DW Inflow',
                                       'GW Inflow','I&I Inflow','Direct Inflow','Total Inflow','Floowding','Outflow',
                                       'Storage','Evaporation','PET'])

    def cboVariable_currentIndexChanged(self, newIndex):
        self.cboStatistic.clear()
        if self.cboCategory.currentIndex() == 0:
            # subcatchment
            if newIndex < 8:
                self.cboStatistic.addItems(['Mean', 'Peak', 'Total', 'Duration', 'Inter-Event Time'])  # flow stats
            else:
                self.cboStatistic.addItems(['Mean Concen.','Peak Concen.','Mean Load','Peak Load','Total Load'])   #qual stats
        elif self.cboCategory.currentIndex() == 1:
            # node
            if newIndex < 2 or newIndex > 5:
                self.cboStatistic.addItems(['Mean', 'Peak'])   # basic stats
            else:
                self.cboStatistic.addItems(['Mean', 'Peak', 'Total', 'Duration', 'Inter-Event Time'])  # flow stats
        elif self.cboCategory.currentIndex() == 2:
            if newIndex == 0:
                self.cboStatistic.addItems(['Mean', 'Peak', 'Total', 'Duration', 'Inter-Event Time'])  # flow stats
            elif newIndex < 5:
                self.cboStatistic.addItems(['Mean', 'Peak'])   # basic stats
            else:
                self.cboStatistic.addItems(['Mean Concen.','Peak Concen.','Mean Load','Peak Load','Total Load'])   #qual stats
        elif self.cboCategory.currentIndex() == 3:
            if newIndex == 2 or newIndex == 13:
                self.cboStatistic.addItems(['Mean', 'Peak'])   # basic stats
            else:
                self.cboStatistic.addItems(['Mean', 'Peak', 'Total', 'Duration', 'Inter-Event Time'])  # flow stats
        self.lblPrecip.setText(self.cboVariable.currentText())

    def cboEvent_currentIndexChanged(self, newIndex):
        if self.cboEvent.currentIndex() == 0:
            self.lblSeparation.setEnabled(True)
            self.txtSeparation.setEnabled(True)
        else:
            self.lblSeparation.setEnabled(False)
            self.txtSeparation.setEnabled(False)

    def cmdOK_Clicked(self):
        self._frmStatisticsReport = frmStatisticsReport(self._main_form)
        selected_id = ''
        for id_index in self.lstName.selectedIndexes():
            selected_id = str(id_index.data())
        self._frmStatisticsReport.set_from(self.project, self.output, self.cboCategory.currentText(),
                                           selected_id, self.cboVariable.currentText(),
                                           self.cboEvent.currentText(), self.cboStatistic.currentText(),
                                           self.txtPrecip.text(), self.txtVolume.text(), self.txtSeparation.text())
        self._frmStatisticsReport.show()
        self.close()

    def cmdCancel_Clicked(self):
        self.close()
