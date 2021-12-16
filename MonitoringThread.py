from PyQt5.QtCore import QThread,pyqtSignal
import cv2
from EyeTracker import EyeTracker
import time
from FaceRecognition import FaceRecognition
from FaceDetecterDnn import FaceDetectionDnn
import glob

class MonitoringThread(QThread):
    report_signal = pyqtSignal(int, int,int)
    def __init__(self,known_faces,eyeTrack=False):
        super(MonitoringThread,self).__init__()
        self.eyeTrack=eyeTrack
        self.total_frames=0
        self.faceRecognition = FaceRecognition()
        # self.faceRecognition.load_known_images(glob.glob("savedimages/*.jpg"))
        self.faceRecognition.encode_known_images(known_faces)

        self.dnnDetector = FaceDetectionDnn()
        self.verifySuspicionCount=0
        self.verifiedFramesCount = 0
        self.eyeTrackSuspicionCount = 0

        self.stop=False

        if (eyeTrack):
            print("init")
            self.eyeTracker = EyeTracker()



    def run(self):
        cap = cv2.VideoCapture(0)
        verified = False
        checked = False
        frame_text=""
        un_checked_count=0
        while (True ):
            ret, frame = cap.read()
            self.total_frames += 1

            frame_dnn, dnn_bboxes = self.dnnDetector.detectFaceOpenCVDnn(frame)

            if (len(dnn_bboxes)) != 1:
                verified = False
                checked = False
                frame_text = "Suspicious Activity"
                bbox_color = (0, 0, 255)

            else:
                if not checked or un_checked_count==10:
                    un_checked_count=0
                    if self.faceRecognition.is_face_match(frame):
                        verified = True
                        bbox_color = (0, 255, 0)
                        frame_text = "Face Verified"
                    else:
                        verified = False
                        bbox_color = (0, 0, 255)
                        frame_text = "Wrong Face"

                    checked = True
                else:
                    un_checked_count+=1
            start=time.time()


            if verified:
                self.verifiedFramesCount+=1
                print("verified")
                if self.eyeTrack:

                    if self.eyeTracker.is_image_suspicious(frame):
                        self.eyeTrackSuspicionCount +=1
                        print("eye")
                        cv2.putText(frame, 'Eyeball Suspicion!',
                                    (700,50),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    1.4,
                                    (0,0,255),
                                    3,2)


            print("time:",time.time()-start)
            cv2.putText(frame, frame_text, (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, bbox_color, 3, 2)
            for bbox in dnn_bboxes:
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), bbox_color,
                              int(round(frame.shape[0] / 150)), 8)
            # cv2.imshow("Face Verification", frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

            if self.stop:
                self.report_signal.emit(self.verifiedFramesCount,self.eyeTrackSuspicionCount,self.total_frames)
                cap.release()
                cv2.destroyAllWindows()
                break

    def stop_monitoring(self):
        self.stop=True
# MonitoringThread(True).start()




