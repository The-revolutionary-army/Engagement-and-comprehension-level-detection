import os
import cv2
import pandas as pd
import pickle
import multiprocessing
import time
import csv
import shutil

outputDir='output\\'
openFaceDir='C:\\Users\\Omar\\OpenFace_2.2.0_win_x64\\FeatureExtraction.exe'
dataPath = 'C:\\Users\\Omar\\Data\\'
noOfProcesses=2 #Maximum number of parallel processes 

def thread_function(dataPath, ttv, user, extract, clip, ts):
    labels = []
    frames = []
    try:
        os.mkdir(f'{outputDir}{extract}')   # openface output dir
        os.system(f'{openFaceDir} -f "{dataPath}{ttv}\\{user}\\{extract}\\{extract}.avi" -out_dir {outputDir}{extract} -aus -simalign')
        # read labels from csv
        with open(f'{outputDir}{extract}\\{extract}.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            i = 1
            for row in readCSV:
                if(i==1):
                    i+=1
                    continue
                labels.append([int(float(x)) for x in row[22:]])
        # read frames images
        frames_img = os.listdir(f'{outputDir}{extract}\\{extract}_aligned')
        #print(frames_img)
        for frame_img in frames_img:
            image = cv2.imread(f'{outputDir}{extract}\\{extract}_aligned\\{frame_img}')
            #print(f'{outputDir}{extract}\\{extract}_aligned\\{frame_img}')
            frames.append(cv2.cvtColor(cv2.resize(image,(48,48)), cv2.COLOR_BGR2GRAY))
    except Exception as e:
        print(e)
    # after reading data, remove openface outputs to reduce size
    shutil.rmtree(f'{outputDir}{extract}')
        

    with open(f'{outputDir}{extract}_labels.pickle', 'wb') as f:
        pickle.dump(labels, f)
    with open(f'{outputDir}{extract}_frames.pickle', 'wb') as f:
        pickle.dump(frames, f)
    return 0

def currentTime(): #Current time in microseconds
    microseconds = time.time()/60
    return microseconds

if __name__ ==  '__main__':
    pool = multiprocessing.Pool(processes=noOfProcesses)
    start=currentTime()
    dataset = os.listdir(dataPath)
    frames = []
    labels = []
    tint = 1
    for ttv in dataset:
        users = os.listdir(dataPath+ttv+'\\')
        for user in users:
            currUser = os.listdir(dataPath+ttv+'\\'+user+'\\')
            for extract in currUser:
                clip = os.listdir(dataPath+ttv+'\\'+user+'\\'+extract+'\\')
                pool.apply_async(thread_function, args=(dataPath, ttv, user, extract ,clip, tint))
                tint+=1
    pool.close()
    pool.join()
    for file in os.listdir(outputDir):
        if file[-13:] == 'frames.pickle':
            with open(outputDir+file, 'rb') as f:
                frames=frames+pickle.load(f)
        elif file[-13:] == 'labels.pickle':
            with open(outputDir+file, 'rb') as f:
                labels=labels+pickle.load(f)
    end=currentTime()
    print(f'Total time = {end-start}')
    print(len(labels))