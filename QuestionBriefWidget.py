import sys
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from ui import *

class QuestionBriefWidget(QWidget):
    def __init__(self,index,question):

        super(QuestionBriefWidget,self).__init__()
        loadUi('ui/questionbrief.ui',self)
        self.label_2.setText("Q"+str(index)+".")

        self.label.setText(question['question'])





