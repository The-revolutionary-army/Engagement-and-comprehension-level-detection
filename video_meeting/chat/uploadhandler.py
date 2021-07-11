from django.core.files.storage import default_storage
from django.core.cache import cache
import cv2
import dlib
import numpy as np
import pandas as pd
from .apps import ChatConfig

def write_results(img, file):
    # detect faces
    detector = dlib.get_frontal_face_detector()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    roi = []
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()
        # if no face skip predictions
        if len(img[y1:y2, x1:x2]) <= 0:
            continue
        # append faces
        roi.append(cv2.resize(cv2.cvtColor(img[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY), (48,48)))
        # get predictions
        predictions = []
        if len(roi)>0:
            test_images = np.expand_dims(roi, axis=3)
            predictions = ChatConfig.states_model.predict(test_images)
    
    try:
        # write predictions as dataframe in csv
        states = {
            "engagement":[predictions[0][0][1]],
            "confusion":[predictions[1][0][1]],
            "boredom":[predictions[2][0][1]],
            "frustration":[predictions[3][0][1]]
        }
        df = pd.DataFrame(states)
        df.to_csv(file,mode='a', header=False, index = False)
        return True
    except UnboundLocalError:
        # if no predictions return false
        return False

def handle_uploaded_file(files):
    for file in files.keys():
        img = np.asarray(bytearray(files[file].read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return write_results(img, 'tmp/'+file+'.csv')