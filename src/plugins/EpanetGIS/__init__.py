try:
    from qgis.core import *
    from qgis.gui import *
    from PyQt4 import QtGui, QtCore, Qt
    from PyQt4.QtGui import QMessageBox
    from core.coordinate import Coordinate
    from core.epanet.hydraulics.link import Pipe
    import os

    plugin_name = "EpanetGIS"
    plugin_create_menu = True
    __all__ = {"Export to GIS": 1,
               "Import from GIS": 2}

    def run(session=None, choice=None):
        print("run " + str(choice))
        if not session or not session.project:
            result = "Project is not open"
        else:
            try:
                if choice == 1:
                    gui_settings = QtCore.QSettings("EPANET", "GUI")
                    directory = gui_settings.value("GISPath", os.path.dirname(session.project.file_name))
                    file_name = QtGui.QFileDialog.getSaveFileName(session, "Export to GIS", directory,
                                                                  "GeoJSON (*.json);;Shapefile (*.shp);;All files (*.*)")
                    if file_name:
                        path_only, file_only = os.path.split(file_name)
                        if path_only != directory:
                            gui_settings.setValue("GISPath", path_only)
                            gui_settings.sync()
                            del gui_settings

                    # file_name = os.path.join(os.path.dirname(session.project.file_name), "pipes.json")
                    print("export to " + file_name)

                    links = session.project.pipes.value
                    attributes = {"type": "type",
                                  "name": "name",
                                  "description": "description",
                                  "inlet_node": "inlet_node",
                                  "outlet_node": "outlet_node",
                                  "length": "length",
                                  "diameter": "diameter",
                                  "roughness": "roughness",
                                  "loss_coefficient": "loss_coefficient"}
                    save_links(session.project, links, file_name, attributes)

                    result = "Saved " + file_name

                elif choice == 2:
                    gui_settings = QtCore.QSettings("EPANET", "GUI")
                    directory = gui_settings.value("ImportGIS", "")
                    file_name = QtGui.QFileDialog.getOpenFileName(session, "Select GIS file to import", directory,
                                                                  "GeoJSON (*.json);;Shapefile (*.shp);;All files (*.*)")
                    if file_name:
                        path_only, file_only = os.path.split(file_name)
                        if path_only != directory:
                            gui_settings.setValue("ImportGIS", path_only)
                            gui_settings.sync()
                            del gui_settings

                        section = session.project.pipes

                        if len(section.value) > 0:
                            msg = QMessageBox()
                            msg.setText("Discard " + str(len(section.value)) + " pipes already in model before import?")
                            msg.setWindowTitle("Importing Pipes")
                            msg.setIcon(QMessageBox.Question)
                            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                            retval = msg.exec_()
                            if retval == QMessageBox.Yes:
                                section.value = []
                            elif retval == QMessageBox.No:
                                pass
                            elif retval == QMessageBox.Cancel:
                                return
                            print("value of pressed message box button:", retval)

                        attributes = {"name":             "name",
                                      "description":      "description",
                                      "inlet_node":       "inlet_node",
                                      "outlet_node":      "outlet_node",
                                      "length":           "length",
                                      "diameter":         "diameter",
                                      "roughness":        "roughness",
                                      "loss_coefficient": "loss_coefficient"}
                        """ Dictionary of attribute names in vector layer: attribute names of EPANET object.
                            Edit strings in the left column as needed to match layer being imported.
                            If a field is not available in the GIS layer, leave an empty string in the left column.
                         """

                        result = load_links(session.project, section.value, file_name, attributes, Pipe)
                        session.map_widget.addLinks(session.project.coordinates.value,
                                                    section.value, "Pipes", "name", QtGui.QColor('gray'))
                        session.map_widget.zoomfull()
                else:
                    result = "Selected operation not yet implemented."
                QMessageBox.information(None, plugin_name, result, QMessageBox.Ok)
            except Exception as ex:
                print str(ex)

    def load_links(project, links, file_name, attributes, model_type):
        count = 0
        try:
            layer = QgsVectorLayer(file_name, "import", "ogr")
            if layer:
                for feature in layer.getFeatures():
                    geom = feature.geometry()
                    if geom.type() == QGis.Line:
                        line = geom.asPolyline()
                        model_item = model_type()
                        for layer_attribute, model_attribute in attributes.items():
                            attr_value = feature[layer_attribute]
                            setattr(model_item, model_attribute, attr_value)
                            index = -1
                            if model_attribute == "inlet_node":
                                index = 0
                            elif model_attribute == "outlet_node":
                                index = len(line) - 1
                            if index >= 0:
                                for existing_coord in project.coordinates.value:
                                    if existing_coord.name == attr_value:
                                        project.coordinates.value.remove(existing_coord)
                                new_coord = Coordinate()
                                new_coord.name = attr_value
                                new_coord.x = line[index].x()
                                new_coord.y = line[index].y()
                                project.coordinates.value.append(new_coord)
                        links.append(model_item)
                        count += 1
        except Exception as ex:
            print(str(ex))
        return "Imported " + str(count) + " features"

    def save_links(project, links, file_name, attributes):
        coordinates = project.coordinates.value
        layer = QgsVectorLayer("LineString", "links", "memory")
        provider = layer.dataProvider()

        # add fields
        fields = []
        for layer_attribute, model_attribute in attributes.items():
            fields.append(QgsField(model_attribute, QtCore.QVariant.String))
        provider.addAttributes(fields)

        features = []
        # Receivers = as in the above example 'Receivers' is a list of results
        for link in links:
            inlet_coord = None
            outlet_coord = None
            for coordinate_pair in coordinates:
                if coordinate_pair.name == link.inlet_node:
                    inlet_coord = coordinate_pair
                if coordinate_pair.name == link.outlet_node:
                    outlet_coord = coordinate_pair
                if inlet_coord and outlet_coord:
                    # add a feature
                    feature = QgsFeature()
                    feature.setGeometry(QgsGeometry.fromPolyline([
                        QgsPoint(float(inlet_coord.x), float(inlet_coord.y)),
                        QgsPoint(float(outlet_coord.x), float(outlet_coord.y))]))

                    values = []
                    for layer_attribute, model_attribute in attributes.items():
                        if model_attribute == "type":
                            values.append(type(link).__name__)
                        else:
                            values.append(getattr(link, model_attribute, ''))
                    feature.setAttributes(values)
                    features.append(feature)
                    break  # stop looking for more coordinates

        # changes are only possible when editing the layer
        layer.startEditing()
        provider.addFeatures(features)
        layer.commitChanges()
        layer.updateExtents()

        if file_name.lower().endswith("shp"):
            driver_name = "ESRI Shapefile"
        else:
            driver_name = "GeoJson"
        QgsVectorFileWriter.writeAsVectorFormat(layer, file_name, "utf-8", layer.crs(), driver_name)


except Exception as ex:
    print "Skip loading plugin: " + str(ex)