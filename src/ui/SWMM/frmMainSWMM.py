import os, sys
os.environ['QT_API'] = 'pyqt'
import sip
for typ in ["QString","QVariant", "QDate", "QDateTime", "QTextStream", "QTime", "QUrl"]:
    sip.setapi(typ, 2)
import webbrowser
import traceback
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox, QFileDialog, QColor

from ui.model_utility import QString, from_utf8, transl8, process_events, StatusMonitor0
from ui.help import HelpHandler
from ui.frmMain import frmMain, ModelLayers
from ui.SWMM.frmDates import frmDates
from ui.SWMM.frmDynamicWave import frmDynamicWave
from ui.SWMM.frmMapBackdropOptions import frmMapBackdropOptions
from ui.SWMM.frmGeneralOptions import frmGeneralOptions
from ui.SWMM.frmInterfaceFiles import frmInterfaceFiles
from ui.SWMM.frmReportOptions import frmReportOptions
from ui.SWMM.frmTimeSteps import frmTimeSteps
from ui.SWMM.frmTitle import frmTitle

from ui.SWMM.frmAbout import frmAbout
from ui.SWMM.frmAquifers import frmAquifers
from ui.SWMM.frmClimatology import frmClimatology
from ui.SWMM.frmConduits import frmConduits
from ui.SWMM.frmControls import frmControls
from ui.SWMM.frmCurveEditor import frmCurveEditor
from ui.SWMM.frmOrifices import frmOrifices
from ui.SWMM.frmOutlets import frmOutlets
from ui.SWMM.frmPatternEditor import frmPatternEditor
from ui.SWMM.frmPumps import frmPumps
from ui.SWMM.frmTimeseries import frmTimeseries
from ui.SWMM.frmJunction import frmJunction
from ui.SWMM.frmOutfalls import frmOutfalls
from ui.SWMM.frmDividers import frmDividers
from ui.SWMM.frmStorageUnits import frmStorageUnits
from ui.SWMM.frmRainGages import frmRainGages
from ui.SWMM.frmSubcatchments import frmSubcatchments
from ui.SWMM.frmLID import frmLID
from ui.SWMM.frmSnowPack import frmSnowPack
from ui.SWMM.frmUnitHydrograph import frmUnitHydrograph
from ui.SWMM.frmTransect import frmTransect
from ui.SWMM.frmWeirs import frmWeirs
from ui.SWMM.frmCrossSection import frmCrossSection
from ui.SWMM.frmInflows import frmInflows
from ui.SWMM.frmLandUses import frmLandUses
from ui.frmGenericPropertyEditor import frmGenericPropertyEditor
from ui.SWMM.frmCalibrationData import frmCalibrationData
from ui.SWMM.frmSummaryReport import frmSummaryReport
from ui.SWMM.frmTimeSeriesPlot import frmTimeSeriesPlot
from ui.SWMM.frmProfilePlot import frmProfilePlot
from ui.SWMM.frmScatterPlot import frmScatterPlot
from ui.SWMM.frmTableSelection import frmTableSelection
from ui.SWMM.frmStatisticsReportSelection import frmStatisticsReportSelection

from core.swmm.swmm_project import SwmmProject as Project
from core.swmm.inp_reader_project import ProjectReader
from core.swmm.inp_writer_project import ProjectWriter
from core.swmm.hydrology.aquifer import Aquifer
from core.swmm.hydrology.subcatchment import Subcatchment
from core.swmm.hydrology.raingage import RainGage
from core.swmm.quality import Pollutant
from core.swmm.hydraulics.node import Junction
from core.swmm.hydraulics.node import Outfall
from core.swmm.hydraulics.node import Divider
from core.swmm.hydraulics.node import StorageUnit
from core.swmm.hydrology.snowpack import SnowPack
from core.swmm.hydrology.lidcontrol import LIDControl
from core.swmm.hydrology.unithydrograph import UnitHydrograph
from core.swmm.hydraulics.link import Conduit
from core.swmm.hydraulics.link import Pump
from core.swmm.hydraulics.link import Orifice
from core.swmm.hydraulics.link import Outlet
from core.swmm.hydraulics.link import Weir
from core.swmm.hydraulics.link import Transect
from core.swmm.hydraulics.link import CrossSection
from core.swmm.quality import Landuse
from core.swmm.curves import Curve
from core.swmm.curves import CurveType
from core.swmm.timeseries import TimeSeries
from core.swmm.patterns import Pattern
from core.swmm.labels import Label

from Externals.swmm.outputapi import SMOutputWrapper
from frmRunSWMM import frmRunSWMM

import Externals.swmm.outputapi.SMOutputWrapper as SMO
import ui.convenience


class frmMainSWMM(frmMain):
    """Main form for SWMM user interface, based on frmMain which is shared with EPANET."""

    # Variables used to populate the tree control
    # Each item is a list: label plus either editing form for this section or a child list of tree variables.
    # If an editing form takes additional arguments, they follow the editing form as a list.
    # Special cases may just have a label and no editing form or children.
    # *_items are a lists of items in a section
    tree_options_General        = ["General",         frmGeneralOptions]
    tree_options_Dates          = ["Dates",           frmDates]
    tree_options_TimeSteps      = ["Time Steps",      frmTimeSteps]
    tree_options_DynamicWave    = ["Dynamic Wave",    frmDynamicWave]
    tree_options_InterfaceFiles = ["Interface Files", frmInterfaceFiles]
    tree_options_Reporting      = ["Reporting",       frmReportOptions]
    tree_options_MapBackdrop    = ["Map/Backdrop",    frmMapBackdropOptions]
    tree_options_items = [
        tree_options_General,
        tree_options_Dates,
        tree_options_TimeSteps,
        tree_options_DynamicWave,
        tree_options_InterfaceFiles,
        tree_options_Reporting,
        tree_options_MapBackdrop]

    tree_climatology_Temperature    = ["Temperature",     frmClimatology, ["Temperature"]]
    tree_climatology_Evaporation    = ["Evaporation",     frmClimatology, ["Evaporation"]]
    tree_climatology_WindSpeed      = ["Wind Speed",      frmClimatology, ["Wind Speed"]]
    tree_climatology_SnowMelt       = ["Snow Melt",       frmClimatology, ["Snow Melt"]]
    tree_climatology_ArealDepletion = ["Areal Depletion", frmClimatology, ["Areal Depletion"]]
    tree_climatology_Adjustment     = ["Adjustment",      frmClimatology, ["Adjustment"]]
    tree_climatology_items = [
        tree_climatology_Temperature,
        tree_climatology_Evaporation,
        tree_climatology_WindSpeed,
        tree_climatology_SnowMelt,
        tree_climatology_ArealDepletion,
        tree_climatology_Adjustment]

    tree_hydrology_RainGages       = ["Rain Gages",       frmRainGages]
    tree_hydrology_Subcatchments   = ["Subcatchments",    frmSubcatchments]
    tree_hydrology_Aquifers        = ["Aquifers",         frmAquifers]
    tree_hydrology_SnowPacks       = ["Snow Packs",       frmSnowPack]
    tree_hydrology_UnitHydrographs = ["Unit Hydrographs", frmUnitHydrograph]
    tree_hydrology_LIDControls     = ["LID Controls",     frmLID]
    tree_hydrology_items = [
        tree_hydrology_RainGages,
        tree_hydrology_Subcatchments,
        tree_hydrology_Aquifers,
        tree_hydrology_SnowPacks,
        tree_hydrology_UnitHydrographs,
        tree_hydrology_LIDControls]

    tree_nodes_Junctions    = ["Junctions",     frmJunction]
    tree_nodes_Outfalls     = ["Outfalls",      frmOutfalls]
    tree_nodes_Dividers     = ["Dividers",      frmDividers]
    tree_nodes_StorageUnits = ["Storage Units", frmStorageUnits]
    tree_nodes_items = [
        tree_nodes_Junctions,
        tree_nodes_Outfalls,
        tree_nodes_Dividers,
        tree_nodes_StorageUnits]

    tree_links_Conduits = ["Conduits", frmConduits]
    tree_links_Pumps    = ["Pumps",    frmPumps]
    tree_links_Orifices = ["Orifices", frmOrifices]
    tree_links_Weirs    = ["Weirs",    frmWeirs]
    tree_links_Outlets  = ["Outlets",  frmOutlets]
    tree_links_items = [
        tree_links_Conduits,
        tree_links_Pumps,
        tree_links_Orifices,
        tree_links_Weirs,
        tree_links_Outlets]

    tree_hydraulics_Nodes     = ["Nodes",     tree_nodes_items]
    tree_hydraulics_Links     = ["Links",     tree_links_items]
    tree_hydraulics_Transects = ["Transects", frmTransect]
    tree_hydraulics_Controls  = ["Controls",  frmControls]
    tree_hydraulics_items = [
        tree_hydraulics_Nodes,
        tree_hydraulics_Links,
        tree_hydraulics_Transects,
        tree_hydraulics_Controls]

    tree_quality_Pollutants = ["Pollutants", None]
    tree_quality_LandUses   = ["Land Uses",  frmLandUses]
    tree_quality_items = [
        tree_quality_Pollutants,
        tree_quality_LandUses]

    tree_curves_ControlCurves   = ["Control Curves",   frmCurveEditor, ["SWMM Control Curves",   "CONTROL"]]
    tree_curves_DiversionCurves = ["Diversion Curves", frmCurveEditor, ["SWMM Diversion Curves", "DIVERSION"]]
    tree_curves_PumpCurves      = ["Pump Curves",      frmCurveEditor, ["SWMM Pump Curves",      "PUMP"]]
    tree_curves_RatingCurves    = ["Rating Curves",    frmCurveEditor, ["SWMM Rating Curves",    "RATING"]]
    tree_curves_ShapeCurves     = ["Shape Curves",     frmCurveEditor, ["SWMM Shape Curves",     "SHAPE"]]
    tree_curves_StorageCurves   = ["Storage Curves",   frmCurveEditor, ["SWMM Storage Curves",   "STORAGE"]]
    tree_curves_TidalCurves     = ["Tidal Curves",     frmCurveEditor, ["SWMM Tidal Curves",     "TIDAL"]]
    tree_curves_items = [
        tree_curves_ControlCurves,
        tree_curves_DiversionCurves,
        tree_curves_PumpCurves,
        tree_curves_RatingCurves,
        tree_curves_ShapeCurves,
        tree_curves_StorageCurves,
        tree_curves_TidalCurves]

    tree_TitleNotes   = ["Title/Notes",   frmTitle]
    tree_Options      = ["Options",       tree_options_items]
    tree_Climatology  = ["Climatology",   tree_climatology_items]
    tree_Hydrology    = ["Hydrology",     tree_hydrology_items]
    tree_Hydraulics   = ["Hydraulics",    tree_hydraulics_items]
    tree_Quality      = ["Quality",       tree_quality_items]
    tree_Curves       = ["Curves",        tree_curves_items]
    tree_TimeSeries   = ["Time Series",   frmTimeseries]
    tree_TimePatterns = ["Time Patterns", frmPatternEditor]
    tree_MapLabels    = ["Map Labels",    None]
    tree_top_items = [
        tree_TitleNotes,
        tree_Options,
        tree_Climatology,
        tree_Hydrology,
        tree_Hydraulics,
        tree_Quality,
        tree_Curves,
        tree_TimeSeries,
        tree_TimePatterns,
        tree_MapLabels]

    tree_items_using_name = (tree_hydrology_Aquifers,
                           tree_hydrology_LIDControls,
                           tree_hydrology_UnitHydrographs,
                           tree_hydrology_SnowPacks,
                           tree_hydraulics_Transects,
                           tree_quality_LandUses,
                           tree_TimeSeries,
                           tree_TimePatterns,
                           tree_curves_ControlCurves,
                           tree_curves_DiversionCurves,
                           tree_curves_PumpCurves,
                           tree_curves_RatingCurves,
                           tree_curves_ShapeCurves,
                           tree_curves_StorageCurves,
                           tree_curves_TidalCurves)

    tree_types = [
        [tree_hydrology_Subcatchments[0], Subcatchment, "subcatchments"],
        [tree_hydrology_RainGages[0], RainGage, "raingages"],
        [tree_hydrology_Aquifers[0], Aquifer, "aquifers"],
        [tree_hydrology_SnowPacks[0], SnowPack, "snowpacks"],
        [tree_hydrology_UnitHydrographs[0], UnitHydrograph, "hydrographs"],
        [tree_hydrology_LIDControls[0], LIDControl, "lid_controls"],
        [tree_nodes_Junctions[0], Junction, "junctions"],
        [tree_nodes_Outfalls[0], Outfall, "outfalls"],
        [tree_nodes_Dividers[0], Divider, "dividers"],
        [tree_nodes_StorageUnits[0], StorageUnit, "storage"],
        [tree_links_Conduits[0], Conduit, "conduits"],
        [tree_links_Pumps[0], Pump, "pumps"],
        [tree_links_Orifices[0], Orifice, "orifices"],
        [tree_links_Weirs[0], Weir, "weirs"],
        [tree_links_Outlets[0], Outlet, "outlets"],
        [tree_hydraulics_Transects[0], Transect, "transects"],
        [tree_quality_Pollutants[0], Pollutant, "pollutants"],
        [tree_quality_LandUses[0], Landuse, "landuses"],
        [tree_curves_ControlCurves[0], Curve, "curves"],
        [tree_curves_DiversionCurves[0], Curve, "curves"],
        [tree_curves_PumpCurves[0], Curve, "curves"],
        [tree_curves_RatingCurves[0], Curve, "curves"],
        [tree_curves_ShapeCurves[0], Curve, "curves"],
        [tree_curves_StorageCurves[0], Curve, "curves"],
        [tree_curves_TidalCurves[0], Curve, "curves"],
        [tree_TimeSeries[0], TimeSeries, "timeseries"],
        [tree_TimePatterns[0], Pattern, "patterns"],
        [tree_MapLabels[0], Label, "labels"]
    ]

    def __init__(self, q_application):
        frmMain.__init__(self, q_application)
        self.model = "SWMM"
        self.model_path = ''  # Set this only if needed later when running model
        self.output = None    # Set this when model output is available
        self.status_suffix = "_status.txt"
        self.status_file_name = ''  # Set this when model status is available
        self.output_filename = ''  # Set this when model output is available
        self.project_type = Project  # Use the model-specific Project as defined in core.swmm.project
        self.project_reader_type = ProjectReader
        self.project_writer_type = ProjectWriter
        self.project = Project()
        self.assembly_path = os.path.dirname(os.path.abspath(__file__))
        self.on_load(tree_top_item_list=self.tree_top_items)
        if self.map_widget:  # initialize empty model map layers, ready to have model elements added
            self.model_layers = ModelLayersSWMM(self.map_widget)

        HelpHandler.init_class(os.path.join(self.assembly_path, "swmm.qhc"))
        self.helper = HelpHandler(self)
        self.help_topic = "swmm/src/src/swmmsmainwindow.htm"

        self.actionStatus_ReportMenu = QtGui.QAction(self)
        self.actionStatus_ReportMenu.setObjectName(from_utf8("actionStatus_ReportMenu"))
        self.actionStatus_ReportMenu.setText(transl8("frmMain", "Status", None))
        self.actionStatus_ReportMenu.setToolTip(transl8("frmMain", "Display Simulation Status", None))
        self.menuReport.addAction(self.actionStatus_ReportMenu)
        QtCore.QObject.connect(self.actionStatus_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_status)

        self.actionSummary_ReportMenu = QtGui.QAction(self)
        self.actionSummary_ReportMenu.setObjectName(from_utf8("actionSummary_ReportMenu"))
        self.actionSummary_ReportMenu.setText(transl8("frmMain", "Summary", None))
        self.actionSummary_ReportMenu.setToolTip(transl8("frmMain", "Display Results Summary", None))
        self.menuReport.addAction(self.actionSummary_ReportMenu)
        QtCore.QObject.connect(self.actionSummary_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_summary)

        menu = QtGui.QMenu()
        submenuGraph = QtGui.QMenu(self.menuReport)
        submenuGraph.setTitle("Graph")
        self.menuReport.addMenu(submenuGraph)

        self.actionGraph_ProfileMenu = QtGui.QAction(self)
        self.actionGraph_ProfileMenu.setObjectName(from_utf8("actionGraph_ProfileMenu"))
        self.actionGraph_ProfileMenu.setText(transl8("frmMain", "Profile", None))
        self.actionGraph_ProfileMenu.setToolTip(transl8("frmMain", "Display Profile Plot", None))
        submenuGraph.addAction(self.actionGraph_ProfileMenu)
        QtCore.QObject.connect(self.actionGraph_ProfileMenu, QtCore.SIGNAL('triggered()'), self.report_profile)

        self.actionGraph_TimeSeriesMenu = QtGui.QAction(self)
        self.actionGraph_TimeSeriesMenu.setObjectName(from_utf8("actionGraph_TimeSeriesMenu"))
        self.actionGraph_TimeSeriesMenu.setText(transl8("frmMain", "Time Series", None))
        self.actionGraph_TimeSeriesMenu.setToolTip(transl8("frmMain", "Display Time Series Plot", None))
        submenuGraph.addAction(self.actionGraph_TimeSeriesMenu)
        QtCore.QObject.connect(self.actionGraph_TimeSeriesMenu, QtCore.SIGNAL('triggered()'), self.report_timeseries)

        self.actionGraph_ScatterMenu = QtGui.QAction(self)
        self.actionGraph_ScatterMenu.setObjectName(from_utf8("actionGraph_ScatterMenu"))
        self.actionGraph_ScatterMenu.setText(transl8("frmMain", "Scatter", None))
        self.actionGraph_ScatterMenu.setToolTip(transl8("frmMain", "Display Scatter Plot", None))
        submenuGraph.addAction(self.actionGraph_ScatterMenu)
        QtCore.QObject.connect(self.actionGraph_ScatterMenu, QtCore.SIGNAL('triggered()'), self.report_scatter)

        self.actionTable_VariableMenu = QtGui.QAction(self)
        self.actionTable_VariableMenu.setObjectName(from_utf8("actionTable_VariableMenu"))
        self.actionTable_VariableMenu.setText(transl8("frmMain", "Table", None))
        self.actionTable_VariableMenu.setToolTip(transl8("frmMain", "Display Table", None))
        self.menuReport.addAction(self.actionTable_VariableMenu)
        QtCore.QObject.connect(self.actionTable_VariableMenu, QtCore.SIGNAL('triggered()'), self.report_variable)

        self.actionStatistics_ReportMenu = QtGui.QAction(self)
        self.actionStatistics_ReportMenu.setObjectName(from_utf8("actionStatistics_ReportMenu"))
        self.actionStatistics_ReportMenu.setText(transl8("frmMain", "Statistics", None))
        self.actionStatistics_ReportMenu.setToolTip(transl8("frmMain", "Display Results Statistics", None))
        self.menuReport.addAction(self.actionStatistics_ReportMenu)
        QtCore.QObject.connect(self.actionStatistics_ReportMenu, QtCore.SIGNAL('triggered()'), self.report_statistics)

        self.Help_Topics_Menu = QtGui.QAction(self)
        self.Help_Topics_Menu.setObjectName(from_utf8("Help_Topics_Menu"))
        self.Help_Topics_Menu.setText(transl8("frmMain", "Help Topics", None))
        self.Help_Topics_Menu.setToolTip(transl8("frmMain", "Display Help Topics", None))
        self.menuHelp.addAction(self.Help_Topics_Menu)
        QtCore.QObject.connect(self.Help_Topics_Menu, QtCore.SIGNAL('triggered()'), self.help_topics)

        self.Help_About_Menu = QtGui.QAction(self)
        self.Help_About_Menu.setObjectName(from_utf8("Help_About_Menu"))
        self.Help_About_Menu.setText(transl8("frmMain", "About", None))
        self.Help_About_Menu.setToolTip(transl8("frmMain", "About SWMM", None))
        self.menuHelp.addAction(self.Help_About_Menu)
        QtCore.QObject.connect(self.Help_About_Menu, QtCore.SIGNAL('triggered()'), self.help_about)

        self.map_widget.applyLegend()
        self.map_widget.LegendDock.setVisible(False)
        self.set_thematic_controls()
        self.cboMapSubcatchments.currentIndexChanged.connect(self.update_thematic_map)
        self.cboMapNodes.currentIndexChanged.connect(self.update_thematic_map)
        self.cboMapLinks.currentIndexChanged.connect(self.update_thematic_map)

        self.cbFlowUnits.currentIndexChanged.connect(self.cbFlowUnits_currentIndexChanged)
        self.cbOffset.currentIndexChanged.connect(self.cbOffset_currentIndexChanged)

        self.signalTimeChanged.connect(self.update_thematic_map)

    def cbFlowUnits_currentIndexChanged(self):
        import core.swmm.options
        self.project.options.flow_units = core.swmm.options.general.FlowUnits[self.cbFlowUnits.currentText()[12:]]

    def cbOffset_currentIndexChanged(self):
        import core.swmm.options
        self.project.options.link_offsets = core.swmm.options.general.LinkOffsets[self.cbOffset.currentText()[9:].upper()]

    def set_thematic_controls(self):
        self.allow_thematic_update = False
        self.cboMapSubcatchments.clear()
        self.cboMapSubcatchments.addItems(['None', 'Area', 'Width', '% Slope', '% Imperv', 'LID Controls'])
        self.cboMapNodes.clear()
        self.cboMapNodes.addItems(['None', 'Invert El.'])
        self.cboMapLinks.clear()
        self.cboMapLinks.addItems(['None', 'Max. Depth', 'Roughness', 'Slope'])
        if self.get_output():
            # Add object type labels to map combos if there are any of each type in output
            for attribute in SMO.SwmmOutputSubcatchment.attributes:
                self.cboMapSubcatchments.addItem(attribute.name)
            for attribute in SMO.SwmmOutputNode.attributes:
                self.cboMapNodes.addItem(attribute.name)
            for attribute in SMO.SwmmOutputLink.attributes:
                self.cboMapLinks.addItem(attribute.name)
        self.allow_thematic_update = True
        self.update_thematic_map()

    def update_thematic_map(self):
        if not self.allow_thematic_update:
            return

        if self.model_layers.subcatchments and self.model_layers.subcatchments.isValid():
            setting = self.cboMapSubcatchments.currentText()
            attribute = None
            setting_index = self.cboMapSubcatchments.currentIndex()
            if setting_index < 6:
                meta_item = Subcatchment.metadata.meta_item_of_label(setting)
                attribute = meta_item.attribute
            color_by = {}
            if attribute:  # Found an attribute of the subcatchment class to color by
                for subcatchment in self.project.subcatchments.value:
                    color_by[subcatchment.name] = float(getattr(subcatchment, attribute, 0))
            elif self.output:  # Look for attribute to color by in the output
                attribute = SMO.SwmmOutputSubcatchment.get_attribute_by_name(setting)
                if attribute:
                    values = SMO.SwmmOutputSubcatchment.get_attribute_for_all_at_time(self.output, attribute, self.time_index)
                    index = 0
                    for subcatchment in self.output.subcatchments.values():
                        color_by[subcatchment.name] = values[index]
                        index += 1
            if color_by:
                self.map_widget.applyGraduatedSymbologyStandardMode(self.model_layers.subcatchments, color_by)
                self.map_widget.LegendDock.setVisible(True)
            else:
                self.map_widget.set_default_polygon_renderer(self.model_layers.subcatchments)
            self.model_layers.subcatchments.triggerRepaint()

        if self.model_layers.nodes_layers:
            setting = self.cboMapNodes.currentText()
            attribute = None
            setting_index = self.cboMapNodes.currentIndex()
            if setting_index < 2:
                meta_item = Junction.metadata.meta_item_of_label(setting)
                attribute = meta_item.attribute
            color_by = {}
            if attribute:  # Found an attribute of the node class to color by
                for junction in self.project.junctions.value:
                    color_by[junction.name] = float(getattr(junction, attribute, 0))
                for outfall in self.project.outfalls.value:
                    color_by[outfall.name] = float(getattr(outfall, attribute, 0))
                for divider in self.project.dividers.value:
                    color_by[divider.name] = float(getattr(divider, attribute, 0))
                for storage in self.project.storage.value:
                    color_by[storage.name] = float(getattr(storage, attribute, 0))
            elif self.output:  # Look for attribute to color by in the output
                attribute = SMO.SwmmOutputNode.get_attribute_by_name(setting)
                if attribute:
                    values = SMO.SwmmOutputNode.get_attribute_for_all_at_time(self.output, attribute, self.time_index)
                    index = 0
                    for node in self.output.nodes.values():
                        color_by[node.name] = values[index]
                        index += 1
            for layer_type in self.model_layers.nodes_layers:
                if layer_type.isValid():
                    if color_by:
                        self.map_widget.applyGraduatedSymbologyStandardMode(layer_type, color_by)
                        self.map_widget.LegendDock.setVisible(True)
                    else:
                        self.map_widget.set_default_point_renderer(layer_type)
                    layer_type.triggerRepaint()

        if self.model_layers.conduits and self.model_layers.conduits.isValid():
            setting = self.cboMapLinks.currentText()
            attribute = None
            setting_index = self.cboMapLinks.currentIndex()
            if setting_index < 3:
                meta_item = Conduit.metadata.meta_item_of_label(setting)
                attribute = meta_item.attribute
            if setting_index == 3:
                # special case for slope
                attribute = 'slope'
            color_by = {}
            if attribute:  # Found an attribute of the conduit class to color by
                for conduit in self.project.conduits.value:
                    if attribute == 'max_depth':
                        for value in self.project.xsections.value:
                            if value.link == conduit.name:
                                color_by[conduit.name] = float(value.geometry1)
                    elif attribute == 'slope':
                        # have to do calcs to get slope
                        start_elev = 0.0
                        end_elev = 0.0
                        slope = 0.0
                        for junction in self.project.junctions.value:
                            if junction.name == conduit.inlet_node:
                                start_elev = junction.elevation
                            if junction.name == conduit.outlet_node:
                                end_elev = junction.elevation
                        for outfall in self.project.outfalls.value:
                            if outfall.name == conduit.inlet_node:
                                start_elev = outfall.elevation
                            if outfall.name == conduit.outlet_node:
                                end_elev = outfall.elevation
                        for divider in self.project.dividers.value:
                            if divider.name == conduit.inlet_node:
                                start_elev = divider.elevation
                            if divider.name == conduit.outlet_node:
                                end_elev = divider.elevation
                        for storage in self.project.storage.value:
                            if storage.name == conduit.inlet_node:
                                start_elev = storage.elevation
                            if storage.name == conduit.outlet_node:
                                end_elev = storage.elevation
                        if conduit.length > 0.0:
                            slope = abs((float(start_elev) - float(end_elev)) / float(conduit.length))
                        color_by[conduit.name] = float(slope)
                    else:
                        color_by[conduit.name] = float(getattr(conduit, attribute, 0))
            elif self.output:  # Look for attribute to color by in the output
                attribute = SMO.SwmmOutputLink.get_attribute_by_name(setting)
                if attribute:
                    values = SMO.SwmmOutputLink.get_attribute_for_all_at_time(self.output, attribute, self.time_index)
                    index = 0
                    for link in self.output.links.values():
                        color_by[link.name] = values[index]
                        index += 1
            if color_by:
                self.map_widget.applyGraduatedSymbologyStandardMode(self.model_layers.conduits, color_by)
                self.map_widget.LegendDock.setVisible(True)
            else:
                self.map_widget.set_default_line_renderer(self.model_layers.conduits)
            self.model_layers.conduits.triggerRepaint()

    def get_output(self):
        if not self.output:
            if os.path.isfile(self.output_filename):
                self.output = SMOutputWrapper.SwmmOutputObject(self.output_filename)
                self.horizontalTimeSlider.setMaximum(self.output.num_periods - 1)
        return self.output

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

    def report_profile(self):
        if self.get_output():
            self._frmProfilePlot = frmProfilePlot(self)
            self._frmProfilePlot.set_from(self.project, self.output) #self.get_output())
            self._frmProfilePlot.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_timeseries(self):
        if self.get_output():
            self._frmTimeSeriesPlot = frmTimeSeriesPlot(self)
            self._frmTimeSeriesPlot.set_from(self.project, self.output) #self.get_output())
            self._frmTimeSeriesPlot.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_scatter(self):
        if self.get_output():
            self._frmScatterPlot = frmScatterPlot(self)
            self._frmScatterPlot.set_from(self.project, self.get_output())
            self._frmScatterPlot.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_variable(self):
        if self.get_output():
            self._frmTableSelection = frmTableSelection(self)
            self._frmTableSelection.set_from(self.project, self.get_output())
            self._frmTableSelection.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_statistics(self):
        if self.get_output():
            self._frmStatisticsReportSelection = frmStatisticsReportSelection(self)
            self._frmStatisticsReportSelection.set_from(self.project, self.output)
            self._frmStatisticsReportSelection.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model output not found.\n"
                                    "Run the model to generate output.",
                                    QMessageBox.Ok)

    def report_summary(self):
        if not os.path.isfile(self.status_file_name):
            prefix, extension = os.path.splitext(self.project.file_name)
            if os.path.isfile(prefix + self.status_suffix):
                self.status_file_name = prefix + self.status_suffix
        if os.path.isfile(self.status_file_name):
            self._frmSummaryReport = frmSummaryReport(self)
            self._frmSummaryReport.set_from(self.project, self.status_file_name)
            self._frmSummaryReport.show()
        else:
            QMessageBox.information(None, self.model,
                                    "Model status not found.\n"
                                    "Run the model to generate model status.",
                                    QMessageBox.Ok)

    def calibration_data(self):
        self._frmCalibrationData = frmCalibrationData(self)
        self._frmCalibrationData.show()
        pass

    def get_editor(self, edit_name):
        frm = None
        # First handle special cases where forms need more than simply being created

        if edit_name == self.tree_quality_Pollutants[0]:
            edit_these = []
            if self.project and self.project.pollutants:
                if not isinstance(self.project.pollutants.value, basestring):
                    if isinstance(self.project.pollutants.value, list):
                        edit_these.extend(self.project.pollutants.value)
                if len(edit_these) == 0:
                    new_item = Pollutant()
                    new_item.name = "NewPollutant"
                    edit_these.append(new_item)
                    self.project.pollutants.value = edit_these
            frm = frmGenericPropertyEditor(self, edit_these, "SWMM Pollutant Editor")
            frm.helper = HelpHandler(frm)
            frm.help_topic = "swmm/src/src/pollutanteditordialog.htm"
        elif edit_name == self.tree_MapLabels[0]:
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
            frm = frmGenericPropertyEditor(self, edit_these, "SWMM Map Label Editor")
            frm.helper = HelpHandler(frm)
            frm.help_topic = "swmm/src/src/maplabeleditordialog.htm"
        elif edit_name in [item[0] for item in self.tree_items_using_name]:
            # in these cases the click on the tree diagram populates the lower left list, not directly to an editor
            return None
        elif edit_name == self.tree_links_Orifices[0] and len(self.project.orifices.value) == 0:
            return None
        elif edit_name == self.tree_links_Outlets[0] and len(self.project.outlets.value) == 0:
            return None
        elif edit_name == self.tree_links_Weirs[0] and len(self.project.weirs.value) == 0:
            return None
        elif edit_name == self.tree_links_Pumps[0] and len(self.project.pumps.value) == 0:
            return None
        elif edit_name == self.tree_nodes_Outfalls[0] and len(self.project.outfalls.value) == 0:
            return None
        elif edit_name == self.tree_nodes_Dividers[0] and len(self.project.dividers.value) == 0:
            return None
        elif edit_name == self.tree_nodes_StorageUnits[0] and len(self.project.storage.value) == 0:
            return None
        else:  # General-purpose case finds most editors from tree information
            frm = self.make_editor_from_tree(edit_name, self.tree_top_items)

        return frm

    def get_editor_with_selected_items(self, edit_name, selected_items):
        frm = None
        # First handle special cases where forms need more than simply being created

        if edit_name == "Pollutants":
            edit_these = []
            if self.project and self.project.pollutants:
                if not isinstance(self.project.pollutants.value, basestring):
                    if isinstance(self.project.pollutants.value, list):
                        for value in self.project.pollutants.value:
                            if value.name in selected_items:
                                edit_these.append(value)
            frm = frmGenericPropertyEditor(self, edit_these, "SWMM Pollutant Editor")
        elif edit_name == 'Map Labels':
            edit_these = []
            if self.project and self.project.labels:
                if not isinstance(self.project.labels.value, basestring):
                    if isinstance(self.project.labels.value, list):
                        for value in self.project.labels.value:
                            if value.name in selected_items:
                                edit_these.append(value)
            frm = frmGenericPropertyEditor(self, edit_these, "SWMM Map Label Editor")
        else:  # General-purpose case finds most editors from tree information
            frm = self.make_editor_from_tree(edit_name, self.tree_top_items, selected_items)
        return frm

    def get_object_list(self, category):
        ids = []
        if category == self.tree_curves_ControlCurves[0]:
            for curve in self.project.curves.value:
                if curve.curve_type == CurveType.CONTROL:
                    ids.append(curve.name)
        elif category == self.tree_curves_DiversionCurves[0]:
            for i in range(0, len(self.project.curves.value)):
                if self.project.curves.value[i].curve_type == CurveType.DIVERSION:
                    ids.append(self.project.curves.value[i].name)
        elif category == self.tree_curves_PumpCurves[0]:
            for i in range(0, len(self.project.curves.value)):
                curve_type = self.project.curves.value[i].curve_type
                if curve_type == CurveType.PUMP1 or curve_type == CurveType.PUMP2 or \
                    curve_type == CurveType.PUMP3 or curve_type == CurveType.PUMP4:
                    ids.append(self.project.curves.value[i].name)
        elif category == self.tree_curves_RatingCurves[0]:
            for i in range(0, len(self.project.curves.value)):
                if self.project.curves.value[i].curve_type == CurveType.RATING:
                    ids.append(self.project.curves.value[i].name)
        elif category == self.tree_curves_ShapeCurves[0]:
            for i in range(0, len(self.project.curves.value)):
                if self.project.curves.value[i].curve_type == CurveType.SHAPE:
                    ids.append(self.project.curves.value[i].name)
        elif category == self.tree_curves_StorageCurves[0]:
            for i in range(0, len(self.project.curves.value)):
                if self.project.curves.value[i].curve_type == CurveType.STORAGE:
                    ids.append(self.project.curves.value[i].name)
        elif category == self.tree_curves_TidalCurves[0]:
            for i in range(0, len(self.project.curves.value)):
                if self.project.curves.value[i].curve_type == CurveType.TIDAL:
                    ids.append(self.project.curves.value[i].name)
        elif category == self.tree_MapLabels[0]:
            for i in range(0, len(self.project.labels.value)):
                ids.append(self.project.labels.value[i].name)
        elif category == self.tree_nodes_StorageUnits[0]:
            for i in range(0, len(self.project.storage.value)):
                ids.append(self.project.storage.value[i].name)
        else:
            section = self.project.find_section(category)
            if section and isinstance(section.value, list):
                ids = [item.name for item in section.value]
            else:
                ids = None
        return ids

    def add_object_clicked(self, section_name):
        new_item = None
        for typ in self.tree_types:
            if typ[0] == section_name:
                new_item = typ[1]()
                new_item.name = "New"
                break

        if new_item:
            if section_name == self.tree_links_Orifices[0]:
                # need to add corresponding cross section
                new_xsection = CrossSection()
                new_xsection.name = new_item.name
                if len(self.project.xsections.value) == 0:
                    edit_these = [new_xsection]
                    self.project.xsections.value = edit_these
                else:
                    self.project.xsections.value.append(new_xsection)
            elif section_name == self.tree_curves_DiversionCurves[0]:
                new_item.curve_type = CurveType.DIVERSION
            elif section_name == self.tree_curves_PumpCurves[0]:
                new_item.curve_type = CurveType.PUMP1
            elif section_name == self.tree_curves_RatingCurves[0]:
                new_item.curve_type = CurveType.RATING
            elif section_name == self.tree_curves_ShapeCurves[0]:
                new_item.curve_type = CurveType.SHAPE
            elif section_name == self.tree_curves_StorageCurves[0]:
                new_item.curve_type = CurveType.STORAGE
            elif section_name == self.tree_curves_TidalCurves[0]:
                new_item.curve_type = CurveType.TIDAL
            self.add_item(new_item, section_name)
            self.show_edit_window(self.get_editor_with_selected_items(self.tree_section, new_item.name))

    def delete_object_clicked(self, section_name, item_name):
        if section_name == self.tree_hydrology_Subcatchments[0]:
            for value in self.project.subcatchments.value:
                if value.name == item_name:
                    self.project.subcatchments.value.remove(value)
        elif section_name == self.tree_hydrology_RainGages[0]:
            for value in self.project.subcatchments.value:
                if value.name == item_name:
                    self.project.raingages.value.remove(value)
        elif section_name == self.tree_hydrology_Aquifers[0]:
            for value in self.project.aquifers.value:
                if value.name == item_name:
                    self.project.aquifers.value.remove(value)
        elif section_name == self.tree_hydrology_SnowPacks[0]:
            for value in self.project.snowpacks.value:
                if value.name == item_name:
                    self.project.snowpacks.value.remove(value)
        elif section_name == self.tree_hydrology_UnitHydrographs[0]:
            for value in self.project.hydrographs.value:
                if value.name == item_name:
                    self.project.hydrographs.value.remove(value)
        elif section_name == self.tree_hydrology_LIDControls[0]:
            for value in self.project.lid_controls.value:
                if value.name == item_name:
                    self.project.lid_controls.value.remove(value)
        elif section_name == self.tree_nodes_Junctions[0]:
            for value in self.project.junctions.value:
                if value.name == item_name:
                    self.project.junctions.value.remove(value)
        elif section_name == self.tree_nodes_Outfalls[0]:
            for value in self.project.outfalls.value:
                if value.name == item_name:
                    self.project.outfalls.value.remove(value)
        elif section_name == self.tree_nodes_Dividers[0]:
            for value in self.project.dividers.value:
                if value.name == item_name:
                    self.project.dividers.value.remove(value)
        elif section_name == self.tree_nodes_StorageUnits[0]:
            for value in self.project.storage.value:
                if value.name == item_name:
                    self.project.storage.value.remove(value)
        elif section_name == self.tree_links_Conduits[0]:
            for value in self.project.conduits.value:
                if value.name == item_name:
                    self.project.conduits.value.remove(value)
        elif section_name == self.tree_links_Pumps[0]:
            for value in self.project.pumps.value:
                if value.name == item_name:
                    self.project.pumps.value.remove(value)
        elif section_name == self.tree_links_Orifices[0]:
            for value in self.project.orifices.value:
                if value.name == item_name:
                    self.project.orifices.value.remove(value)
        elif section_name == self.tree_links_Weirs[0]:
            for value in self.project.weirs.value:
                if value.name == item_name:
                    self.project.weirs.value.remove(value)
        elif section_name == self.tree_links_Outlets[0]:
            for value in self.project.outlets.value:
                if value.name == item_name:
                    self.project.outlets.value.remove(value)
        elif section_name == self.tree_hydraulics_Transects[0]:
            for value in self.project.transects.value:
                if value.name == item_name:
                    self.project.transects.value.remove(value)
        elif section_name == self.tree_quality_Pollutants[0]:
           for value in self.project.pollutants.value:
                if value.name == item_name:
                    self.project.pollutants.value.remove(value)
        elif section_name == self.tree_quality_LandUses[0]:
            for value in self.project.landuses.value:
                if value.land_use_name == item_name:
                    self.project.landuses.value.remove(value)
        elif section_name == self.tree_curves_ControlCurves[0]:
            for value in self.project.curves.value:
                if value.name == item_name and value.curve_type == CurveType.CONTROL:
                    self.project.curves.value.remove(value)
        elif section_name == self.tree_curves_DiversionCurves[0]:
            for value in self.project.curves.value:
                if value.name == item_name and value.curve_type == CurveType.DIVERSION:
                    self.project.curves.value.remove(value)
        elif section_name == self.tree_curves_PumpCurves[0]:
            for value in self.project.curves.value:
                if value.name == item_name and \
                        (value.curve_type == CurveType.PUMP1 or value.curve_type == CurveType.PUMP2
                         or value.curve_type == CurveType.PUMP3 or value.curve_type == CurveType.PUMP4):
                    self.project.curves.value.remove(value)
        elif section_name == self.tree_curves_RatingCurves[0]:
            for value in self.project.curves.value:
                if value.name == item_name and value.curve_type == CurveType.RATING:
                    self.project.curves.value.remove(value)
        elif section_name == self.tree_curves_ShapeCurves[0]:
            for value in self.project.curves.value:
                if value.name == item_name and value.curve_type == CurveType.SHAPE:
                    self.project.curves.value.remove(value)
        elif section_name == self.tree_curves_StorageCurves[0]:
            for value in self.project.curves.value:
                if value.name == item_name and value.curve_type == CurveType.STORAGE:
                    self.project.curves.value.remove(value)
        elif section_name == self.tree_curves_TidalCurves[0]:
            for value in self.project.curves.value:
                if value.name == item_name and value.curve_type == CurveType.TIDAL:
                    self.project.curves.value.remove(value)
        elif section_name == self.tree_TimeSeries[0]:
            for value in self.project.timeseries.value:
                if value.name == item_name:
                    self.project.timeseries.value.remove(value)
        elif section_name == self.tree_TimePatterns[0]:
            for value in self.project.patterns.value:
                if value.name == item_name:
                    self.project.patterns.value.remove(value)
        elif section_name == self.tree_MapLabels[0]:
            for value in self.project.labels.value:
                if value.name == item_name:
                    self.project.labels.value.remove(value)

    def run_simulation(self):
        self.output = None
        # First find input file to run
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
            prefix, extension = os.path.splitext(file_name)
            self.status_file_name = prefix + self.status_suffix
            self.output_filename = prefix + '.out'
            if self.output:
                self.output.close()
                self.output = None
            # if not os.path.exists(self.model_path):
            #     if 'darwin' in sys.platform:
            #         lib_name = 'libswmm.dylib'
            #     elif 'win' in sys.platform:
            #         lib_name = 'swmm5_x64.dll'
            #     else:  # Linux
            #         lib_name = 'libswmm_amd64.so'
            #     self.model_path = self.find_external(lib_name)
            #
            # if os.path.exists(self.model_path):
            #     try:
            #         from Externals.swmm.model.swmm5 import pyswmm
            #         model_api = pyswmm(file_name, self.status_file_name, self.output_filename, self.model_path)
            #         frmRun = frmRunSWMM(model_api, self.project, self)
            #         self._forms.append(frmRun)
            #         if not use_existing:
            #             # Read this project so we can refer to it while running
            #             frmRun.progressBar.setVisible(False)
            #             frmRun.lblTime.setVisible(False)
            #             frmRun.fraTime.setVisible(False)
            #             frmRun.fraBottom.setVisible(False)
            #             frmRun.showNormal()
            #             frmRun.set_status_text("Reading " + file_name)
            #
            #             self.project = Project()
            #             self.project.read_file(file_name)
            #             frmRun.project = self.project
            #
            #         frmRun.Execute()
            #         self.add_map_constituents()
            #         return
            #     except Exception as e1:
            #         print(str(e1) + '\n' + str(traceback.print_exc()))
            #         QMessageBox.information(None, self.model,
            #                                 "Error running model with library:\n {0}\n{1}\n{2}".format(
            #                                     self.model_path, str(e1), str(traceback.print_exc())),
            #                                 QMessageBox.Ok)
                # finally:
                #     try:
                #         if model_api and model_api.isOpen():
                #             model_api.ENclose()
                #     except:
                #         pass
                #     return

            # Could not run with library, try running with executable
            args = []
            if 'darwin' in sys.platform:
                exe_name = "swmm5.app"
            elif sys.platform == "linux2":
                exe_name = "swmm5"
            else:
                exe_name = "swmm5.exe"
            exe_path = self.find_external(exe_name)
            if os.path.isfile(exe_path):
                args.append(file_name)
                args.append(self.status_file_name)
                args.append(self.output_filename)
                # running the Exe
                status = StatusMonitor0(exe_path, args, self, model='SWMM')
                status.show()
                self.set_thematic_controls()
        else:
            QMessageBox.information(None, self.model, self.model + " input file not found", QMessageBox.Ok)

    def help_topics(self):
        self.helper.show_help()

    def help_about(self):
        self._frmAbout = frmAbout(self)
        self._frmAbout.show()
        pass

    def open_project_quiet(self, file_name, gui_settings, directory):
        frmMain.open_project_quiet(self, file_name, gui_settings, directory)
        ui.convenience.set_combo(self.cbFlowUnits, 'Flow Units: ' + self.project.options.flow_units.name)
        ui.convenience.set_combo(self.cbOffset, 'Offsets: ' + self.project.options.link_offsets.name)

        if self.time_widget:
            if self.project.options.dates.start_date == self.project.options.dates.end_date:
                self.labelStartTime.setText(self.project.options.dates.start_time)
                self.labelEndTime.setText(self.project.options.dates.end_time)
            else:
                self.labelStartTime.setText(self.project.options.dates.start_date)
                self.labelEndTime.setText(self.project.options.dates.end_date)
        if self.map_widget:
            try:
                self.model_layers.create_layers_from_project(self.project)
                self.map_widget.zoomfull()
            except Exception as ex:
                print(str(ex) + '\n' + str(traceback.print_exc()))


class ModelLayersSWMM(ModelLayers):
    """
    This class creates and manages the map layers that are directly linked to SWMM model elements.
    Layer names must match the text in the tree control for the corresponding model section.
    """
    def __init__(self, map_widget):
        ModelLayers.__init__(self, map_widget)
        addCoordinates = self.map_widget.addCoordinates
        addLinks = self.map_widget.addLinks
        self.junctions = addCoordinates(None, "Junctions")
        self.outfalls = addCoordinates(None, "Outfalls")
        self.dividers = addCoordinates(None, "Dividers")
        self.storage = addCoordinates(None, "Storage Units")
        self.raingages = addCoordinates(None, "Rain Gages")
        self.labels = addCoordinates(None, "Map Labels")
        self.pumps = addLinks(None, None, "Pumps", "name", QColor('red'), 1)
        self.orifices = addLinks(None, None, "Orifices", "name", QColor('green'), 1.5)
        self.outlets = addLinks(None, None, "Outlets", "name", QColor('pink'), 2)
        self.weirs = addLinks(None, None, "Weirs", "name", QColor('orange'), 2.5)
        self.conduits = addLinks(None, None, "Conduits", "name", QColor('gray'), 3.5)
        self.subcatchments = self.map_widget.addPolygons(None, "Subcatchments")
        self.set_lists()

    def set_lists(self):
        self.nodes_layers = [self.junctions, self.outfalls, self.dividers, self.storage]
        self.all_layers = [self.raingages, self.labels, self.pumps, self.orifices,
                           self.outlets, self.weirs, self.conduits, self.subcatchments]
        self.all_layers.extend(self.nodes_layers)

    def create_layers_from_project(self, project):
        ModelLayers.create_layers_from_project(self, project)
        addCoordinates = self.map_widget.addCoordinates
        addLinks = self.map_widget.addLinks

        # Add new layers containing objects from this project
        self.junctions = addCoordinates(project.junctions.value, "Junctions")
        self.outfalls = addCoordinates(project.outfalls.value, "Outfalls")
        self.dividers = addCoordinates(project.dividers.value, "Dividers")
        self.storage = addCoordinates(project.storage.value, "Storage Units")
        self.raingages = addCoordinates(project.symbols.value, "Rain Gages")
        self.labels = addCoordinates(project.labels.value, "Map Labels")
        coord = project.coordinates.value
        self.pumps = addLinks(coord, project.pumps.value, "Pumps", "name", QColor('red'), 1)
        self.orifices = addLinks(coord, project.orifices.value, "Orifices", "name", QColor('green'), 1.5)
        self.outlets = addLinks(coord, project.outlets.value, "Outlets", "name", QColor('pink'), 2)
        self.weirs = addLinks(coord, project.weirs.value, "Weirs", "name", QColor('orange'), 2.5)
        self.conduits = addLinks(coord, project.conduits.value, "Conduits", "name", QColor('gray'), 3.5)
        self.subcatchments = self.map_widget.addPolygons(project.polygons.value, "Subcatchments")
        self.set_lists()


if __name__ == '__main__':
    application = QtGui.QApplication(sys.argv)
    main_form = frmMainSWMM(application)
    main_form.show()
    sys.exit(application.exec_())
