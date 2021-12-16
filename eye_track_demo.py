import cv2
import dlib
import numpy as np
import math
import csv
import pickle
from sklearn.linear_model import LogisticRegression

def shape_to_np(landmarks, dtype="int"):
    # initialize the list of (x, y)-coordinates
    # coords = np.zeros((68, 2), dtype=dtype)
    # # loop over the 68 facial landmarks and convert them
    # # to a 2-tuple of (x, y)-coordinates
    # for i in range(0, 68):
    #     coords[i] = (shape.part(i).x, shape.part(i).y)
    # # return the list of (x, y)-coordinates
    # return coords

    pos = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(0, 68)]
    pos = np.array(pos)
    return pos


def eye_on_mask(mask, side):
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask


def contouring(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key=cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        if right:
            cx += mid
        print("center:",cx," : ",cy)
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
        return [cx,cy]
    except:
        return [-1,-1]
        pass


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')

left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]
imp_landmarks=[1,2,16,17,28,29,30]
landmarks_dataset=[]
landmarks_logreg=[[39,0],[40,0],[41,0],[37,1],[38,1],[28,1]]



cap = cv2.VideoCapture(0)
ret, img = cap.read()
thresh = img.copy()

cv2.namedWindow('image')
kernel = np.ones((3, 3), np.uint8)

def calculateDistance(x1,y1,x2,y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def nothing(x):
    pass


cv2.createTrackbar('threshold', 'image', 0, 255, nothing)

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (450, 30)
fontScale              = 1
fontColor              = (0, 0, 255)
lineType               = 2


while (True and len(landmarks_dataset)<500):
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    # cv2.imshow('eyes', img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    if len(rects)==0:
        cv2.putText(img, 'Suspicious Activity! Face away from screen',
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)

    for rect in rects:
        dataset_row=[]
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)

        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        mask = eye_on_mask(mask, left)
        mask = eye_on_mask(mask, right)

        mask = cv2.dilate(mask, kernel, 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[39][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        # threshold = cv2.getTrackbarPos('threshold', 'image')
        # print("threshold:",threshold)
        threshold = 51
        _, binary_img = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        binary_img = cv2.erode(binary_img, None, iterations=2)  # 1
        binary_img = cv2.dilate(binary_img, None, iterations=4)  # 2
        binary_img = cv2.medianBlur(binary_img, 3)  # 3
        binary_img = cv2.bitwise_not(binary_img)

        # thresh = cv2.erode(thresh, None, iterations=2)
        # thresh = cv2.dilate(thresh, None, iterations=4)
        # thresh = cv2.medianBlur(thresh, 5)
        lx,ly=contouring(binary_img[:, 0:mid], mid, img)
        rx,ry=contouring(binary_img[:, mid:], mid, img, True)
        print(lx,rx,ly,ry)
        if lx == -1 and rx == -1:

            cv2.putText(img, 'Suspicious Activity Eyeball!',
                        bottomLeftCornerOfText,
                        font,
                        fontScale,
                        fontColor,
                        lineType)
        # else:
        #
        #     if lx==-1:
        #         dataset_row_x=[rx,rx]
        #         dataset_row_y=[ry,ry]
        #     elif rx==-1:
        #         dataset_row_x=[lx,lx]
        #         dataset_row_y=[ly,ly]
        #     else:
        #         dataset_row_x=[lx,rx]
        #         dataset_row_y=[ly,ry]
        #
        #
        #     # for creating dataset
        #     for landmark_index in imp_landmarks + left + right:
        #         print(shape[landmark_index])
        #         dataset_row_x.append(shape[landmark_index][0])
        #         dataset_row_y.append(shape[landmark_index][1])
        #     dataset_row=[x -min(dataset_row_x) for x in dataset_row_x]
        #     dataset_row+=[y -min(dataset_row_y) for y in dataset_row_y]
        #     landmarks_dataset.append(dataset_row)
        #     print(dataset_row)
        #     cv2.putText(img, str(len(landmarks_dataset)),
        #                 (10,300),
        #                 font,
        #                 fontScale,
        #                 fontColor,
        #                 lineType)
        mindist_left = 100
        mindist_right=100
        for (x, y) in shape[36:42]:

                if(calculateDistance(x,y,lx,ly)<mindist_left):
                    mindist_left=calculateDistance(x,y,lx,ly)

        for (x, y) in shape[42:48]:

                if (calculateDistance(x, y, rx, ry) < mindist_right):
                    mindist_right = calculateDistance(x, y, rx, ry)



        mindist_threshold=calculateDistance(shape[36][0], shape[36][1], shape[40][0], shape[40][1])/4

        # if logistic regression is to be used
        # logreg = pickle.load(open("models/eye_suspicion_detection_model.sav", 'rb'))
        # X=[]
        # for x,y in landmarks_logreg:
        #    X.append(shape[x][y])
        # result = logreg.predict(np.array(X).reshape(1,-1))

        # if result[0]==1:
        if mindist_left<mindist_threshold or mindist_right <mindist_threshold:
        #
            cv2.putText(img, 'Suspicious Activity Eyeball!',
                        bottomLeftCornerOfText,
                        font,
                        fontScale,
                        fontColor,
                        lineType)
        # cv2.putText(img,  str(mindist_left)+ " : " +str(mindist_right),
        #             (100,30),
        #             font,
        #             0.5,
        #             fontColor,
        #             lineType)
        # cv2.putText(img, str(mindist_threshold) ,
        #             (100, 50),
        #             font,
        #             0.5,
        #             fontColor,
        #             lineType)
        for (x, y) in shape[36:48]:
            cv2.circle(img, (x, y), 2, (0, 255, 0), -1)

        # for (x, y) in shape:
        #     cv2.circle(img, (x, y), 2, (0, 255, 0), -1)

    cv2.putText(img, 'Press Esc to exit',
                (10, 30),
                font,
                fontScale,
                fontColor,
                lineType)
    # show the image with the face detections + facial landmarks
    cv2.imshow('eyes', img)
    # cv2.imshow("image", binary_img)
    # print(thresh)
    k = cv2.waitKey(10)
    if k == 27:
        break


# for single image test
# img = cv2.imread('down.png')
#
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# rects = detector(gray, 1)
#
# for rect in rects:
#     shape = predictor(gray, rect)
#     shape = shape_to_np(shape)
#
#     mask = np.zeros(img.shape[:2], dtype=np.uint8)
#     mask = eye_on_mask(mask, left)
#     mask = eye_on_mask(mask, right)
#
#     mask = cv2.dilate(mask, kernel, 5)
#     eyes = cv2.bitwise_and(img, img, mask=mask)
#     mask = (eyes == [0, 0, 0]).all(axis=2)
#     eyes[mask] = [255, 255, 255]
#     mid = (shape[42][0] + shape[39][0]) // 2
#     eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
#     # threshold = cv2.getTrackbarPos('threshold', 'image')
#     # print(threshold)
#     threshold = 50
#     _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
#     thresh = cv2.erode(thresh, None, iterations=2)  # 1
#     thresh = cv2.dilate(thresh, None, iterations=4)  # 2
#     thresh = cv2.medianBlur(thresh, 3)  # 3
#     thresh = cv2.bitwise_not(thresh)
#     lx,ly=contouring(thresh[:, 0:mid], mid, img)
#     rx,ry=contouring(thresh[:, mid:], mid, img, True)
#     if lx==-1 or rx==-1:
#         cv2.putText(img, 'Suspicious Activity',
#                     (600, 10),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     1,
#                     (255,0,0),
#                     2)
#     i=36
#     mindist_left=100
#     mindist_right=100
#
#     for (x, y) in shape[36:42]:
#
#         if(calculateDistance(x,y,lx,ly)<mindist_left):
#             mindist_left=calculateDistance(x,y,lx,ly)
#
#     for (x, y) in shape[42:48]:
#
#         if (calculateDistance(x, y, rx, ry) < mindist_right):
#             mindist_right = calculateDistance(x, y, rx, ry)
#     print("Left mindist:",mindist_left,"right_mindist:",mindist_right)
#     for (x, y) in shape[36:48]:
#         print(i,") ",x," : ",y)
#         i+=1
#         cv2.circle(img, (x, y), 2, (255, 0, 0), -1)
# # show the image with the face detections + facial landmarks
# cv2.imshow('eyes', img)
#
# while(True):
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break


cap.release()
cv2.destroyAllWindows()

# for creating dataset

# with open('eye_suspicion/eye_landmarks.csv', 'w', newline='') as file:
#     writer = csv.writer(file)
#     title_row=["suspicious","left_eyeball_x","left_eyeball_y"]
#
#     for x in left+right+imp_landmarks:
#         title_row.append((str(x)+'x'))
#     title_row+=["right_eyeball_x","right_eyeball_y"]
#     for x in left + right + imp_landmarks:
#         title_row.append((str(x)+'y'))
#     writer.writerow(title_row)
#
#     for row in landmarks_dataset:
#         writer.writerow([1]+row)


