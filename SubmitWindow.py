import sys
from PyQt5.QtCore import QTimer

from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from QuestionMCQWidget import QuestionMCQWidget
from QuestionBriefWidget import QuestionBriefWidget

from ui import *
from api_calls import *

class SubmitWindow(QMainWindow):
    def __init__(self,eye_track,switch_duration,app_switching_percent,verified_frames,eye_sus,total_frames,test_id,student_email,test_content):

        super(SubmitWindow,self).__init__()
        loadUi('ui/submitwindow.ui',self)
        print("switch_duration",switch_duration)
        # self.label_3.setText(str(int(switch_duration/60)))
        # self.label_5.setText(str(switch_duration%60))
        self.test_content=test_content
        self.label_8.setText(str(app_switching_percent)+"%")

        # self.label_10.setText(str(total_frames-verified_frames)+"/"+str(total_frames))
        #
        # self.label_14.setText(str(eye_sus)+"/"+str(verified_frames))
        self.label_13.setHidden(not eye_track)
        self.label_14.setHidden(not eye_track)
        self.face_sus_percent=int(((total_frames-verified_frames)/total_frames)*100)
        self.eye_sus_percent=int((eye_sus/total_frames)*100)

        self.label_10.setText(str(self.eye_sus_percent) +"%")
        #
        self.label_14.setText(str(self.face_sus_percent)+"%")

        self.app_switching_percent=app_switching_percent
        self.student_email=student_email
        self.test_id=test_id
        # put_reports(test_id,student_email,app_switching_percent,face_sus_percent,eye_sus_percent)
        self.pushButton.clicked.connect(self.submit_report)

    def submit_report(self):
        isSuccess=put_reports(self.test_id,self.student_email,self.app_switching_percent,self.face_sus_percent,self.eye_sus_percent,self.test_content)

        if(isSuccess):
            self.label_2.setText("Report Submitted!")
            self.label_2.repaint()

