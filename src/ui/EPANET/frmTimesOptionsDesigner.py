# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\dev\Python\dev-ui\src\ui\EPANET\frmTimesOptions.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_frmTimesOptions(object):
    def setupUi(self, frmTimesOptions):
        frmTimesOptions.setObjectName(_fromUtf8("frmTimesOptions"))
        frmTimesOptions.resize(304, 368)
        font = QtGui.QFont()
        font.setPointSize(10)
        frmTimesOptions.setFont(font)
        self.centralWidget = QtGui.QWidget(frmTimesOptions)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.lblTotalDuration = QtGui.QLabel(self.centralWidget)
        self.lblTotalDuration.setGeometry(QtCore.QRect(30, 20, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblTotalDuration.setFont(font)
        self.lblTotalDuration.setObjectName(_fromUtf8("lblTotalDuration"))
        self.lblHydraulic = QtGui.QLabel(self.centralWidget)
        self.lblHydraulic.setGeometry(QtCore.QRect(30, 50, 121, 16))
        self.lblHydraulic.setObjectName(_fromUtf8("lblHydraulic"))
        self.lblQuality = QtGui.QLabel(self.centralWidget)
        self.lblQuality.setGeometry(QtCore.QRect(30, 80, 111, 16))
        self.lblQuality.setObjectName(_fromUtf8("lblQuality"))
        self.cmdOK = QtGui.QPushButton(self.centralWidget)
        self.cmdOK.setGeometry(QtCore.QRect(60, 330, 75, 23))
        self.cmdOK.setObjectName(_fromUtf8("cmdOK"))
        self.cmdCancel = QtGui.QPushButton(self.centralWidget)
        self.cmdCancel.setGeometry(QtCore.QRect(160, 330, 75, 23))
        self.cmdCancel.setObjectName(_fromUtf8("cmdCancel"))
        self.txtQuality = QtGui.QLineEdit(self.centralWidget)
        self.txtQuality.setGeometry(QtCore.QRect(160, 80, 113, 20))
        self.txtQuality.setObjectName(_fromUtf8("txtQuality"))
        self.lblRule = QtGui.QLabel(self.centralWidget)
        self.lblRule.setGeometry(QtCore.QRect(30, 110, 111, 16))
        self.lblRule.setObjectName(_fromUtf8("lblRule"))
        self.txtRule = QtGui.QLineEdit(self.centralWidget)
        self.txtRule.setGeometry(QtCore.QRect(160, 110, 113, 20))
        self.txtRule.setObjectName(_fromUtf8("txtRule"))
        self.lblPattern = QtGui.QLabel(self.centralWidget)
        self.lblPattern.setGeometry(QtCore.QRect(30, 140, 111, 16))
        self.lblPattern.setObjectName(_fromUtf8("lblPattern"))
        self.txtPattern = QtGui.QLineEdit(self.centralWidget)
        self.txtPattern.setGeometry(QtCore.QRect(160, 140, 113, 20))
        self.txtPattern.setObjectName(_fromUtf8("txtPattern"))
        self.lblPatternTime = QtGui.QLabel(self.centralWidget)
        self.lblPatternTime.setGeometry(QtCore.QRect(30, 170, 121, 16))
        self.lblPatternTime.setObjectName(_fromUtf8("lblPatternTime"))
        self.lblReporting = QtGui.QLabel(self.centralWidget)
        self.lblReporting.setGeometry(QtCore.QRect(30, 200, 121, 16))
        self.lblReporting.setObjectName(_fromUtf8("lblReporting"))
        self.cboStatistic = QtGui.QComboBox(self.centralWidget)
        self.cboStatistic.setGeometry(QtCore.QRect(160, 290, 111, 22))
        self.cboStatistic.setObjectName(_fromUtf8("cboStatistic"))
        self.txtPatternTime = QtGui.QLineEdit(self.centralWidget)
        self.txtPatternTime.setGeometry(QtCore.QRect(160, 170, 113, 20))
        self.txtPatternTime.setObjectName(_fromUtf8("txtPatternTime"))
        self.lblReportingTime = QtGui.QLabel(self.centralWidget)
        self.lblReportingTime.setGeometry(QtCore.QRect(30, 230, 111, 16))
        self.lblReportingTime.setObjectName(_fromUtf8("lblReportingTime"))
        self.lblClockStart = QtGui.QLabel(self.centralWidget)
        self.lblClockStart.setGeometry(QtCore.QRect(30, 260, 111, 16))
        self.lblClockStart.setObjectName(_fromUtf8("lblClockStart"))
        self.lblStatistic = QtGui.QLabel(self.centralWidget)
        self.lblStatistic.setGeometry(QtCore.QRect(30, 290, 111, 16))
        self.lblStatistic.setObjectName(_fromUtf8("lblStatistic"))
        self.txtReportingTime = QtGui.QLineEdit(self.centralWidget)
        self.txtReportingTime.setGeometry(QtCore.QRect(160, 230, 113, 20))
        self.txtReportingTime.setObjectName(_fromUtf8("txtReportingTime"))
        self.txtClockStart = QtGui.QLineEdit(self.centralWidget)
        self.txtClockStart.setGeometry(QtCore.QRect(160, 260, 113, 20))
        self.txtClockStart.setObjectName(_fromUtf8("txtClockStart"))
        self.txtReporting = QtGui.QLineEdit(self.centralWidget)
        self.txtReporting.setGeometry(QtCore.QRect(160, 200, 113, 20))
        self.txtReporting.setObjectName(_fromUtf8("txtReporting"))
        self.txtTotalDuration = QtGui.QLineEdit(self.centralWidget)
        self.txtTotalDuration.setGeometry(QtCore.QRect(160, 20, 113, 20))
        self.txtTotalDuration.setObjectName(_fromUtf8("txtTotalDuration"))
        self.txtHydraulic = QtGui.QLineEdit(self.centralWidget)
        self.txtHydraulic.setGeometry(QtCore.QRect(160, 50, 113, 20))
        self.txtHydraulic.setObjectName(_fromUtf8("txtHydraulic"))
        frmTimesOptions.setCentralWidget(self.centralWidget)

        self.retranslateUi(frmTimesOptions)
        QtCore.QMetaObject.connectSlotsByName(frmTimesOptions)

    def retranslateUi(self, frmTimesOptions):
        frmTimesOptions.setWindowTitle(_translate("frmTimesOptions", "EPANET Times Options", None))
        self.lblTotalDuration.setText(_translate("frmTimesOptions", "Total Duration", None))
        self.lblHydraulic.setText(_translate("frmTimesOptions", "<html><head/><body><p>Hydraulic Time Step</p></body></html>", None))
        self.lblQuality.setText(_translate("frmTimesOptions", "Quality Time Step", None))
        self.cmdOK.setText(_translate("frmTimesOptions", "OK", None))
        self.cmdCancel.setText(_translate("frmTimesOptions", "Cancel", None))
        self.lblRule.setText(_translate("frmTimesOptions", "Rule Time Step", None))
        self.lblPattern.setText(_translate("frmTimesOptions", "Pattern Time Step", None))
        self.lblPatternTime.setText(_translate("frmTimesOptions", "Pattern Start Time", None))
        self.lblReporting.setText(_translate("frmTimesOptions", "Reporting Time Step", None))
        self.lblReportingTime.setText(_translate("frmTimesOptions", "Report Start Time", None))
        self.lblClockStart.setText(_translate("frmTimesOptions", "Clock Start Time", None))
        self.lblStatistic.setText(_translate("frmTimesOptions", "Statistic", None))

