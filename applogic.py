import sys
from PyQt5.QtCore import pyqtSlot,QTimer
import json
from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5.uic import loadUi
from ui import *
from api_calls import *
from TestDetailsWindow import TestDetailsWindow
from TestWindow import TestWindow
from SubmitWindow import SubmitWindow
from MonitoringThread import MonitoringThread
# dummy_data='{ ' \
#            '  "test_id": 123,' \
#            '  "test_title":"Advanced Internet Technology",' \
#            '  "test_description":"Second Unit Test",' \
#            '  "test_duration":1,' \
#            '  "test_deadline":"19/05/20 19:55:00",' \
#            '  "student_img":"base64string",' \
#            '  "eye_track":false,' \
#            ' "questions":[' \
#            '    {' \
#            '      "question_id":1,' \
#            '      "question_type":0,' \
#            '      "question":"Which of the following domains is used for — profit businesses??",' \
#            '      "options":[".net",".edu",".com",".org"]' \
#            '    },' \
#            '    {' \
#            '      "question_id":2,' \
#            '      "question_type":0,' \
#            '      "question":"What is the full form of USB as used in computer-related activities?"' \
#            '    }' \
#            '    ]' \
#            '}'

dummy_questions_data='{  "questions":[' \
           '    {' \
           '      "question_id":1,' \
           '      "question_type":0,' \
           '      "question":"Which of the following domains is used for — profit businesses?",' \
           '      "options":[".net",".edu",".com",".org"]' \
           '    },' \
           '    {' \
           '      "question_id":2,' \
           '      "question_type":0,' \
           '      "question":"What is the full form of USB as used in computer-related activities?",' \
           '      "options":["Universal Security Block","Universal Serial Bus","United Serial Bus","Ultra Security Block"]' \
           '    },' \
           '    {' \
           '      "question_id":3,' \
           '      "question_type":1,' \
           '      "question":"What is the name of a webpage address?",' \
           '      "options":["Directory","Protocol","URL","Domain"]' \
           '    },' \
           '    {' \
           '      "question_id":4,' \
           '      "question_type":0,' \
           '      "question":"Which of the following represents billion characters?",' \
           '      "options":["Megabytes","Kilobytes","Gigabytes","Chigabytes"]' \
           '    },' \
           '    {' \
           '      "question_id":5,' \
           '      "question_type":1,' \
           '      "question":"Which technologies  accomplish less power ?",' \
           '      "options":["Serial Bus Mouse","Random Access Memory","Blu Ray Drive","SSD"]' \
           '    }'\
           '    ]' \
           '    }'
class MainPage(QMainWindow):
    def __init__(self):
        super(MainPage,self).__init__()

        loadUi('ui/firstpage.ui',self)
        self.label_5.setText("")
        # self.label_6.setText("")

        self.pushButton.clicked.connect(self.moveToTestDetails)



    def moveToTestDetails(self):
        # self.label_6.setText("Loading...")
        # self.label_6.repaint()
        self.email=self.lineEdit.text()
        self.test_id=self.lineEdit_2.text()

        self.test_details_dict=get_test_details(self.test_id)
        self.test_details_dict['duration']=int(self.test_details_dict['duration'])
        print("test detils:",self.test_details_dict)
        print("testid: ",self.test_id)
        print("emaiil: ",self.email)
        if self.test_details_dict is None:
            self.label_5.setText("Invalid Test ID")
            # self.label_6.setText("")
            self.label_5.repaint()
            # self.label_6.repaint()

        else:
            self.label_5.setText("")
            self.label_5.repaint()

            self.student_img=get_student_img(self.email)
            if self.student_img is None:
                self.label_5.setText("Invalid Email")
                self.label_5.repaint()

            else:
                self.label_5.setText("")
                self.label_5.repaint()

                # self.label_6.setText("")
                # self.label_6.repaint()
                # self.test_details_dict=json.loads(dummy_data)
                self.test_details_dict['eye_track']=True
                self.questions_dict=json.loads(dummy_questions_data)
                self.test_details_dict['questions']=self.questions_dict['questions']
                # self.label_6.setText("")
                # self.label_6.repaint()

                self.hide()
                print("going to next page")
                self.testDetails = TestDetailsWindow(self.test_details_dict,[self.student_img])
                self.testDetails.startTestSignal.connect(self.moveToTestWindow)

                self.testDetails.show()


    def moveToTestWindow(self,saved_faces):

        self.testDetails.hide()
        self.testWindow = TestWindow(self.test_details_dict)

        self.monitorThread= MonitoringThread([self.student_img]+saved_faces,self.test_details_dict['eye_track'])
        self.monitorThread.report_signal.connect(self.monitor_report_slot)
        self.total_frames=-1
        self.monitorThread.start()
        self.testWindow.show()
        self.testWindow.pushButton_3.clicked.connect(self.submit_test)
        self.testWindow.setFocus()
        app.focusChanged.connect(self.onFocusChange)

        self.timer_start()

    def monitor_report_slot(self,verifiedFramesCount,eyeTrackSuspicionCount,total_frames):

        self.testWindow.hide()
        test_duration_seconds = self.test_details_dict['duration'] * 60
        app_switch_percent = int(
            (self.offscreen_time / (test_duration_seconds-(self.min_left*60+self.sec_left)) * 100))
        self.testWindow.qtimer.stop()



        # face_sus = int((verifiedFramesCount / total_frames) * 100)
        # if(verifiedFramesCount==total_frames):
        #     eye_sus=0
        # else:
        #     eye_sus = int((eyeTrackSuspicionCount / verifiedFramesCount) * 100)

        print("Eye track",self.test_details_dict['eye_track'])
        reportArray=[]
        for briefWidget in self.testWindow.breiefWidgets:
            questionObj={}
            questionObj['isSubjective']=True
            questionObj['question']=briefWidget.label.text()

            questionObj['answer']=briefWidget.plainTextEdit.toPlainText()
            reportArray.append((questionObj))
        print(reportArray)
        reportArray=json.dumps(reportArray)
        self.submitWindow = SubmitWindow(self.test_details_dict['eye_track'],self.offscreen_time, app_switch_percent,
                                         verifiedFramesCount, eyeTrackSuspicionCount,total_frames,self.test_details_dict['_id'],self.email,reportArray)

        self.submitWindow.show()

    def onFocusChange(self):
        print("is active:",self.testWindow.isActiveWindow())

        try:

            self.submitWindow.isActiveWindow()
            print("here")
        except:
            if not self.testWindow.isActiveWindow():
                self.offscreen_interval = self.min_left * 60 + self.sec_left
            else:

                self.offscreen_time += self.offscreen_interval - (self.min_left * 60 + self.sec_left)
                self.offscreen_interval = self.min_left * 60 + self.sec_left


    def timer_start(self):
        self.min_left = self.test_details_dict['duration']
        self.sec_left = 0
        self.offscreen_time=0
        self.testWindow.qtimer.timeout.connect(self.timer_timeout)
        self.testWindow.qtimer.start(1000)

        self.update_timer()

    def timer_timeout(self):
        if self.min_left==0 and self.sec_left==0:
            self.testWindow.qtimer.stop()
            self.submit_test()

        elif(self.sec_left==0):
            self.min_left-=1
            self.sec_left=59

        else:
            self.sec_left-=1


        self.update_timer()

    def update_timer(self):
        self.testWindow.label_3.setText(str(self.min_left))
        self.testWindow.label_5.setText(str(self.sec_left))


    def submit_test(self):

        self.testWindow.label_7.setVisible(True)

        self.monitorThread.stop=True



def focus():
    print("focus")
app =QApplication(sys.argv)
widget=MainPage()
widget.show()

# app.focusWindowChanged(focus)
sys.exit(app.exec_())
