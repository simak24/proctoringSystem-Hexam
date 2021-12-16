import numpy as np
import cv2
import dlib
import math

class EyeTracker():

    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
        self.left_eye_coords = [36, 37, 38, 39, 40, 41]
        self.right_eye_coords = [42, 43, 44, 45, 46, 47]
        self.kernel = np.ones((3, 3), np.uint8)

    def landmark_to_pos(self,landmarks, dtype="int"):
        pos=[(landmarks.part(i).x, landmarks.part(i).y) for i in range(0,68)]
        pos=np.array(pos)
        return pos

    def create_eye_mask(self,landmarks,mask, side):
        eye_coords = [landmarks[i] for i in side]
        eye_coords = np.array(eye_coords, dtype=np.int32)
        mask = cv2.fillConvexPoly(mask, eye_coords, 255)
        return mask

    def calculateDistance(self,x1,y1,x2,y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def contouring(self,binary_img, mid, img, right=False):
        cnts, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        try:
            cnt = max(cnts, key=cv2.contourArea)
            M = cv2.moments(cnt)
            x = int(M['m10'] / M['m00'])
            y = int(M['m01'] / M['m00'])
            if right:
                x += mid
            print("center:", x, " : ", y)
            cv2.circle(img, (x, y), 4, (0, 0, 255), 2)
            return [x, y]
        except:
            return [-1, -1]
            pass
    def is_image_suspicious(self,img):

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray, 1)

        if len(rects) == 0:
            return True
        for rect in rects:
            landmarks = self.predictor(gray, rect)
            landmarks = self.landmark_to_pos(landmarks)

            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            mask = self.create_eye_mask(landmarks,mask, self.left_eye_coords)
            mask = self.create_eye_mask(landmarks,mask, self.right_eye_coords)

            mask = cv2.dilate(mask, self.kernel, 5)
            eyes = cv2.bitwise_and(img, img, mask=mask)
            mask = (eyes == [0, 0, 0]).all(axis=2)
            eyes[mask] = [255, 255, 255]
            mid = (landmarks[42][0] + landmarks[39][0]) // 2
            eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
            # threshold = cv2.getTrackbarPos('threshold', 'image')
            # print(threshold)
            threshold = 52
            _, binary_img = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
            binary_img = cv2.erode(binary_img, None, iterations=2)  # 1
            binary_img = cv2.dilate(binary_img, None, iterations=4)  # 2
            binary_img = cv2.medianBlur(binary_img, 3)  # 3
            binary_img = cv2.bitwise_not(binary_img)
            lx, ly = self.contouring(binary_img[:, 0:mid], mid, img)
            rx, ry = self.contouring(binary_img[:, mid:], mid, img, True)
            print(lx, rx, ly, ry)
            if lx == -1 and rx == -1:
                return True
            mindist_left = 100
            mindist_right = 100
            for (x, y) in landmarks[36:42]:

                if (self.calculateDistance(x, y, lx, ly) < mindist_left):
                    mindist_left = self.calculateDistance(x, y, lx, ly)

            for (x, y) in landmarks[42:48]:

                if (self.calculateDistance(x, y, rx, ry) < mindist_right):
                    mindist_right = self.calculateDistance(x, y, rx, ry)

            mindist_threshold = self.calculateDistance(landmarks[36][0], landmarks[36][1], landmarks[40][0], landmarks[40][1]) / 4.8
            if mindist_left < mindist_threshold or mindist_right < mindist_threshold:
                return True

        return False
