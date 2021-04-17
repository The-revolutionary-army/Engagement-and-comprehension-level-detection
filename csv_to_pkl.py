import os
import csv
import pickle

with open('/home/ahmed/Downloads/Telegram Desktop/csvFile.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    acu = []
    i = 1
    for row in readCSV:
        print (row[0:3])
        acu.append(row[0:3])
        i += 1
        if i == 5: break
    
    print acu
    pickle_out = open('acu.pickle', 'wb')
    pickle.dump(acu, pickle_out)
    pickle_out.close()