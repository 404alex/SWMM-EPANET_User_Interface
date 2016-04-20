import os, sys
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
import traceback
from ui.ui_utility import *

from PyQt4 import QtCore, QtGui
from ui.frmMain import frmMain
from ui.EPANET.frmEnergyOptions import frmEnergyOptions
from ui.EPANET.frmHydraulicsOptions import frmHydraulicsOptions
from ui.EPANET.frmMapBackdropOptions import frmMapBackdropOptions
from ui.EPANET.frmQualityOptions import frmQualityOptions
from ui.EPANET.frmReactionsOptions import frmReactionsOptions
from ui.EPANET.frmReportOptions import frmReportOptions
from ui.EPANET.frmTimesOptions import frmTimesOptions
from ui.EPANET.frmTitle import frmTitle

from ui.EPANET.frmControls import frmControls
from ui.EPANET.frmCurveEditor import frmCurveEditor
from ui.EPANET.frmPatternEditor import frmPatternEditor
from ui.EPANET.frmSourcesQuality import frmSourcesQuality
from ui.EPANET.frmDemands import frmDemands

from ui.model_utility import *
from core.epanet.project import Project
import Externals.epanet2 as pyepanet
from frmRunEPANET import frmRunEPANET

class frmMainEPANET(frmMain):
    def __init__(self, parent=None, *args):
        frmMain.__init__(self, parent)

        QtCore.QObject.connect(self.actionStdNewProjectMenu, QtCore.SIGNAL('triggered()'), self.std_newproj)
        QtCore.QObject.connect(self.actionStdNewProject, QtCore.SIGNAL('triggered()'), self.std_newproj)

        QtCore.QObject.connect(self.actionStdOpenProjMenu, QtCore.SIGNAL('triggered()'), self.std_openproj)
        QtCore.QObject.connect(self.actionStdOpenProj, QtCore.SIGNAL('triggered()'), self.std_openproj)

        QtCore.QObject.connect(self.actionStdExit, QtCore.SIGNAL('triggered()'), self.action_exit)

        self.model = 'EPANET'
        self.model_path = ''  # Set this only if needed later when running model
        self.modelenv1 = 'EXE_EPANET'
        self.assembly_path = os.path.dirname(os.path.abspath(__file__))

        self.on_load(model=self.model)

        self._frmEnergyOptions = None
        self._frmHydraulicsOptions = None
        self._frmMapBackdropOptions = None
        self._frmQualityOptions = None
        self._frmReactionsOptions = None
        self._frmReportOptions = None
        self._frmTimesOptions = None
        self._frmTitle = None

        self._frmControls = None
        self._frmCurveEditor = None
        self._frmPatternEditor = None

        self._forms = []

    def std_newproj(self):
        self.project = Project()
        self.setWindowTitle(self.model + " - New")
        self.project.file_name = "New.inp"
        pass

    def std_openproj(self):
        qsettings = QtCore.QSettings(self.model, "GUI")
        directory = qsettings.value("ProjectDir", "")
        file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Project...", directory,
                                                      "Inp files (*.inp);;All files (*.*)")
        if file_name:
            self.project = Project()
            try:
                self.project.read_file(file_name)
                path_only, file_only = os.path.split(file_name)
                self.setWindowTitle(self.model + " - " + file_only)
                if path_only != directory:
                    qsettings.setValue("ProjectDir", path_only)
                    del qsettings
            except:
                self.project = None
                self.setWindowTitle(self.model)
        pass

    def edit_options(self, itm, column):
        if self.project is None:
            return

        if itm.data(0, 0) == 'Energy':
            self._frmEnergyOptions = frmEnergyOptions(self)
            self._frmEnergyOptions.show()
        if itm.data(0, 0) == 'Hydraulics':
            self._frmHydraulicsOptions = frmHydraulicsOptions(self)
            self._frmHydraulicsOptions.show()
        if itm.data(0, 0) == 'Map/Backdrop':
            self._frmMapBackdropOptions = frmMapBackdropOptions(self)
            self._frmMapBackdropOptions.show()
        if itm.data(0, 0) == 'Quality':
            self._frmQualityOptions = frmQualityOptions(self)
            self._frmQualityOptions.show()
        if itm.data(0, 0) == 'Reactions':
            self._frmReactionsOptions = frmReactionsOptions(self)
            self._frmReactionsOptions.show()
        if itm.data(0, 0) == 'Report':
            self._frmReportOptions = frmReportOptions(self)
            self._frmReportOptions.show()
        if itm.data(0, 0) == 'Times':
            self._frmTimesOptions = frmTimesOptions(self)
            self._frmTimesOptions.show()
        if itm.data(0, 0) == 'Title/Notes':
            self._frmTitle = frmTitle(self)
            self._frmTitle.show()
        if itm.data(0, 0) == 'Simple':
            self._frmControls = frmControls(self)
            self._frmControls.setWindowTitle('EPANET Simple Controls')
            self._frmControls.set_from(self.project, "CONTROLS")
            self._frmControls.show()
        if itm.data(0, 0) == 'Rule-Based':
            self._frmControls = frmControls(self)
            self._frmControls.setWindowTitle('EPANET Rule-Based Controls')
            self._frmControls.set_from(self.project, "RULES")
            self._frmControls.show()

        # the following items will respond to a click in the list, not the tree diagram
        if itm.data(0, 0) == 'Patterns':
            self._frmPatternEditor = frmPatternEditor(self)
            self._frmPatternEditor.show()
        if itm.data(0, 0) == 'Curves':
            self._frmCurveEditor = frmCurveEditor(self)
            self._frmCurveEditor.show()

        # the following items will respond to a click on a node form, not the tree diagram
        if itm.data(0, 0) == 'Junctions' or itm.data(0, 0) == 'Reservoirs' or itm.data(0, 0) == 'Tanks':
            # assume we're editing the first node for now
            self._frmSourcesQuality = frmSourcesQuality(self)
            self._frmSourcesQuality.setWindowTitle('EPANET Source Editor for Node ' + '1')
            self._frmSourcesQuality.set_from(self.project, '1')
            self._frmSourcesQuality.show()
        if itm.data(0, 0) == 'Junctions':
            # assume we're editing the first junction for now
            self._frmDemands = frmDemands(self)
            self._frmDemands.setWindowTitle('EPANET Demands for Junction ' + '1')
            self._frmDemands.set_from(self.project, '1')
            self._frmDemands.show()

        # mitm = itm
        # if self.project == None or mitm.data(0, 0) != 'Options':
        #     return
        # from ui.frmOptions import frmOptions
        # dlg = frmOptions(self, self.project.options)
        # dlg.show()
        # result = dlg.exec_()
        # if result == 1:
        #    pass

    def run_simulation(self):
        # Find input file to run
        file_name = ''
        use_existing = self.project and self.project.file_name and os.path.exists(self.project.file_name)
        if use_existing:
            file_name = self.project.file_name
            # TODO: save if needed, decide whether to save to temp location as previous version did.
        else:
            qsettings = QtCore.QSettings(self.model, "GUI")
            directory = qsettings.value("ProjectDir", "")
            file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Project...", directory,
                                                          "Inp files (*.inp);;All files (*.*)")

        if os.path.exists(file_name):
            prefix, extension = os.path.splitext(file_name)
            if not os.path.exists(self.model_path):
                if 'darwin' in sys.platform:
                    lib_name = 'libepanet.dylib.dylib'
                    ext = '.dylib'
                elif 'win' in sys.platform:
                    lib_name = 'epanet2_amd64.dll'
                    ext = '.dll'
                else:  # Linux
                    lib_name = 'libepanet2_amd64.so'
                    ext = '.so'

                self.model_path = os.path.join(self.assembly_path, lib_name)
                if not os.path.exists(self.model_path):
                    pp = os.path.dirname(os.path.dirname(self.assembly_path))
                    self.model_path = os.path.join(pp, "Externals", lib_name)
                if not os.path.exists(self.model_path):
                    self.model_path = QtGui.QFileDialog.getOpenFileName(self,
                                                                        'Locate ' + self.model + ' Library',
                                                                        '/', '(*{1})'.format(ext))
            if os.path.exists(self.model_path):
                try:
                    model_api = pyepanet.ENepanet(file_name, prefix + '.rpt', prefix + '.bin', self.model_path)
                    frmRun = frmRunEPANET(model_api, self.project, self)
                    self._forms.append(frmRun)
                    if not use_existing:
                        # Read this project so we can refer to it while running
                        frmRun.progressBar.setVisible(False)
                        frmRun.lblTime.setVisible(False)
                        frmRun.fraTime.setVisible(False)
                        frmRun.fraBottom.setVisible(False)
                        frmRun.showNormal()
                        frmRun.set_status_text("Reading " + file_name)

                        self.project = Project()
                        self.project.read_file(file_name)
                        frmRun.project = self.project

                    frmRun.Execute()
                    return
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
            # program = os.environ[self.modelenv1]
            #
            # exe_name = "epanet2d.exe"
            # exe_path = os.path.join(self.assembly_path, exe_name)
            # if not os.path.exists(exe_path):
            #     pp = os.path.dirname(os.path.dirname(self.assembly_path))
            #     exe_path = os.path.join(pp, "Externals", exe_name)
            # if not os.path.exists(exe_path):
            #     exe_path = QtGui.QFileDialog.getOpenFileName(self, 'Locate EPANET Executable', '/',
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
            # status = StatusMonitor0(program, args, self, model='EPANET')
            # status.show()
        else:
            QMessageBox.information(None, self.model, self.model + " input file not found", QMessageBox.Ok)

    def on_load(self, **kwargs):
        # self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        # cleaner = QtCore.QObjectCleanupHandler()
        # cleaner.add(self.tabProjMap.layout())
        self.obj_tree = ObjectTreeView(model=kwargs['model'])
        self.obj_tree.itemDoubleClicked.connect(self.edit_options)
        # self.tabProjMap.addTab(self.obj_tree, 'Project')
        layout = QVBoxLayout(self.tabProject)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.obj_tree)
        self.tabProject.setLayout(layout)
        self.setWindowTitle(self.model)

        self.obj_list = ObjectListView(model=kwargs['model'],ObjRoot='',ObjType='',ObjList=None)
        mlayout = self.dockw_more.layout()
        #mlayout.setContentsMargins(0, 0, 0, 0)
        mlayout.addWidget(self.obj_list)
        #layout1 = QVBoxLayout(self.dockw_more)
        self.dockw_more.setLayout(mlayout)
        #self.actionPan.setEnabled(False)

    def action_exit(self):
        # TODO: check project status and prompt if there are unsaved changed
        app.quit()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MainApp = frmMainEPANET()
    MainApp.show()
    sys.exit(app.exec_())
