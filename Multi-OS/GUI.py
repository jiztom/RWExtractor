import time
from os.path import expanduser

from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
import xml.etree.ElementTree as ET
import XMLCreator as xml1
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QProcess
import pathlib as path
import csv
import datetime as dt

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin

    myappid = 'IowaStateUniversity.RWAutoExtractor.GUIExtractor.3.0.0'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

tree = ET.parse('parameters.xml')
root = tree.getroot()
elements = root.findall('*')

fileloc = elements[1].text
extrLoc = elements[2].text
imextXML = elements[3].text
# name_format = elements[4].text
Console = elements[4].text
process = elements[5].text
date_created = elements[0].find('dateCreated').text

filename = '../Archive/test.csv'
data = []

Log_Path = path.Path('Log')
logfile = f"ExtractionLog_" + dt.datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".log"

log_path_full = Log_Path / logfile
log_path_full = log_path_full.absolute()

# if not log_path_full.exists():
#     file1 = open(log_path_full, "w")
#     L = ["Starting Log of Image Extraction \n",
#          "The log started at " + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"]
#     file1.writelines(L)
#     file1.close()


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('Batch_GUI_03232021.ui', self)
        self.setWindowTitle("RW Auto Extractor")
        self.p = None
        self.Source_LineEdit.setPlainText(fileloc)
        self.Destination_LineEdit.setPlainText(extrLoc)
        self.ConsolePlayer_lineEdit.setPlainText(Console)
        self.XML_lineedit.setPlainText(imextXML)
        self.Multi_spinBox.setValue(int(process))
        self.csv_val = 0

        _convert = {
            Qt.Checked: True,
            Qt.Unchecked: False
        }

        self.CSV_CheckBox.stateChanged.connect(
            lambda v: self.result(_convert[v])
        )

        self.Source_Directory_Button.clicked.connect(self.choose_Source_directory)
        self.Parameter_Button.clicked.connect(self.choose_Parameter_file)
        self.ConsolePLayer_Button.clicked.connect(self.choose_Robotics_WorkBench)
        self.XML_file_button.clicked.connect(self.choose_XML_FIle)

        self.CSV_CheckBox.stateChanged.connect(self.Source_choice)

        self.Save_Button_1.clicked.connect(self.save_data)
        self.Save_Button_2.clicked.connect(self.save_data)
        # self.Save_Button_3.clicked.connect(self.save_data)

        self.StartButton.clicked.connect(self.start_process)

        # self.loadCsv(extrLoc)
        self.setWindowTitle("Robotics Workbench Extraction Automation")
        self.show()

    def save_data(self):
        global fileloc, extrLoc, Console, imextXML, process
        fileloc = self.Source_LineEdit.toPlainText()
        extrLoc = self.Destination_LineEdit.toPlainText()
        Console = self.ConsolePlayer_lineEdit.toPlainText()
        imextXML = self.XML_lineedit.toPlainText()
        process = self.Multi_spinBox.value()

        # print(f"Data Read. {fileloc} , {extrLoc},{name_format}")
        # self.writeCsv('test.csv')
        xml1.save_XML(fileloc, extrLoc, imextXML, Console, process, date_created)

        # print("File Saved.")

        self.Source_LineEdit.setPlainText(fileloc)
        self.Destination_LineEdit.setPlainText(extrLoc)
        self.ConsolePlayer_lineEdit.setPlainText(Console)
        self.XML_lineedit.setPlainText(imextXML)
        self.Multi_spinBox.setValue(process)
        self.message("Data Saved Sucessfully.")

    def result(self, v):
        print(v)

    def message(self, s):
        self.ScrollArea.appendPlainText(s)

    def start_process(self):
        global fileloc, extrLoc, imextXML, Console, process
        if self.p is None:  # No process running.
            self.StartButton.setEnabled(False)
            self.StartButton.setStyleSheet("background-color: green")
            self.save_data()
            self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.

            # To get any outputs and errors generated from the threads
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)  # Clean up once complete.

            # Starting the thread.
            program = path.Path('Extractor_new.py')
            # program = path.Path('Extractor.py')
            # program = path.Path('sample.py')
            program = str(program.absolute()).replace('\\', '/')
            self.p.start("python",
                         [
                             program,
                             fileloc, extrLoc, imextXML, Console, str(process), str(self.csv_val)])

    def handle_stderr(self):
        """Function to handle standard errors"""
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        # file1 = open(log_path_full, "a")  # append mode
        # file1.write(stderr)
        # file1.close()
        self.message(stderr)

    def handle_stdout(self):
        """Function to dead with standard outputs"""
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        # file1 = open(log_path_full, "a")  # append mode
        # file1.write(stdout)
        # file1.close()
        self.message(stdout)

    def process_finished(self):
        """Cleanup code"""
        self.message("Process finished.")
        self.StartButton.setStyleSheet("background-color: light grey")
        self.StartButton.setEnabled(True)
        self.p = None

    def handle_state(self, state):
        """State change Control function"""
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def Source_choice(self):
        """The checkbox association control"""
        if self.CSV_CheckBox.isChecked():
            self.csv_val = 1
            self.Source_Directory_Button.disconnect()
            self.Source_Directory_Button.setText("Select CSV File")
            self.Source_Directory_Button.clicked.connect(self.choose_Source_File)
        else:
            self.csv_val = 0
            self.Source_Directory_Button.disconnect()
            self.Source_Directory_Button.setText("Select Directory")
            self.Source_Directory_Button.clicked.connect(self.choose_Source_directory)

    def choose_Source_directory(self):
        """FUnction to point to the location of the source directory"""
        input_dir = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:', str(path.Path(fileloc).parent))
        self.message(f"Source set to {input_dir}")
        self.Source_LineEdit.setText(input_dir)

    def choose_Source_File(self):
        """Function to Load source file if the source is a CSV File (Kristine)"""
        input_dir = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', str(path.Path(fileloc).parent),
                                                          "Comma Separated Values Spreadsheet (*.csv);;"
                                                          "All Files (*)")
        self.message(f"Source set to {input_dir}")
        self.Source_LineEdit.setText(input_dir[0])

    def choose_Parameter_file(self):
        """Function to load the Parameter file location"""
        # input_dir = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', str(path.Path(extrLoc).parent),
        #                                                   "Comma Separated Values Spreadsheet (*.csv);;"
        #                                                   "All Files (*)")
        input_dir = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:', str(path.Path(fileloc).parent))
        self.message(f"Destination Folder set to {input_dir}")
        self.Destination_LineEdit.setText(input_dir)
        # self.loadCsv(input_dir[0])

    def choose_Robotics_WorkBench(self):
        """Function to point towards the location of the active Console Player"""
        input_dir = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', str(path.Path(Console).parent))
        self.message(f"Console Player set to {input_dir[0]}")
        self.ConsolePlayer_lineEdit.setText(input_dir[0].replace('\\', '/'))

    def choose_XML_FIle(self):
        """Function to load the Base XML file to be parsed"""
        input_dir = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', str(path.Path(imextXML).parent))
        print(input_dir[0])
        self.message(f"XML file set to {input_dir[0]}")
        self.XML_lineedit.setText(input_dir[0])

    def loadCsv(self, fileName):
        """Loading the selected parameter file into the GUI for viewing"""
        with open(fileName, "r") as fileInput:
            for row in csv.reader(fileInput):
                items = [
                    QtGui.QStandardItem(field)
                    for field in row
                ]
                self.model.appendRow(items)
        with open(fileName, "r") as f:
            reader = csv.reader(f)
            data = list(reader)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('tractor-512.ico'))
    window = Ui()
    app.exec_()
