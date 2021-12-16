import cv2
import glob
from FaceRecognition import FaceRecognition
from FaceDetecterDnn import FaceDetectionDnn
# print(glob.glob("savedimages/*.jpg"))

recog= FaceRecognition()
recog.load_known_images(glob.glob("savedimages/*.jpg"))

cap = cv2.VideoCapture(0)

verified=False
checked=False

dnnDetector=FaceDetectionDnn()
bbox_color = (0, 0, 255)
frame_text=""
not_checked_count=0
while(True):
    ret,frame=cap.read()
    # frame = cv2.flip(frame, 1)


    frame_dnn, dnn_bboxes=dnnDetector.detectFaceOpenCVDnn(frame)

    if(len(dnn_bboxes))!=1:
        checked = False
        frame_text = "Suspicious Activity"
        bbox_color=(0,0,255)



    else:
        if not checked or not_checked_count==10000:
            not_checked_count=0
            if recog.is_face_match(frame):
                verified=True
                bbox_color=(0,255,0)
                frame_text="Face Verified"
            else:
                verified = False
                bbox_color=(0,0,255)
                frame_text = "Wrong Face"

            checked=True
        else:
            not_checked_count+=1
    cv2.putText(frame, frame_text, (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, bbox_color, 3, 2)
    for bbox in dnn_bboxes:
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), bbox_color,
                      int(round(frame.shape[0] / 150)), 8)
    cv2.imshow("Face Verification", frame)
    # cv2.putText(outOpencvDnn, "yo", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3, cv2.LINE_AA)

    k = cv2.waitKey(10)
    if k == 27:
        break
