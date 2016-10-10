import os, sys
os.environ['QT_API'] = 'pyqt'
import sip
for typ in ["QString","QVariant", "QDate", "QDateTime", "QTextStream", "QTime", "QUrl"]:
    sip.setapi(typ, 2)
from cStringIO import StringIO
from embed_ipython_new import EmbedIPython

#from ui.ui_utility import EmbedMap
# from ui.ui_utility import *
from ui.frmGenericPropertyEditor import frmGenericPropertyEditor
from ui.help import HelpHandler
from ui.model_utility import *
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from frmMainDesigner import Ui_frmMain
#from IPython import embed
#from RestrictedPython import compile_restricted
#import py_compile
import imp
import traceback
from core.indexed_list import IndexedList
from core.project_base import ProjectBase

INSTALL_DIR = os.path.abspath(os.path.dirname('__file__'))
INIT_MODULE = "__init__"


class frmMain(QtGui.QMainWindow, Ui_frmMain):

    signalTimeChanged = QtCore.pyqtSignal()

    def __init__(self, q_application):
        QtGui.QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.q_application = q_application
        self.layers = []
        self._forms = []
        """List of editor windows used during this session, kept here so they are not automatically closed."""
        self.model = "Not Set"
        self.project_type = ProjectBase
        self.project = None
        self.obj_tree = None
        self.obj_list = None
        self.obj_view_model = QStandardItemModel()
        self.plugins = self.get_plugins()
        self.populate_plugins_menu()
        QtCore.QObject.connect(self.actionStdNewProjectMenu, QtCore.SIGNAL('triggered()'), self.new_project)
        QtCore.QObject.connect(self.actionStdNewProject, QtCore.SIGNAL('triggered()'), self.new_project)
        QtCore.QObject.connect(self.actionStdOpenProjMenu, QtCore.SIGNAL('triggered()'), self.open_project)
        QtCore.QObject.connect(self.actionStdOpenProj, QtCore.SIGNAL('triggered()'), self.open_project)
        QtCore.QObject.connect(self.actionStdExit, QtCore.SIGNAL('triggered()'), self.action_exit)
        QtCore.QObject.connect(self.actionIPython, QtCore.SIGNAL('triggered()'), self.script_ipython)
        QtCore.QObject.connect(self.actionExec, QtCore.SIGNAL('triggered()'), self.script_exec)
        QtCore.QObject.connect(self.actionStdSave, QtCore.SIGNAL('triggered()'), self.save_project)
        QtCore.QObject.connect(self.actionStdSaveMenu, QtCore.SIGNAL('triggered()'), self.save_project)
        QtCore.QObject.connect(self.actionStdSave_As, QtCore.SIGNAL('triggered()'), self.save_project_as)
        QtCore.QObject.connect(self.actionStdRun_Simulation, QtCore.SIGNAL('triggered()'), self.run_simulation)
        QtCore.QObject.connect(self.actionRun_SimulationMenu, QtCore.SIGNAL('triggered()'), self.run_simulation)
        QtCore.QObject.connect(self.actionStdProjCalibration_Data, QtCore.SIGNAL('triggered()'), self.calibration_data)

        self.setAcceptDrops(True)
        self.tree_section = ''

        # Map attributes will be set below if possible or will remain None to indicate map is not present.
        self.canvas = None
        self.map_widget = None
        try:
            # TODO: make sure this works on all platforms, both in dev environment and in our installed packages
            orig_path = os.environ["Path"]
            search_paths = []
            if os.environ.has_key("QGIS_PREFIX_PATH"):
                search_paths.append(os.environ.get("QGIS_PREFIX_PATH"))
            if os.environ.has_key("QGIS_HOME"):
                search_paths.append(os.environ.get("QGIS_HOME"))
            dirname = INSTALL_DIR
            while dirname:
                search_paths.append(os.path.join(dirname, "qgis"))
                updir = os.path.dirname(dirname)
                if not updir or updir == dirname:
                    break
                dirname = updir
            search_paths.extend([r"C:\OSGeo4W64\apps\qgis",
                                 r"C:\OSGeo4W\apps\qgis",
                                 r"/usr",
                                 r"/Applications/QGIS.app/Contents/MacOS"])
            for qgis_home in search_paths:
                try:
                    if os.path.isdir(qgis_home):
                        # os.environ["Path"] = r"C:/OSGeo4W64/apps/Python27/Scripts;C:/OSGeo4W64/apps/qgis/bin;C:/OSGeo4W64/bin;" + os.environ["Path"]
                        updir = os.path.dirname(qgis_home)
                        updir2 = os.path.dirname(updir)
                        os.environ["Path"] = os.path.join(updir, r"/Python27/Scripts;") +\
                                             os.path.join(qgis_home, "bin;") + \
                                             os.path.join(updir2, "bin;") + orig_path
                        from qgis.core import QgsApplication
                        from qgis.gui import QgsMapCanvas
                        from map_tools import EmbedMap
                        QgsApplication.setPrefixPath(qgis_home, True)
                        QgsApplication.initQgis()
                        self.canvas = QgsMapCanvas(self, 'mapCanvas')
                        self.canvas.setMouseTracking(True)
                        self.map_widget = EmbedMap(session=self, mapCanvas=self.canvas, main_form=self)
                        self.map_win = self.map.addSubWindow(self.map_widget, QtCore.Qt.Widget)
                        if self.map_win:
                            self.map_win.setGeometry(0, 0, 600, 400)
                            self.map_win.setWindowTitle('Study Area Map')
                            self.map_win.show()
                            QtCore.QObject.connect(self.actionAdd_Vector, QtCore.SIGNAL('triggered()'), self.map_addvector)
                            QtCore.QObject.connect(self.actionAdd_Raster, QtCore.SIGNAL('triggered()'), self.map_addraster)
                            QtCore.QObject.connect(self.actionPan, QtCore.SIGNAL('triggered()'), self.setQgsMapTool)
                            QtCore.QObject.connect(self.actionMapSelectObj, QtCore.SIGNAL('triggered()'), self.setQgsMapTool)
                            QtCore.QObject.connect(self.actionZoom_in, QtCore.SIGNAL('triggered()'), self.setQgsMapTool)
                            QtCore.QObject.connect(self.actionZoom_out, QtCore.SIGNAL('triggered()'), self.setQgsMapTool)
                            QtCore.QObject.connect(self.actionZoom_full, QtCore.SIGNAL('triggered()'), self.zoomfull)
                            QtCore.QObject.connect(self.actionAdd_Feature, QtCore.SIGNAL('triggered()'), self.map_addfeature)
                            QtCore.QObject.connect(self.actionObjAddGage, QtCore.SIGNAL('triggered()'), self.map_add_gage)

                            break  # Success, done looking for a qgis_home
                except Exception as e1:
                    msg = "Did not load QGIS from " + qgis_home + ": " + str(e1) + '\n' # + str(traceback.print_exc())
                    print(msg)
                    # QMessageBox.information(None, "Error Initializing Map", msg, QMessageBox.Ok)

        except Exception as eImport:
            self.canvas = None
        if not self.canvas:
            print("QGIS libraries not found, Not creating map\n")
            # QMessageBox.information(None, "QGIS libraries not found", "Not creating map\n" + str(eImport), QMessageBox.Ok)

        self.time_index = 0
        self.horizontalTimeSlider.valueChanged.connect(self.currentTimeChanged)

        self.onLoad()
        self.undo_stack = QUndoStack(self)
        # self.undo_view = QUndoView(self.undo_stack)

        self.action_undo = QtGui.QAction(self)
        self.action_undo.setObjectName("actionUndo")
        self.action_undo.setText(transl8("frmMain", "Undo", None) )
        self.action_undo.setToolTip(transl8("frmMain", "Undo the most recent edit", None) )
        self.menuEdit.addAction(self.action_undo)
        QtCore.QObject.connect(self.action_undo, QtCore.SIGNAL('triggered()'), self.undo)

        self.action_redo = QtGui.QAction(self)
        self.action_redo.setObjectName("actionRedo")
        self.action_redo.setText(transl8("frmMain", "Redo", None) )
        self.action_redo.setToolTip(transl8("frmMain", "Redo the most recent Undo", None) )
        self.menuEdit.addAction(self.action_redo)
        QtCore.QObject.connect(self.action_redo, QtCore.SIGNAL('triggered()'), self.redo)

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()

    class _AddItem(QtGui.QUndoCommand):
        """Private class that adds an item to the model and the map. Accessed via add_item method."""
        def __init__(self, session, item):
            QtGui.QUndoCommand.__init__(self, "Add " + str(item))
            self.session = session
            self.item = item
            section_field_name = session.section_types[type(item)]
            if hasattr(session.project, section_field_name):
                self.section = getattr(session.project, section_field_name)
            else:
                raise Exception("Section not found in project: " + section_field_name)
            if session.map_widget and hasattr(self.session, "model_layers")\
                                  and hasattr(session.model_layers, section_field_name):
                self.layer = getattr(self.session.model_layers, section_field_name)
            else:
                self.layer = None

        def redo(self):
            if self.item.name == '' or self.item.name in self.section.value:
                self.item.name = self.session.new_item_name(type(self.item))
            if len(self.section.value) == 0 and not isinstance(self.section, list):
                self.section.value = IndexedList([], ['name'])
            self.section.value.append(self.item)
            # self.session.list_objects()  # Refresh the list of items on the form
            list_item = self.session.listViewObjects.addItem(self.item.name)
            self.session.listViewObjects.scrollToItem(list_item)
            if self.layer:
                self.layer.addFeature(self.session.map_widget.point_feature_from_item(self.item))
                self.layer.updateExtents()

                # self.session.map_widget.clearSelectableObjects()
                # self.session.model_layers.create_layers_from_project(self.session.project)

        def undo(self):
            self.section.value.remove(self.item)
            self.session.list_objects()  # Refresh the list of items on the form
            # self.session.listViewObjects.takeItem(len(self.section.value))
            if hasattr(self.session, "model_layers"):
                self.session.map_widget.clearSelectableObjects()
                self.session.model_layers.create_layers_from_project(self.session.project)

    def add_item(self, new_item):
        self.undo_stack.push(self._AddItem(self, new_item))

    class _DeleteItem(QtGui.QUndoCommand):
        """Private class that adds an item to the model and the map. Accessed via add_item method."""
        def __init__(self, session, item):
            QtGui.QUndoCommand.__init__(self, "Delete " + str(item))
            self.session = session
            self.item = item
            section_field_name = session.section_types[type(item)]
            if hasattr(session.project, section_field_name):
                self.section = getattr(session.project, section_field_name)
            else:
                raise Exception("Section not found in project: " + section_field_name)

        def redo(self):
            self.section.value.remove(self.item)
            self.list_objects()  # Refresh the list of items on the form
            if hasattr(self, "model_layers"):
                self.session.map_widget.clearSelectableObjects()
                self.model_layers.create_layers_from_project(self.session.project)

        def undo(self):
            self.section.value.append(self.item)
            self.session.list_objects()  # Refresh the list of items on the form
            if hasattr(self.session, "model_layers"):
                self.session.map_widget.clearSelectableObjects()
                self.session.model_layers.create_layers_from_project(self.session.project)

    def delete_item(self, item):
        self.undo_stack.push(self._DeleteItem(self, item))

    def new_item_name(self, item_type):
        section = getattr(self.project, self.section_types[item_type])
        number = 1
        while str(number) in section.value:
            number += 1
        return str(number)

    def currentTimeChanged(self, slider_val):
        self.time_index = slider_val
        self.signalTimeChanged.emit()

    def setQgsMapTool(self):
        self.map_widget.setZoomInMode()
        self.map_widget.setZoomOutMode()
        self.map_widget.setPanMode()
        self.map_widget.setSelectMode()

    def zoomfull(self):
        self.map_widget.zoomfull()

    def map_addfeature(self):
        self.map_widget.setAddFeatureMode()

    def map_add_gage(self):
        self.map_widget.setAddGageMode()

    def onGeometryAdded(self):
        print 'Geometry Added'

    def mouseMoveEvent(self, event):
        pass
        x = event.x()
        y = event.y()
        if self.canvas:
            p = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            self.btnCoord.setText('x,y: {:}, {:}'.format(p.x(), p.y()))

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove:
            if event.buttons() == QtCore.Qt.NoButton:
                pos = event.pos()
                x = pos.x()
                y = pos.y()
                if self.canvas:
                    p = self.map_widget.canvas.getCoordinateTransform().toMapCoordinates(x, y)
                    self.btnCoord.setText('x,y: %s, %s' % (p.x()), p.y())
            else:
                pass

    def map_addvector(self):
        print 'add vector'
        from frmMapAddVector import frmMapAddVector
        dlg = frmMapAddVector(self)
        dlg.show()
        result = dlg.exec_()
        if result == 1:
            specs = dlg.getLayerSpecifications()
            filename = specs['filename']
            if filename.lower().endswith('.shp'):
                self.map_widget.addVectorLayer(filename)

    def map_addraster(self):
        filename = QtGui.QFileDialog.getOpenFileName(None, 'Specify Raster Dataset', '/')
        if len(filename) > 0:
            self.map_widget.addRasterLayer(filename)

    def on_load(self, tree_top_item_list):
        # self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        # cleaner = QtCore.QObjectCleanupHandler()
        # cleaner.add(self.tabProjMap.layout())
        self.obj_tree = ObjectTreeView(self, tree_top_item_list)
        self.obj_tree.itemDoubleClicked.connect(self.edit_options)
        # self.obj_tree.itemClicked.connect(self.list_objects)
        self.obj_tree.itemSelectionChanged.connect(self.list_objects)
        self.listViewObjects.doubleClicked.connect(self.list_item_clicked)

        self.btnObjAdd.clicked.connect(self.add_object)
        self.btnObjDelete.clicked.connect(self.delete_object)
        self.btnObjProperty.clicked.connect(self.edit_object)
        self.btnObjMoveUp.clicked.connect(self.moveup_object)
        self.btnObjMoveDown.clicked.connect(self.movedown_object)
        self.btnObjSort.clicked.connect(self.sort_object)

        # self.tabProjMap.addTab(self.obj_tree, 'Project')
        layout = QtGui.QVBoxLayout(self.tabProject)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.obj_tree)
        self.tabProject.setLayout(layout)
        self.setWindowTitle(self.model)
        '''
        self.obj_list = ObjectListView(model=self.model, ObjRoot='', ObjType='', ObjList=None)
        mlayout = self.dockw_more.layout()
        # mlayout.setContentsMargins(0, 0, 0, 0)
        mlayout.addWidget(self.obj_list)
        # layout1 = QVBoxLayout(self.dockw_more)
        self.dockw_more.setLayout(mlayout)
        # self.actionPan.setEnabled(False)
        '''

    def populate_plugins_menu(self):
        if self.plugins:
            menu = self.menuPlugins
            for p in self.plugins:
                lnew_action = QtGui.QAction(p['name'], menu)
                lnew_action.setCheckable(True)
                menu.addAction(lnew_action)
                QtCore.QObject.connect(lnew_action, QtCore.SIGNAL('triggered()'), self.run_tier1_plugin)

    def get_plugins(self):
        found_plugins = []
        plugin_folder = os.path.join(INSTALL_DIR, "plugins")
        if not os.path.exists(plugin_folder):
            plugin_folder = os.path.normpath(os.path.join(INSTALL_DIR, "../../plugins"))
        if os.path.exists(plugin_folder):
            for folder_name in os.listdir(plugin_folder):
                location = os.path.join(plugin_folder, folder_name)
                if os.path.isdir(location) and INIT_MODULE + ".py" in os.listdir(location):
                    info = imp.find_module(INIT_MODULE, [location])
                    found_plugins.append({"name": folder_name, "info": info})
        return found_plugins

    def load_plugin(self, plugin):
        try:
            return imp.load_module(INIT_MODULE, *plugin["info"])
        except Exception as ex:
            QMessageBox.information(None, "Exception Loading Plugin", plugin['name'] + '\n' + str(ex), QMessageBox.Ok)
            return None

    def run_tier1_plugin(self):
        # pymsgbox.alert('called here.', 'main program')
        for p in self.plugins:
            if p['name'] == self.sender().text():
                lplugin = self.load_plugin(p)
                if lplugin:
                    create_menu = False
                    if hasattr(lplugin, 'plugin_create_menu'):
                        create_menu = lplugin.plugin_create_menu
                    if create_menu and self.sender().isChecked():
                        self.add_plugin_menu(lplugin)
                        return
                    elif create_menu and not self.sender().isChecked():
                        self.remove_plugin_menu(lplugin)
                        return
                    if hasattr(lplugin, "run"):
                        lplugin.run(self)
                    elif hasattr(lplugin, "classFactory"):
                        plugin_object = lplugin.classFactory(self)
                        plugin_object.initGui()
                return

    def add_plugin_menu(self, plugin):
        new_custom_menu = self.menubar.addMenu(plugin.plugin_name)
        new_custom_menu.menuTag = 'plugin_mainmenu_' + plugin.plugin_name
        for m in plugin.__all__:
            new_action = QtGui.QAction(m, self)
            new_action.setStatusTip(m)
            new_action.setData(plugin.plugin_name + '|' + m)
            new_action.setCheckable(False)
            # new_action.triggered.connect(self.run_plugin_custom)
            QtCore.QObject.connect(new_action, QtCore.SIGNAL('triggered()'), self.run_plugin_custom)
            new_custom_menu.addAction(new_action)

    def find_plugin_main_menu(self, plugin):
        for qm in self.menubar.children():
            if hasattr(qm, 'menuTag'):
                if qm.menuTag == 'plugin_mainmenu_' + plugin.plugin_name:
                    return qm
        return None

    def remove_plugin_menu(self, plugin):
        custom_plugin_menu = self.find_plugin_main_menu(plugin)
        if custom_plugin_menu:
            custom_plugin_menu.clear()
            menu_act = custom_plugin_menu.menuAction()
            self.menubar.removeAction(menu_act)
            menu_act.deleteLater()
            custom_plugin_menu.deleteLater()

    def run_plugin_custom(self):
        menu_text = str(self.sender().data())
        (plugin_name, method_name) = menu_text.split('|', 2)
        for plugin in self.plugins:
            if plugin['name'] == plugin_name:
                loaded_plugin = self.load_plugin(plugin)
                if loaded_plugin:
                    loaded_plugin.run(self, int(loaded_plugin.__all__[str(method_name)]))
                    return

    def script_ipython(self):
        widget = EmbedIPython(session=self, plugins=self.plugins, mainmodule=INIT_MODULE)
        ipy_win = self.map.addSubWindow(widget,QtCore.Qt.Widget)
        if ipy_win:
            ipy_win.show()

    def script_exec(self):
        gui_settings = QtCore.QSettings(self.model, "GUI")
        directory = gui_settings.value("ScriptDir", "")
        file_name = QtGui.QFileDialog.getOpenFileName(self, "Select script to run", directory, "All files (*.*)")
        if file_name:
            path_only, file_only = os.path.split(file_name)
            if path_only != directory:
                gui_settings.setValue("ScriptDir", path_only)
                gui_settings.sync()
                del gui_settings

            save_handle = sys.stdout
            try:
                redirected_output = StringIO()
                sys.stdout = redirected_output
                session = self
                with open(file_name, 'r') as script_file:
                    exec(script_file)
                QMessageBox.information(None, "Finished Running Script",
                                        file_name + "\n" + redirected_output.getvalue(), QMessageBox.Ok)
            except Exception as ex:
                QMessageBox.information(None, "Exception Running Script",
                                        file_name + '\n' + str(ex), QMessageBox.Ok)
            sys.stdout = save_handle

    def make_editor_from_tree(self, search_for, tree_list, selected_items=[], new_item=None):
        edit_form = None
        # If new_item is specified, it is a new item to be edited and is only added if user presses OK.

        # First handle special cases
        section = None
        if search_for == "Pollutants":
            if self.project:
                section = self.project.pollutants
        elif search_for == "Map Labels" or search_for == "Labels":
            if self.project:
                section = self.project.labels

        if section:
            if new_item:
                edit_these = [new_item]
            else:  # add selected items to edit_these
                edit_these = []
                if not isinstance(section.value, basestring):
                    if isinstance(section.value, list):
                        for value in section.value:
                            if value.name in selected_items:
                                edit_these.append(value)
            edit_form = frmGenericPropertyEditor(self, edit_these, self.model + ' ' + search_for + " Editor")
        else:
            for tree_item in tree_list:
                if search_for == tree_item[0]:  # If we found a matching tree item, return its editor
                    if len(tree_item) > 0 and tree_item[1] and not (type(tree_item[1]) is list):
                        args = [self]
                        if len(tree_item) > 2:
                            # We recommend this is a list, but if not, try to treat it as a single argument
                            if isinstance(tree_item[2], basestring) or not isinstance(tree_item[2], list):
                                args.append(str(tree_item[2]))
                            else:  # tree_item[2] is a list that is not a string
                                args.extend(tree_item[2])
                        if selected_items:
                            args.append(selected_items)
                        edit_form = tree_item[1](*args)  # Create editor with first argument self, other args from tree_item
                        edit_form.helper = HelpHandler(edit_form)
                        break
                    return None
                if len(tree_item) > 0 and type(tree_item[1]) is list:  # find whether there is a match in this sub-tree
                    edit_form = self.make_editor_from_tree(search_for, tree_item[1], selected_items)
                    if edit_form:
                        break
        if edit_form:
            edit_form.new_item = new_item
        return edit_form

    def edit_options(self, itm, column):
        if not self.project or not self.get_editor:
            return
        edit_name = itm.data(0, 0)
        if edit_name:
            self.show_edit_window(self.get_editor(edit_name))

    def show_edit_window(self, window):
        if window:
            print "Show edit window " + str(window)
            self._forms.append(window)
            # window.destroyed.connect(lambda s, e, a: self._forms.remove(s))
            # window.destroyed = lambda s, e, a: self._forms.remove(s)
            # window.connect(window, QtCore.SIGNAL('triggered()'), self.editor_closing)
            window.show()

            # def editor_closing(self, event):
            #     print "Editor Closing: " + str(event)
            #     # self._forms.remove(event.)

    def list_item_clicked(self):
        # on double click of an item in the 'bottom left' list
        if not self.project or not hasattr(self, "get_editor"):
            return
        if len(self.listViewObjects.selectedItems()) == 0:
            return
        selected = [str(item.data()) for item in self.listViewObjects.selectedIndexes()]
        self.show_edit_window(self.make_editor_from_tree(self.tree_section, self.tree_top_items, selected))

    def edit_object(self):
        self.list_item_clicked()

    def add_object(self):
        if not self.project or not self.get_editor:
            return
        self.add_object_clicked(self.tree_section)

    def delete_object(self):
        if not self.project or not self.get_editor:
            return
        for item in self.listViewObjects.selectedIndexes():
            selected_text = str(item.data())
            self.delete_object_clicked(self.tree_section, selected_text)

    def moveup_object(self):
        currentRow = self.listViewObjects.currentRow()
        currentItem = self.listViewObjects.takeItem(currentRow)
        self.listViewObjects.insertItem(currentRow - 1, currentItem)

    def movedown_object(self):
        currentRow = self.listViewObjects.currentRow()
        currentItem = self.listViewObjects.takeItem(currentRow)
        self.listViewObjects.insertItem(currentRow + 1, currentItem)

    def sort_object(self):
        self.listViewObjects.sortItems()

    def select_id(self, layer, object_id):
        if object_id is None:
            self.listViewObjects.clearSelection()
        else:
            if layer:
                try:
                    layer_name = layer.name()
                    already_selected_item = self.obj_tree.currentItem()
                    if already_selected_item is None or already_selected_item.text(0) != layer_name:
                        tree_node = self.obj_tree.find_tree_item(layer_name)
                        if tree_node:
                            self.obj_tree.setCurrentItem(tree_node)
                except Exception as ex:
                    print("Did not find layer in tree:\n" + str(ex))
            for i in range(self.listViewObjects.count()):
                item = self.listViewObjects.item(i)
                if item.text() == object_id:
                    self.listViewObjects.setItemSelected(item, True)
                    self.listViewObjects.scrollToItem(item)

    def new_project(self):
        self.project = self.project_type()
        self.setWindowTitle(self.model + " - New")
        self.project.file_name = "New.inp"

    def open_project(self):
        gui_settings = QtCore.QSettings(self.model, "GUI")
        directory = gui_settings.value("ProjectDir", "")
        file_name = QtGui.QFileDialog.getOpenFileName(self, "Open Project...", directory,
                                                      "Inp files (*.inp);;All files (*.*)")
        if file_name:
            self.open_project_quiet(file_name, gui_settings, directory)

    def open_project_quiet(self, file_name, gui_settings, directory):
        self.project = self.project_type()
        try:
            project_reader = self.project_reader_type()
            project_reader.read_file(self.project, file_name)
            path_only, file_only = os.path.split(file_name)
            self.setWindowTitle(self.model + " - " + file_only)
            if path_only != directory:
                gui_settings.setValue("ProjectDir", path_only)
                gui_settings.sync()
                del gui_settings
        except Exception as ex:
            print("open_project_quiet error opening " + file_name + ":\n" + str(ex) + '\n' + str(traceback.print_exc()))
            self.project = ProjectBase()
            self.setWindowTitle(self.model)

    def save_project(self, file_name=None):
        if not file_name:
            file_name = self.project.file_name
        project_writer = self.project_writer_type()
        project_writer.write_file(self.project, file_name)
        if self.map_widget:
            self.map_widget.saveVectorLayers(os.path.dirname(file_name))

    def find_external(self, lib_name):
        filename = os.path.join(self.assembly_path, lib_name)
        if not os.path.exists(filename):
            pp = os.path.dirname(os.path.dirname(self.assembly_path))
            filename = os.path.join(pp, "Externals", lib_name)
        if not os.path.exists(filename):
            pp = os.path.dirname(os.path.dirname(self.assembly_path))
            filename = os.path.join(pp, "Externals", self.model.lower(), "model", lib_name)
        if not os.path.exists(filename):
            filename = QtGui.QFileDialog.getOpenFileName(self,
                                                         'Locate ' + self.model + ' Library',
                                                         '/', '(*{0})'.format(os.path.splitext(lib_name)[1]))
        return filename

    def save_project_as(self):
        gui_settings = QtCore.QSettings(self.model, "GUI")
        directory = gui_settings.value("ProjectDir", "")
        file_name = QtGui.QFileDialog.getSaveFileName(self, "Save As...", directory, "Inp files (*.inp)")
        if file_name:
            path_only, file_only = os.path.split(file_name)
            try:
                self.save_project(file_name)
                self.setWindowTitle(self.model + " - " + file_only)
                if path_only != directory:
                    gui_settings.setValue("ProjectDir", path_only)
                    gui_settings.sync()
                    del gui_settings
            except Exception as ex:
                print(str(ex) + '\n' + str(traceback.print_exc()))
                QMessageBox.information(self, self.model,
                                        "Error saving {0}\nin {1}\n{2}\n{2}".format(
                                            file_only, path_only,
                                            str(ex), str(traceback.print_exc())),
                                        QMessageBox.Ok)

    def dragEnterEvent(self, drag_enter_event):
        if drag_enter_event.mimeData().hasUrls():
            drag_enter_event.accept()
        else:
            drag_enter_event.ignore()

    def dropEvent(self, drop_event):
        #TODO: check project status and prompt if there are unsaved changes that would be overwritten
        for url in drop_event.mimeData().urls():
            directory, filename = os.path.split(str(url.encodedPath()))
            directory = str.lstrip(str(directory), 'file:')
            print(directory)
            if os.path.isdir(directory):
                print(' is directory')
            elif os.path.isdir(directory[1:]):
                directory = directory[1:]
            filename = str.rstrip(str(filename), '\r\n')
            print(filename)
            full_path = os.path.join(directory, filename)
            lfilename = filename.lower()
            if lfilename.endswith('.inp'):
                gui_settings = QtCore.QSettings(self.model, "GUI")
                self.open_project_quiet(full_path, gui_settings, directory)
            #TODO - check to see if QGIS can handle file type
            elif lfilename.endswith('.shp') or lfilename.endswith(".json"):
                self.map_widget.addVectorLayer(full_path)
            else:
                try:
                    self.map_widget.addRasterLayer(full_path)
                except:
                    QMessageBox.information(self, self.model,
                            "Dropped file '" + full_path + "' is not a know type of file",
                            QMessageBox.Ok)

    def action_exit(self):
        # TODO: check project status and prompt if there are unsaved changed
        if self.q_application:
            try:
                self.q_application.quit()
            except:
                try:
                    self.close()
                except:
                    pass

    def __unicode__(self):
        return unicode(self)

    def clear_object_listing(self):
        self.tree_section = ''
        self.listViewObjects.clear()

    def list_objects(self):
        selected_text = ''
        for item in self.obj_tree.selectedIndexes():
            selected_text = str(item.data())
        self.clear_object_listing()
        self.dockw_more.setWindowTitle('')
        if self.project is None or not selected_text:
            return
        ids = self.get_object_list(selected_text)
        self.tree_section = selected_text
        if ids is None:
            self.dockw_more.setEnabled(False)
        else:
            self.dockw_more.setEnabled(True)
            self.dockw_more.setWindowTitle(selected_text)
            self.listViewObjects.addItems(ids)

    def onLoad(self):
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setContentsMargins(1, 2, 1, 3)
        self.listViewObjects.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)


class ModelLayers:
    """
    This is a base class for creating and managing the map layers that are directly linked to model elements.
    Model-specific inheritors contain the model-specific set of layers.
    """
    def __init__(self, map_widget):
        self.map_widget = map_widget
        self.nodes_layers = []
        self.all_layers = []

    def create_layers_from_project(self, project):
        self.project = project
        # First remove old ModelLayers already on the map
        from qgis.core import QgsMapLayerRegistry
        layer_names = []
        for layer in self.all_layers:
            layer_names.append(layer.name())
        QgsMapLayerRegistry.instance().removeMapLayers(layer_names)
        from ui.map_tools import EmbedMap
        EmbedMap.layers = self.map_widget.canvas.layers()


def print_process_id():
    print 'Process ID is:', os.getpid()

if __name__ == '__main__':
    application = QtGui.QApplication(sys.argv)
    QMessageBox.information(None, "frmMain",
                            "Run ui/EPANET/frmMainEPANET or ui/SWMM/frmMainSWMM instead of frmMain.",
                            QMessageBox.Ok)
