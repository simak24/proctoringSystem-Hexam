import sys
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from QuestionMCQWidget import QuestionMCQWidget
from QuestionBriefWidget import QuestionBriefWidget

from ui import *


class TestWindow(QMainWindow):
    def __init__(self,test_details_dict):

        super(TestWindow,self).__init__()
        loadUi('ui/testwindow.ui',self)
        self.label_7.setVisible(False)
        self.qIndex=2
        self.numQuestions=len(test_details_dict['questions'])

        self.label.setText(test_details_dict['title'])
        self.qustionWidgets=[]
        self.breiefWidgets=[]
        for index,question in enumerate(test_details_dict['questions']):
            questionWidget=None

            print(question)
            if(question['question_type']==0):

                questionWidget=QuestionMCQWidget(index+1,test_details_dict['questions'][index])
            else:
                questionWidget = QuestionBriefWidget(index+1,test_details_dict['questions'][index])
                self.breiefWidgets.append(questionWidget)

            self.qustionWidgets.append(questionWidget)
            self.stackedWidget.addWidget(questionWidget)


        self.pushButton.clicked.connect(self.prevQuestion)

        self.pushButton_2.clicked.connect(self.nextQuestion)
        self.stackedWidget.setCurrentIndex(2)

        self.qtimer = QTimer(self)


    def prevQuestion(self):
        self.qIndex-=1
        self.qIndex=self.numQuestions+1 if self.qIndex==1 else self.qIndex
        self.stackedWidget.setCurrentIndex(self.qIndex)

    def nextQuestion(self):
        self.qIndex+=1
        self.qIndex=2 if self.qIndex==self.numQuestions+2 else self.qIndex
        self.stackedWidget.setCurrentIndex(self.qIndex)


