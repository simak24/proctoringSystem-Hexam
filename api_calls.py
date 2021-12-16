from PIL import Image
import requests
from io import BytesIO
import cv2
import numpy as np
import json
base_url="http://127.0.0.1:8000/"

def get_test_details(test_id):
    path = "api/exam/"
    try:
        print("making call: ",base_url+path+test_id)
        r = requests.get(url=base_url+path+test_id)
        print(r)
        print(r.status_code)
        print(r.headers)
        print(r.json()['data'][0])




        return r.json()['data'][0]
    except:
        return None
# print(get_test_details("7c54028a-7fca-4447-94e9-d8e9f3780091"))
def get_student_details(email):
    path = "api/student/"
    try:
        print("making call: ",base_url+path+email)

        r = requests.get(url=base_url + path + email)
        print(r)
        print(r.status_code)
        print(r.headers)
        print(json.loads(r.json()['data'])[0])
        return json.loads(r.json()['data'])[0]
    except:
        return None
# get_student_details("lnew@gmail.com")
def get_student_img(email):
    student_details=get_student_details(email)
    print("student details",student_details)
    try:
        print("making call: ",student_details['path'])

        response = requests.get(student_details['path'])

        print("got img",response.content)
        img = Image.open(BytesIO(response.content))
        img = np.array(img)
        # cv2.imshow("photo",cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # cv2.waitKey(0)
        # 

        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except  Exception as e :
        print(e)
        return None

# get_student_img("testingAccount@gmail.com")

def put_reports(test_id,student_email,tab_switches,face_suspicion,eye_suspicion,test_content):
    try :
        path = "api/student/report/"

        # Making a PUT request
        r = requests.put(base_url+path+test_id, data={'studentEmail': student_email,'faceSuspicion': face_suspicion,'eyeSuspicion': eye_suspicion,'tabSwitches': tab_switches,'test_content':test_content})

        # check status code for response recieved
        # success code - 200
        print(r)

        # print content of request
        print(r.content)
        return True
    except:
        return False


# put_reports("d7689f6c-edde-4d06-ad14-","lk@gmail",31,30,30)

# print(get_test_details("c6c76b4a-bf53-4a9e-9c33-b86e11c53371"))
#
# from PIL import Image
# import requests
# from io import BytesIO
# import cv2
# import numpy as np
# response = requests.get("https://hexam.eu-gb.mybluemix.net/uploads/1590492232629banner-test.jpg")
#
# img = Image.open(BytesIO(response.content))
# img = np.array(img)
#
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# cv2.imshow("img",np.array(img) )
# while(True):
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break