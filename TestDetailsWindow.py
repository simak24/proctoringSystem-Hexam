import sys
from PyQt5.QtCore import pyqtSlot,pyqtSignal

from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5.uic import loadUi
from ui import *
from FaceCalibration import FaceCalibration

class TestDetailsWindow(QMainWindow):
    startTestSignal = pyqtSignal(list)
    def __init__(self,test_details_dict,known_faces):

        super(TestDetailsWindow,self).__init__()
        loadUi('ui/testdetails.ui',self)
        self.faceCalibration=FaceCalibration(known_faces)
        self.label_6.setText(test_details_dict['title'])
        self.label_7.setText(test_details_dict['description'])
        self.label_8.setText(str(test_details_dict['duration'])+" minutes")
        self.label_9.setText(test_details_dict['end']+" "+test_details_dict['date'])

        self.pushButton.clicked.connect(self.start_calibration)

    def start_calibration(self):

        saved_faces,esc_pressed=self.faceCalibration.start_calibration()
        print(esc_pressed)
        if not esc_pressed:
            self.startTestSignal.emit(saved_faces)
