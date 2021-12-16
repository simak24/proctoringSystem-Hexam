import cv2
from FaceRecognition import FaceRecognition
class FaceCalibration():
    def __init__(self,known_faces):
        # self.start_calibration()
        self.modelFile = "models/opencv_face_detector_uint8.pb"
        self.configFile = "models/opencv_face_detector.pbtxt"
        self.net = cv2.dnn.readNetFromTensorflow(self.modelFile, self.configFile)

        self.conf_threshold = 0.8
        self.faceRecognition = FaceRecognition()
        # self.faceRecognition.load_known_images(glob.glob("savedimages/*.jpg"))
        self.faceRecognition.encode_known_images(known_faces)



        self.faceCascade = cv2.CascadeClassifier('models/haarcascade_profileface.xml')


    def detectFaceOpenCVHaar(self,faceCascade, frame, inHeight=300, inWidth=0):
        frameOpenCVHaar = frame.copy()
        frameHeight = frameOpenCVHaar.shape[0]
        frameWidth = frameOpenCVHaar.shape[1]
        if not inWidth:
            inWidth = int((frameWidth / frameHeight) * inHeight)

        scaleHeight = frameHeight / inHeight
        scaleWidth = frameWidth / inWidth

        frameOpenCVHaarSmall = cv2.resize(frameOpenCVHaar, (inWidth, inHeight))
        frameGray = cv2.cvtColor(frameOpenCVHaarSmall, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(frameGray)
        bboxes = []
        for (x, y, w, h) in faces:
            x1 = x
            y1 = y
            x2 = x + w
            y2 = y + h
            cvRect = [int(x1 * scaleWidth), int(y1 * scaleHeight),
                      int(x2 * scaleWidth), int(y2 * scaleHeight)]
            bboxes.append(cvRect)
            cv2.rectangle(frameOpenCVHaar, (cvRect[0], cvRect[1]), (cvRect[2], cvRect[3]), (0, 255, 0),
                          int(round(frameHeight / 150)), 4)
        return frameOpenCVHaar, bboxes


    def detectFaceOpenCVDnn(self,net, frame):
        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], False, False)

        net.setInput(blob)
        detections = net.forward()
        bboxes = []
        # print(detections)
        for i in range(detections.shape[2]):

            confidence = detections[0, 0, i, 2]
            if confidence > self.conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                bboxes.append([x1, y1, x2, y2])
                cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)
        return frameOpencvDnn, bboxes

    def verify_face(self,frame):

        return self.faceRecognition.is_face_match(frame)

    def start_calibration(self):
        cap = cv2.VideoCapture(0)

        verification_phase=True
        right_phase=False
        left_phase=False

        right_phase_count = 0
        left_phase_count = 0


        saved_faces=[]
        while (True):
            bbox_color = (0, 255, 0)
            hasFrame, frame = cap.read()
            frame = cv2.flip(frame, 1)

            outOpencvDnn, dnn_bboxes  = self.detectFaceOpenCVDnn(self.net, frame)
            if len(dnn_bboxes) ==0:
                verification_phase=True

            if verification_phase:
                right_phase_count = 0
                left_phase_count = 0
                saved_faces = []

                bbox_color = (0, 255, 255)
                cv2.putText(outOpencvDnn, "Look Straight into the camera to verify face", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, bbox_color, 3,
                            cv2.LINE_AA)
                if self.verify_face(frame):
                    verification_phase=False
                    right_phase=True
            elif right_phase:
                cv2.putText(outOpencvDnn, "Face Verified", (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 0), 3,
                            cv2.LINE_AA)
                cv2.putText(outOpencvDnn, "Slowly move your head towards your right", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 0), 3,
                            cv2.LINE_AA)

                outOpencvHaar, bboxes = self.detectFaceOpenCVHaar(self.faceCascade, cv2.flip(outOpencvDnn, 1))

                print(right_phase_count)
                if right_phase_count ==11:
                    right_phase=False
                    left_phase=True

                elif len(bboxes)==1:
                    bbox_color = (255, 255, 0)
                    right_phase_count+=1
                    if right_phase_count % 5==0:
                        saved_faces.append(frame[bboxes[0][1]:bboxes[0][3],bboxes[0][0]:bboxes[0][2]])
                        # cv2.imwrite('savedimages/'+str(right_phase_count)+".jpg",saved_faces[-1])

                # cv2.imshow("Face Calibration", outOpencvHaar)

            elif left_phase:


                if left_phase_count ==11:
                    cv2.destroyAllWindows()
                    cap.release()
                    print("breaking")
                    break

                cv2.putText(outOpencvDnn, "Face Verified", (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 0), 3,
                            cv2.LINE_AA)
                cv2.putText(outOpencvDnn, "Slowly move your head towards your left", (100, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 0, 0), 3,
                            cv2.LINE_AA)
                outOpencvHaar, bboxes = self.detectFaceOpenCVHaar(self.faceCascade, outOpencvDnn)

                if len(bboxes)==1:
                    bbox_color = (255, 0, 0)
                    left_phase_count+=1
                    if left_phase_count % 5==0:
                        saved_faces.append(frame[bboxes[0][1]:bboxes[0][3],bboxes[0][0]:bboxes[0][2]])
                        # cv2.imwrite('savedimages/l'+str(left_phase_count)+".jpg",saved_faces[-1])

                # cv2.imshow("Face Calibration", outOpencvHaar)

            for bbox in dnn_bboxes:
                cv2.rectangle(outOpencvDnn, (bbox[0],bbox[1] ), (bbox[2], bbox[3]), bbox_color, int(round(frame.shape[0] / 150)), 8)
            cv2.putText(outOpencvDnn, "Press Esc to exit", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3,
                        cv2.LINE_AA)
            cv2.imshow("Face Calibration", outOpencvDnn)
            # cv2.putText(outOpencvDnn, "yo", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3, cv2.LINE_AA)




            k = cv2.waitKey(10)
            if k == 27:
                cv2.destroyAllWindows()
                cap.release()

                return [],True
        print("destroying")
        # cv2.destroyAllWindows()
        # cap.release()
        print("destroyed")
        return saved_faces,False


# FaceCalibration().start_calibration()