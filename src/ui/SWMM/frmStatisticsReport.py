import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import core.swmm.project
from ui.SWMM.frmStatisticsReportDesigner import Ui_frmStatisticsReport
from ui.help import HelpHandler


class frmStatisticsReport(QtGui.QMainWindow, Ui_frmStatisticsReport):

    def __init__(self, main_form):
        QtGui.QMainWindow.__init__(self, main_form)
        self.help_topic = "swmm/src/src/viewingastatisticsreport.htm"
        self.setupUi(self)
        QtCore.QObject.connect(self.cmdCancel, QtCore.SIGNAL("clicked()"), self.cmdCancel_Clicked)

        # self.set_from(parent.project)
        self._main_form = main_form

    def set_from(self, project, output, object_name, object_id, variable_name, event_name, stat_name,
                 threshold_value, event_volume, separation_time):
        self.project = project
        self.output = output

        self.object_name = object_name      # Subcatchment
        self.object_id = object_id          # 1
        self.variable_name = variable_name  # Precipitation
        self.event_name = event_name        # Daily
        self.stat_name = stat_name          # Mean
        self.threshold_value = threshold_value   # 0
        self.event_volume = event_volume         # 0
        self.separation_time = separation_time   # 6

        self.setWindowTitle('SWMM Statistics ' + '- ' + self.object_name + ' ' + self.object_id + ' ' + self.variable_name)
        self.textEdit.setReadOnly(True)

        # y_values, units = output.get_series_by_name(type_label, object_id, attribute, start_index, num_steps)
        units = '(in/hr)'
        volume_units = '(in)'
        start_date = '01/01/1998'
        end_date = '01/02/1998'

        # Ustats.GetStats(Stats, EventList, Results)

        EventList = []
        results_n = '2'
        results_frequency = '0.194'
        results_minimum = '0.300'
        results_maximum = '0.410'
        results_mean = '0.355'
        results_std_deviation = '0.078'
        results_skewness_coeff = '0.000'

        if self.event_name == "Event-Dependent":
            frequency_note = '  *Fraction of all reporting periods belonging to an event.'
            self.event_name = 'Variable'
            self.event_units = units
        elif self.event_name == "Daily":
            frequency_note = '  *Fraction of all days containing an event.'
            self.event_units = '(days)'
        elif self.event_name == "Monthly":
            frequency_note = '  *Fraction of all months containing an event.'
            self.event_units = '(months)'
        else:
            frequency_note = '  *Fraction of all years containing an event.'
            self.event_units = '(years)'

        summary_string = '  S U M M A R Y   S T A T I S T I C S' + '\n' + '  ===================================' + '\n' + \
                              '  Object  .............. ' + self.object_name + ' ' + self.object_id  + '\n' + \
                              '  Variable ............. ' + self.variable_name + '  ' + units + '\n' + \
                              '  Event Period ......... ' + self.event_name + '\n' + \
                              '  Event Statistic ...... ' + self.stat_name + '  ' + self.event_units + '\n' + \
                              '  Event Threshold ...... ' + self.variable_name + ' > ' + self.threshold_value + '  ' + units + '\n' + \
                              '  Event Threshold ...... Event Volume > ' + self.event_volume + ' ' + volume_units + '\n' + \
                              '  Event Threshold ...... Separation Time >= ' + self.separation_time + ' (hr)' + '\n' + \
                              '  Period of Record ..... ' + start_date + ' to ' + end_date + '\n' + \
                              ' ' + '\n' + \
                              '  Number of Events ..... ' + results_n + '\n' + \
                              '  Event Frequency*...... ' + results_frequency + '\n' + \
                              '  Minimum Value ........ ' + results_minimum + '\n' + \
                              '  Maximum Value ........ ' + results_maximum + '\n' + \
                              '  Mean Value ........... ' + results_mean + '\n' + \
                              '  Std. Deviation ....... ' + results_std_deviation + '\n' + \
                              '  Skewness Coeff. ...... ' + results_skewness_coeff + '\n' + \
                              ' ' + '\n' + frequency_note

        self.textEdit.setText(summary_string)

        # Events Tab (grid)

        if self.event_name == 'Variable':
            self.event_name = 'Event'

        column_headers = ['Rank',
                          'Start Date',
                          self.event_name + '\n' + 'Duration' + '\n' + '(hours)',
                          self.event_name + '\n' + self.stat_name + '\n' + self.event_units,
                          'Exceedance' + '\n' + 'Frequency' + '\n' + '(percent)',
                          'Return' + '\n' + 'Period' + '\n' + '(months)']

        if self.stat_name == 'Inter-Event Time':
            column_headers[3] = 'Inter-Event' + '\n' + 'Time' + '\n' + self.event_units

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        if len(EventList) == 0:
            num_rows = 2
        else:
            num_rows = len(EventList) + 1
        self.tableWidget.setRowCount(num_rows)

    def cmdCancel_Clicked(self):
        self.close()
