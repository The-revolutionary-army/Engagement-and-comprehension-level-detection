from django.core.files.storage import default_storage
from django.core.cache import cache
import cv2
import dlib
import numpy as np
import pandas as pd
from .apps import ChatConfig

def write_results(img, file):
    # detect faces
    try:
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
            if len(img[y1:y2, x1:x2]) <= 0 or len(img[y1-100:y2+100, x1-100:x2+100]) <= 0:
                continue
            # append faces
            roi.append(cv2.resize(cv2.cvtColor(img[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY), (48,48)))
            au = ChatConfig.au_model.predict(cv2.cvtColor(img[y1-100:y2+100, x1-100:x2+100], cv2.COLOR_BGR2RGB))
            # get predictions
            predictions = []
            if len(roi)>0:
                test_images = np.expand_dims(roi, axis=3)
                predictions = ChatConfig.states_model.predict(test_images)
    
    
        # write predictions as dataframe in csv
        states = {
            "engagement":[round(predictions[0][0][1],3)],
            "confusion":[round(predictions[1][0][1],3)],
            "boredom":[round(predictions[2][0][1],3)],
            "frustration":[round(predictions[3][0][1],3)],
        }
        pos_au = au["AU02"]+au["AU05"]+au["AU12"]
        neg_au = au["AU04"]+au["AU07"]+au["AU15"]
        neg_state = (round(states["confusion"][0])+round(states["boredom"][0])+round(states["frustration"][0]))
        pos_state = 3-neg_state
        eng=states["engagement"][0]
        states["comprehension"]=[np.sign(max(0,eng*(pos_au+pos_state-neg_au-neg_state)))]


        df = pd.DataFrame(states)
        df.to_csv(file,mode='a', header=False, index = False)
        return True
    except UnboundLocalError:
        # if no predictions return false
        return False
    except:
        return False

def handle_uploaded_file(files):
    for file in files.keys():
        img = np.asarray(bytearray(files[file].read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return write_results(img, 'tmp/'+file+'.csv')
