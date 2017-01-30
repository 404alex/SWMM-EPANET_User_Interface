import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
from ui.help import HelpHandler
from ui.frmGenericPropertyEditorDesigner import Ui_frmGenericPropertyEditor
from ui.SWMM.frmInfiltrationDesigner import Ui_frmInfiltrationEditor
from ui.property_editor_backend import PropertyEditorBackend
from ui.convenience import set_combo_items
from ui.convenience import set_combo
from core.swmm.hydrology.subcatchment import E_InfilModel
from core.swmm.hydrology.subcatchment import HortonInfiltration
from core.swmm.hydrology.subcatchment import GreenAmptInfiltration
from core.swmm.hydrology.subcatchment import CurveNumberInfiltration
from ui.model_utility import ParseData


class frmInfiltration(QtGui.QMainWindow, Ui_frmInfiltrationEditor):
    def __init__(self, parent, edit_these, new_item, title, **kwargs):
        QtGui.QMainWindow.__init__(self, parent)
        self.helper = HelpHandler(self)
        option_section = parent.project.find_section('OPTIONS')
        if option_section.infiltration=="HORTON" or option_section.infiltration=="MODIFIED_HORTON":
            self.help_topic = "swmm/src/src/hortoninfiltrationparameters.htm"
        elif option_section.infiltration=="GREEN_AMPT" or option_section.infiltration=="MODIFIED_GREEN_AMPT":
            self.help_topic = "swmm/src/src/green_amptinfiltrationparame.htm"
        elif option_section.infiltration=="CURVE_NUMBER":
            self.help_topic = "swmm/src/src/curvenumberinfiltrationpara.htm"
        self.setupUi(self)
        self.setWindowTitle(title)
        QtCore.QObject.connect(self.cmdOK, QtCore.SIGNAL("clicked()"), self.cmdOK_Clicked)
        QtCore.QObject.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"), self.cmdCancel_Clicked)
        QtCore.QObject.connect(self.cboInfilModel, QtCore.SIGNAL("currentIndexChanged(int)"),
                               self.cboInfilModel_currentIndexChanged)

        self.qsettings = None
        if kwargs.has_key("qsettings"):
            self.qsettings = kwargs["qsettings"]
        self.default_key = "obj_def_infilmodel"
        if kwargs.has_key("default_key"):
            self.default_key = kwargs["default_key"]
        self.infil_model = None
        self.infil_model_horton = HortonInfiltration()
        self.infil_model_greenampt = GreenAmptInfiltration()
        self.infil_model_cn = CurveNumberInfiltration()
        self.infil_model_horton.set_defaults()
        self.infil_model_greenampt.set_defaults()
        self.infil_model_cn.set_defaults()

        enum_val = E_InfilModel.HORTON
        if self.qsettings is not None:
            self.infil_model = self.qsettings.value(self.default_key, None)
            if self.infil_model is None:
                self.infil_model = HortonInfiltration()
                self.infil_model.set_defaults()
            else:
                enum_val = self.infil_model.model_type()
                if enum_val == E_InfilModel.HORTON or \
                   enum_val == E_InfilModel.MODIFIED_HORTON:
                    self.infil_model_horton.__dict__.update(self.infil_model.__dict__)
                elif enum_val == E_InfilModel.GREEN_AMPT or \
                     enum_val == E_InfilModel.MODIFIED_GREEN_AMPT:
                    self.infil_model_greenampt.__dict__.update(self.infil_model.__dict__)
                elif enum_val == E_InfilModel.CURVE_NUMBER:
                    self.infil_model_cn.__dict__.update(self.infil_model.__dict__)

            self.cboInfilModel.setEnabled(True)
            if self.lblNotes:
                self.tblGeneric.currentCellChanged.connect(self.table_currentCellChanged)
            pass
        else:
            self.backend = PropertyEditorBackend(self.tblGeneric, self.lblNotes, parent, edit_these, new_item)
            #self.lblTop.setText("Infiltration Method:  " + parent.project.find_section('OPTIONS').infiltration)
            proj_infilmodel = parent.project.find_section('OPTIONS').infiltration
            enum_val = E_InfilModel[proj_infilmodel.upper()]
            self.cboInfilModel.setEnabled(False)

        set_combo_items(type(enum_val), self.cboInfilModel)
        set_combo(self.cboInfilModel, enum_val)
        # self.tblGeneric.horizontalHeader().show()
        # self.tblGeneric.setHorizontalHeaderLabels(('1','2','3','4','5','6','7','8'))

        self.corner_label = QtGui.QLabel("Property", self.tblGeneric)
        self.corner_label.setAlignment(QtCore.Qt.AlignCenter)
        self.corner_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        QtCore.QObject.connect(self.tblGeneric.verticalHeader(),
                               QtCore.SIGNAL("geometriesChanged()"), self.resizeCorner)
        QtCore.QObject.connect(self.tblGeneric.horizontalHeader(),
                               QtCore.SIGNAL("geometriesChanged()"), self.resizeCorner)

    def cboInfilModel_currentIndexChanged(self, currentIndex):
        if self.infil_model is None: return
        self.tblGeneric.clearContents()
        enum_val = E_InfilModel[self.cboInfilModel.currentText().upper()]
        if enum_val == E_InfilModel.HORTON or \
           enum_val == E_InfilModel.MODIFIED_HORTON:
            self.meta = self.infil_model_horton.metadata
            self.set_horton()
        elif enum_val == E_InfilModel.GREEN_AMPT or \
             enum_val == E_InfilModel.MODIFIED_GREEN_AMPT:
            self.meta = self.infil_model_greenampt.metadata
            self.set_greenampt()
        elif enum_val == E_InfilModel.CURVE_NUMBER:
            self.meta = self.infil_model_cn.metadata
            self.set_CN()



    def set_horton(self):
        mtype = self.infil_model_horton.model_type()
        props = []
        for i in range(0, len(HortonInfiltration.metadata)):
            if "subcatch" in HortonInfiltration.metadata[i].label.lower():
                continue
            else:
                props.append(HortonInfiltration.metadata[i].label)
        self.tblGeneric.setRowCount(len(props))
        self.tblGeneric.setVerticalHeaderLabels(props)
        for i in range(0, self.tblGeneric.rowCount()):
            vtitle = self.tblGeneric.verticalHeaderItem(i).text().lower()
            if "max" in vtitle and "infil" in vtitle:
                val = self.infil_model_horton.default_max_rate()
                if mtype == E_InfilModel.MODIFIED_HORTON:
                    val = self.infil_model_horton.max_rate
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
            elif "min" in vtitle and "infil" in vtitle:
                val = self.infil_model_horton.default_min_rate()
                if mtype == E_InfilModel.MODIFIED_HORTON:
                    val = self.infil_model_horton.min_rate
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
            elif "decay" in vtitle:
                val = self.infil_model_horton.default_decay()
                if mtype == E_InfilModel.MODIFIED_HORTON:
                    val = self.infil_model_horton.decay
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
            elif "dry" in vtitle:
                val = self.infil_model_horton.default_dry_time()
                if mtype == E_InfilModel.MODIFIED_HORTON:
                    val = self.infil_model_horton.dry_time
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
            elif "max" in vtitle and "volume" in vtitle:
                val = self.infil_model_horton.default_max_volume()
                if mtype == E_InfilModel.MODIFIED_HORTON:
                    val = self.infil_model_horton.max_volume
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))

    def set_greenampt(self):
        mtype = self.infil_model_greenampt.model_type()
        props = []
        for i in range(0, len(GreenAmptInfiltration.metadata)):
            if "subcatch" in GreenAmptInfiltration.metadata[i].label.lower():
                continue
            else:
                props.append(GreenAmptInfiltration.metadata[i].label)
        self.tblGeneric.setRowCount(len(props))
        self.tblGeneric.setVerticalHeaderLabels(props)
        #self.infil_model = GreenAmptInfiltration()
        for i in range(0, self.tblGeneric.rowCount()):
            vtitle = self.tblGeneric.verticalHeaderItem(i).text().lower()
            if "suction" in vtitle:
                val = self.infil_model_greenampt.default_suction()
                if mtype == E_InfilModel.MODIFIED_GREEN_AMPT:
                    val = self.infil_model_greenampt.suction
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
            elif "conduct" in vtitle:
                val = self.infil_model_greenampt.default_conductivity()
                if mtype == E_InfilModel.MODIFIED_GREEN_AMPT:
                    val = self.infil_model_greenampt.hydraulic_conductivity
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
            elif "deficit" in vtitle:
                val = self.infil_model_greenampt.default_init_deficit()
                if mtype == E_InfilModel.MODIFIED_GREEN_AMPT:
                    val = self.infil_model_greenampt.initial_moisture_deficit
                self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))

    def set_CN(self):
        props = []
        for i in range(0, len(CurveNumberInfiltration.metadata)):
            if "subcatch" in CurveNumberInfiltration.metadata[i].label.lower():
                continue
            elif "conduct" in CurveNumberInfiltration.metadata[i].label.lower():
                continue
            else:
                props.append(CurveNumberInfiltration.metadata[i].label)
        self.tblGeneric.setRowCount(len(props))
        self.tblGeneric.setVerticalHeaderLabels(props)
        #self.infil_model = CurveNumberInfiltration()
        for i in range(0, self.tblGeneric.rowCount()):
            vtitle = self.tblGeneric.verticalHeaderItem(i).text().lower()
            if "curve" in vtitle:
                val, val_is_good = ParseData.floatTryParse(self.infil_model_cn.curve_number)
                if val_is_good:
                    self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
                else:
                    self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(self.infil_model_cn.default_CN())))
            elif "dry" in vtitle:
                val, val_is_good = ParseData.floatTryParse(self.infil_model_cn.dry_days)
                if val_is_good:
                    self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(val)))
                else:
                    self.tblGeneric.setItem(i,0, QtGui.QTableWidgetItem(unicode(self.infil_model_cn.default_dry_time())))

    def resizeCorner(self):
        self.corner_label.setGeometry(0, 0, self.tblGeneric.verticalHeader().width(),
                                           self.tblGeneric.horizontalHeader().height())

    def table_currentCellChanged(self):
        row = self.tblGeneric.currentRow()
        if self.lblNotes:
            if hasattr(self, "meta") and self.meta and self.meta[row]:
                self.lblNotes.setText(self.meta[row + 1].hint)
            else:
                self.lblNotes.setText('')

    def cmdOK_Clicked(self):
        if self.backend is not None:
            self.backend.apply_edits()
        else:
            infil_model = None
            if self.qsettings is not None:
                self.qsettings.setValue(self.default_key, infil_model)
        self.close()

    def cmdCancel_Clicked(self):
        self.close()

