import os
import cv2
import pandas as pd
import pickle
import multiprocessing
import time
import csv
import shutil

def thread_function(dataPath, ttv, user, extract, clip, ts):
    labels = []
    frames = []
    try:
        os.mkdir(f'output/{extract}')   # openface output dir
        os.system(f'/home/mohamed/OpenFace/build/bin/FeatureExtraction -f "{dataPath}{ttv}/{user}/{extract}/{extract}.avi" -out_dir output/{extract} -aus -simalign')
        # read labels from csv
        with open(f'output/{extract}/{extract}.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            i = 1
            for row in readCSV:
                if(i==1):
                    i+=1
                    continue
                labels.append([int(float(x)) for x in row[22:]])
        # read frames images
        frames_img = os.listdir(f'output/{extract}/{extract}_aligned')
        print(frames_img)
        for frame_img in frames_img:
            image = cv2.imread(f'output/{extract}/{extract}_aligned/{frame_img}')
            print(f'output/{extract}/{extract}_aligned/{frame_img}')
            frames.append(cv2.cvtColor(cv2.resize(image,(48,48)), cv2.COLOR_BGR2GRAY))
    except Exception as e:
        print(e)
    # after reading data, remove openface outputs to reduce size
    shutil.rmtree(f'output/{extract}')
        

    with open(f'output/{extract}_labels.pickle', 'wb') as f:
        pickle.dump(labels, f)
    with open(f'output/{extract}_frames.pickle', 'wb') as f:
        pickle.dump(frames, f)
    return 0

def currentTime(): #Current time in microseconds
    microseconds = time.time()/60
    return microseconds

if __name__ ==  '__main__':
    start=currentTime()
    dataPath = '/home/mohamed/Downloads/Telegram Desktop/Data/'
    dataset = os.listdir(dataPath)
    threads = []
    frames = []
    labels = []
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
        if file[-13:] == 'frames.pickle':
            with open('output/'+file, 'rb') as f:
                frames=frames+pickle.load(f)
        elif file[-13:] == 'labels.pickle':
            with open('output/'+file, 'rb') as f:
                labels=labels+pickle.load(f)
    end=currentTime()
    print(f'Total time = {end-start}')
    print(len(labels))



