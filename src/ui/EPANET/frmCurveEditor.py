import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import core.epanet.curves
from ui.EPANET.frmCurveEditorDesigner import Ui_frmCurveEditor
import ui.convenience
from core.epanet.curves import CurveType
from core.epanet.curves import Curve
from PyQt4.QtGui import *
import numpy as np
from ui.model_utility import ParseData


class frmCurveEditor(QtGui.QMainWindow, Ui_frmCurveEditor):
    def __init__(self, main_form, edit_these, new_item):
        QtGui.QMainWindow.__init__(self, main_form)
        self.help_topic = "epanet/src/src/Curve_Ed.htm"
        self.setupUi(self)
        self.cboCurveType.clear()
        ui.convenience.set_combo_items(core.epanet.curves.CurveType, self.cboCurveType)
        QtCore.QObject.connect(self.cmdOK, QtCore.SIGNAL("clicked()"), self.cmdOK_Clicked)
        QtCore.QObject.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"), self.cmdCancel_Clicked)
        # QtCore.QObject.connect(self.cboCurveType, QtCore.SIGNAL("clicked()"), self.cboCurveType_currentIndexChanged)
        self.cboCurveType.currentIndexChanged.connect(self.cboCurveType_currentIndexChanged)
        self.selected_curve_name = ''
        self._main_form = main_form
        self.project = main_form.project
        self.section = self.project.curves

        self.VOLCURVE = 0
        self.HEADCURVE = 1
        self.EFFCURVE = 2
        self.HLOSSCURVE = 3
        self.MAXPOINTS = 51
        self.TINY = 1.e-6
        self.Xlabel = (' Height', ' Flow', ' Flow', ' Flow')
        self.Ylabel = (' Volume', ' Head', ' Efficiency', ' Headloss')
        self.MSG_OUT_OF_ORDER = ' values are not in ascending order.'
        self.MSG_BAD_CURVE = 'Illegal pump curve. Continue editing?'
        self.FMT_EQN = ' Head = %f%-.4g(Flow)^%f'
        self.TXT_PERCENT = ' (%)'
        self.TXT_CUBIC = ' (cubic '
        self.TXT_PUMP = 'PUMP'
        self.TXT_BAD_CURVE = ' Illegal pump curve.'
        self.TXT_OPEN_CURVE_TITLE = 'Open a Curve'
        self.TXT_SAVE_CURVE_TITLE = 'Save Curve As'
        self.TXT_CURVE_FILTER = 'Curve files (*.CRV)|*.CRV|All files|*.*'
        self.TXT_CURVE_HEADER = 'EPANET Curve Data'

        self.X = np.arange(self.MAXPOINTS, dtype=float) * 0.0
        self.Y = np.arange(self.MAXPOINTS, dtype=float) * 0.0
        self.Xunits = ["", "", "", ""] #array[0..3] of String
        self.Yunits = ["", "", "", ""] #array[0..3] of String

        self.new_item = new_item
        if new_item:
            self.set_from(new_item)
        elif edit_these:
            if isinstance(edit_these, list):  # edit first curve if given a list
                self.set_from(edit_these[0])
            else:
                self.set_from(edit_these)

        self.txtEquation.setEnabled(False) #only for display
        self.txtEquation.setText("Display only")

    def set_from(self, curve):
        if not isinstance(curve, Curve):
            curve = self.section.value[curve]
        if isinstance(curve, Curve):
            self.editing_item = curve
        self.txtCurveName.setText(str(curve.name))
        self.txtDescription.setText(str(curve.description))
        ui.convenience.set_combo(self.cboCurveType, curve.curve_type)
        point_count = -1
        for point in curve.curve_xy:
            point_count += 1
            led = QtGui.QLineEdit(str(point[0]))
            self.tblMult.setItem(point_count, 0, QtGui.QTableWidgetItem(led.text()))
            led = QtGui.QLineEdit(str(point[1]))
            self.tblMult.setItem(point_count, 1, QtGui.QTableWidgetItem(led.text()))

        LengthUnits = "???"
        FlowUnits = "???"
        self.Xunits[self.VOLCURVE] = ' (' + LengthUnits + ')'
        self.Xunits[self.HEADCURVE] = ' (' + FlowUnits + ')'
        self.Xunits[self.EFFCURVE] = self.Xunits[self.HEADCURVE]
        self.Xunits[self.HLOSSCURVE] = self.Xunits[self.HEADCURVE]
        self.Yunits[self.VOLCURVE] = self.TXT_CUBIC + LengthUnits + ')'
        self.Yunits[self.HEADCURVE] = ' (' + LengthUnits + ')'
        self.Yunits[self.EFFCURVE] = self.TXT_PERCENT
        self.Yunits[self.HLOSSCURVE] = ' (' + LengthUnits + ')'
        #CurveGrid.RowCount= MAXPOINTS + 1
        #CurveID.MaxLength= MAXID; // Max.chars. in a ID
        #ActiveControl= CurveID

    def GetData(self):
        for row in range(self.tblMult.rowCount()):
            if self.tblMult.item(row,0) and self.tblMult.item(row,1):
                x_val, x_val_good = ParseData.floatTryParse(self.tblMult.item(row, 0).text())
                y_val, y_val_good = ParseData.floatTryParse(self.tblMult.item(row, 1).text())
                if x_val_good and y_val_good:
                    if row + 1 >= self.MAXPOINTS:
                        break
                    else:
                        self.X[row + 1] = x_val
                        self.Y[row + 1] = y_val

    def cmdOK_Clicked(self):
        # TODO: Check for duplicate curve name
        # TODO: Check if X-values are in ascending order
        # TODO: Check for legal pump curve
        self.editing_item.name = self.txtCurveName.text()
        self.editing_item.description = self.txtDescription.text()
        self.editing_item.curve_type = core.epanet.curves.CurveType[self.cboCurveType.currentText()]
        self.editing_item.curve_xy = []
        for row in range(self.tblMult.rowCount()):
            if self.tblMult.item(row,0) and self.tblMult.item(row,1):
                x = self.tblMult.item(row, 0).text()
                y = self.tblMult.item(row, 1).text()
                if len(x) > 0 and len(y) > 0:
                    self.editing_item.curve_xy.append((x, y))
        if self.new_item:  # We are editing a newly created item and it needs to be added to the project
            self._main_form.add_item(self.new_item)
        else:
            pass
            # TODO: self._main_form.edited_?
        self.close()

    def cmdCancel_Clicked(self):
        self.close()

    def cboCurveType_currentIndexChanged(self, newIndex):
        curve_type = core.epanet.curves.CurveType[self.cboCurveType.currentText()]
        if curve_type == CurveType.PUMP:
            self.tblMult.setHorizontalHeaderLabels(("Flow", "Head"))
        elif curve_type == CurveType.EFFICIENCY:
            self.tblMult.setHorizontalHeaderLabels(("Flow", "Efficiency"))
        elif curve_type == CurveType.HEADLOSS:
            self.tblMult.setHorizontalHeaderLabels(("Flow", "Headloss"))
        elif curve_type == CurveType.VOLUME:
            self.tblMult.setHorizontalHeaderLabels(("Height", "Volume"))

    def FitPumpCurve(self, N):
        # From Dcurve.pas, LR
        # Fits 1- or 3-point head curve data to power function
        # input N: Integer
        # return: Boolean
        h0 = 0.0
        h1 = 0.0
        h2 = 0.0
        h4 = 0.0
        h5 = 0.0
        q0 = 0.0
        q1 = 0.0
        q2 = 0.0
        a  = 0.0
        a1 = 0.0
        b  = 0.0
        c  = 0.0
        I = 0
        Iter = 0

        if N == 1:
            q0 = 0.0
            q1 = self.X[1]
            h1 = self.Y[1]
            h0 = 1.33334 * h1
            q2 = 2.0 * q1
            h2 = 0.0
        else:
            q0 = self.X[1]
            h0 = self.Y[1]
            q1 = self.X[2]
            h1 = self.Y[2]
            q2 = self.X[3]
            h2 = self.Y[3]

        a= h0
        b= 0.0
        c= 1.0

        if h0 < self.TINY \
        or (h0 - h1 < self.TINY) \
        or (h1 - h2 < self.TINY) \
        or (q1 - q0 < self.TINY) \
        or (q2 - q1 < self.TINY):
             Result = False
        else:
            a = h0
            Result = False
            for Iter in xrange(1, 6): # 1 to 5 do
                h4 = a - h1
                h5 = a - h2
                #c = ln(h5/h4)/ln(q2/q1)
                c = np.log(h5/h4) / np.log(q2/q1)
                '''
                ************************************************
                NOTE: If c < 1.0 then pump curve is convex which
                might cause convergence problems. This was
                permitted in Version 1.x so it is kept the
                same here. We might want to enforce c >= 1
                in the future.
                *************************************************
                '''
                if (c <= 0.0) or (c > 20.0):
                    break
                #b = -h4/Power(q1,c)
                b = -h4 / (q1 ** c)
                if b > 0.0:
                    break
                #a1 = h0 - b * Power(q0,c)
                a1 = h0 - b * (q0 ** c)
                if abs(a1 - a) < 0.01:
                    Result = True
                    break
                a = a1

        if Result:
            N = 25
            if N > self.tblMult.rowCount:
                N = self.tblMult.rowCount
            #with CurveGrid do
            #  if N > RowCount then N = RowCount
            h4 = -a/b
            h5 = 1.0/c
            #q1 = Power(h4,h5)
            q1 = h4 ** h5
            q1 = q1/N
            self.X[1] = 0.0
            self.Y[1] = a
            for I in xrange(2, N + 1): #2 to N do:
                self.X[I] = (I-1)*q1
                #Y[I] = a + b*Power(X[I],c)
                self.Y[I] = a + b * (self.X[I] ** c)
            #CurveEqn.Caption = Format(FMT_EQN,[a,b,c])
            print "equation is good"
        else:
            #CurveEqn.Caption = self.TXT_BAD_CURVE
            self.setWindowTitle(self.TXT_BAD_CURVE)
        #EqnLabel.Enabled = True
        self.txtEquation.setEnabled(True)

