import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
import pandas as pd
import dlib
import pickle
import multiprocessing
import logging
import time

labels_data = pd.read_csv('labels/AllLabels.csv')
labels_data.head()

def thread_function(dataPath, ttv, user, extract, clip, ts):
    detector = dlib.get_frontal_face_detector()
    frames = []
    labels = []
    #print("Thread extracting start: ", ts)
    for imagepath in clip:
        try:
            if imagepath[-3:] != 'jpg':
                continue
            image = cv2.imread(dataPath+ttv+'/'+user+'/'+extract+'/'+imagepath)
            faces = detector(image)
            l = len(faces)
            for face in faces:
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()
                roi = cv2.cvtColor(cv2.resize(image[y1:y2,x1:x2],(48,48)), cv2.COLOR_BGR2GRAY)
                frames.append(roi)
                labels.append(int(labels_data.loc[labels_data['ClipID'] == extract+'.avi', 'Engagement']))
            if l==0:
                frames.append(cv2.cvtColor(cv2.resize(image,(48,48)), cv2.COLOR_BGR2GRAY))
                labels.append(int(labels_data.loc[labels_data['ClipID'] == extract+'.avi', 'Engagement']))
        except:
            continue
    with open('output/'+extract+'_frames.pkl','wb') as f:
        pickle.dump(frames,f)
    with open('output/'+extract+'_labels.pkl','wb') as f:
        pickle.dump(labels,f)
    return 0
def currentTime(): #Current time in microseconds
    microseconds = time.time()/60
    return microseconds

if __name__ ==  '__main__':
    start=currentTime()
    dataPath = 'Data/'
    dataset = os.listdir(dataPath)
    global frames
    frames = []
    global labels
    labels = []
    threads = []
    tint = 1
    for ttv in dataset:
        users = os.listdir(dataPath+ttv+'/')
        for user in users:
            currUser = os.listdir(dataPath+ttv+'/'+user+'/')
            for extract in currUser:
                clip = os.listdir(dataPath+ttv+'/'+user+'/'+extract+'/')
                thread = multiprocessing.Process(target=thread_function, args=(dataPath, ttv, user, extract ,clip, tint))
                threads.append(thread)
                thread.start()
                tint+=1
    for thread in threads:
        thread.join()
    for file in os.listdir('output/'):
        if file[-10:] == 'frames.pkl':
            with open('output/'+file, 'rb') as f:
                frames=frames+pickle.load(f)
        elif file[-10:] == 'labels.pkl':
            with open('output/'+file, 'rb') as f:
                labels=labels+pickle.load(f)
    end=currentTime()
    print(f'Total time = {end-start}')
    print(len(labels))

