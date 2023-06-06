import cv2 as cv
import face_recognition
from pathlib import Path
from datetime import datetime
import firebase_admin
import numpy as np
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://attendance-system-f2a4c-default-rtdb.firebaseio.com/",
    'storageBucket': "attendance-system-f2a4c.appspot.com"
})

bucket = storage.bucket()

capture = cv.VideoCapture(0)

known_faces_encoding = []
modeList = []
studentIds = []

capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480)


background_img = cv.imread('background/main_background.jpg')

for modetype in Path('background/modes').iterdir():
    type = cv.imread(f'{modetype}')
    modeList.append(type)


for face_file in Path('Faces').iterdir():
    init_file = face_recognition.load_image_file(face_file)
    encoding = face_recognition.face_encodings(init_file)[0]
    known_faces_encoding.append(encoding)
    studentIds.append(Path(face_file).stem)


mode = 0
counter = 0
id = -1

while True:
    isTrue, frame = capture.read()

    background_img[0:0+720, 835:835+445] = modeList[mode]

    resize_frame = cv.resize(frame, (0, 0), fx=0.25,
                             fy=0.25, interpolation=cv.INTER_AREA)

    face_locations = face_recognition.face_locations(
        resize_frame, model="hog")

    face_encoding = face_recognition.face_encodings(
        resize_frame, face_locations, model="small")
    if face_encoding:
        for encoding, locations in zip(face_encoding, face_locations):

            matches = face_recognition.compare_faces(
                known_faces_encoding, encoding, tolerance=0.6)

            if True in matches:
                first_match_index = matches.index(True)
                background_img[0:0+720, 835:835+445] = modeList[1]
                id = studentIds[first_match_index]
                print(id)

                if counter == 0:
                    counter = 1
                    mode = 1

            else:
                background_img[0:0+720, 835:835+445] = modeList[0]

            top_left = (locations[3]*4, locations[2]*4)
            bottom_right = (locations[1]*4, locations[0]*4)
            cv.rectangle(frame, top_left, bottom_right, (0, 0, 255), 3)

        if counter != 0:

            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                blob = bucket.get_blob(f'Faces/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgOfStudent = cv.imdecode(array, cv.COLOR_BGRA2BGR)

                prevTime = datetime.strptime(
                    studentInfo["last attendance time"], "%Y-%m-%d %H:%M:%S")
                Delay = (datetime.now() - prevTime).total_seconds()

                if Delay > 60:
                    ref = db.reference(f'Students/{id}')
                    studentInfo["total attendance"] += 1
                    studentInfo['passed'] = False
                    ref.child('passed').set(studentInfo['passed'])
                    ref.child("total attendance").set(
                        studentInfo["total attendance"])
                    ref.child("last attendance time").set(datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"))
                elif studentInfo['passed'] == True:
                    mode = 3
                    counter = 0
                    background_img[0:0+720, 835:835+445] = modeList[mode]

            if mode != 3:

                if 20 < counter < 30:

                    if True in matches:
                        if counter == 29:
                            ref1 = db.reference(f'Students/{id}')
                            studentInfo['passed'] = True
                            ref1.child('passed').set(studentInfo['passed'])
                        mode = 2
                        background_img[0:0+720, 835:835+445] = modeList[mode]

                if counter <= 20:

                    if True not in matches:
                        mode = 0
                        background_img[0:0+720, 835:835+445] = modeList[mode]

                    else:

                        cv.putText(background_img, f'{studentInfo["total attendance"]}', (900, 75),
                                   cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv.putText(background_img, f'{studentInfo["name"]}', (920, 470),
                                   cv.FONT_HERSHEY_COMPLEX, 1, (55, 55, 55), 1)
                        cv.putText(background_img, f'{studentInfo["major"]}', (1050, 600),
                                   cv.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv.putText(background_img, f'{id}', (1050, 525),
                                   cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1)
                        cv.putText(background_img, f'{studentInfo["standing"]}', (1200, 670),
                                   cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (55, 55, 55), 1)
                        cv.putText(background_img, f'{studentInfo["starting year"]}', (978, 670),
                                   cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (55, 55, 55), 1)
                        cv.putText(background_img, f'{studentInfo["year"]}', (1100, 670),
                                   cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (55, 55, 55), 1)

                        background_img[163:163+260, 936:936+245] = imgOfStudent

                counter += 1

                if counter >= 30:
                    mode = 0
                    counter = 0
                    studentInfo = []
                    imgOfStudent = []
                    background_img[0:0+720, 835:835+445] = modeList[mode]

    else:
        counter = 0
        mode = 0
        background_img[0:0+720, 835:835+445] = modeList[mode]

    background_img[150:150+480, 55:55+640] = frame
    cv.imshow('Attendance system', background_img)

    key = cv.waitKey(1)

    if key == ord('d'):
        break

capture.release()
cv.destroyAllWindows()
