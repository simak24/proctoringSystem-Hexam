
import sys
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from ui import *


class QuestionMCQWidget(QWidget):
    def __init__(self,index,question):

        super(QuestionMCQWidget,self).__init__()
        loadUi('ui/questionmcq.ui',self)
        self.label_2.setText("Q"+str(index)+".")

        self.label.setText(question['question'])


        self.radioButton.setText(question['options'][0])
        self.radioButton_2.setText(question['options'][1])
        self.radioButton_3.setText(question['options'][2])
        self.radioButton_4.setText(question['options'][3])
