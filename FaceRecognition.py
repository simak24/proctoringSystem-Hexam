import cv2
import face_recognition
import numpy as np
import glob

class FaceRecognition:


    def load_img(self, path):
        image = face_recognition.load_image_file(path)
        return image

    def load_known_images(self, img_paths):
        self.known_images = []
        for img_path in img_paths:
            image = self.load_img(img_path)
            self.known_images.append(image)

        self.known_face_encodings = []

        for i,image in enumerate(self.known_images):
            try:
                encode = self.get_encode(image)
                print(i)
                self.known_face_encodings.append(encode)
            except Exception:
                pass
        print(len(self.known_images))
        print(len(self.known_face_encodings))
        # return self.known_images

    def encode_known_images(self, images):
        self.known_images = images

        self.known_face_encodings = []

        for i,image in enumerate(self.known_images):
            try:
                encode = self.get_encode(image)
                print(i)
                self.known_face_encodings.append(encode)
            except Exception:
                pass
        print(len(self.known_images))
        print(len(self.known_face_encodings))
        # return self.known_images

    def get_encode(self, image):
        face_encoding = face_recognition.face_encodings(image)[0]
        return face_encoding

    # def Encoding(self, known_images):
    #     self.known_face_encodings = []
    #
    #     for image in known_images:
    #         encode = get_encode(image)
    #         known_face_encodings.append(encode)
    #
    #     return self.known_face_encodings

    def is_face_match(self, im):

        # im=get_img(img_path)

        face_locations = face_recognition.face_locations(im)
        face_encodings = face_recognition.face_encodings(im, face_locations)


        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                # first_match_index = matches.index(True)
                # name = known_face_names[first_match_index]
                return True

            # Or instead, use the known face with the smallest distance to the new face
            # face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            #
            # best_match_index = np.argmin(face_distances)
            #
            # if matches[best_match_index]:
            #     is_Present = True
            #     break
                # name = known_face_names[best_match_index]

                # Draw a box around the face
                # cv2.rectangle(im, (left, top), (right, bottom), (0, 0, 255), 2)

                # # Draw a label with a name below the face
                # cv2.rectangle(im, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                # font = cv2.FONT_HERSHEY_DUPLEX
                # cv2.putText(im, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # cv2.imwrite('/content/drive/My Drive/Books/savedata/'+str(i)+' sec.jpg', im)
                # i=i+1

        return False

# recog= FaceRecognition()
# recog.load_known_images(glob.glob("savedimages/*.jpg"))
# print(glob.glob("savedimages/*.jpg"))
#
# cap = cv2.VideoCapture(0)
#
# while(True):
#     ret,frame=cap.read()
#
#     if recog.is_face_match(frame):
#         cv2.putText(frame, "Face Verified", (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 0), 3,
#                     2)
#     cv2.imshow("Face Verification", frame)
#     # cv2.putText(outOpencvDnn, "yo", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3, cv2.LINE_AA)
#
#     k = cv2.waitKey(10)
#     if k == 27:
#         break
