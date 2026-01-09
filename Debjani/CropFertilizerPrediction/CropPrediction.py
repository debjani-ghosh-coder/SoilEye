import chardet
import pandas as pd

with open('SensorData.csv', 'rb') as f:
    result = chardet.detect(f.read())  # or readline if the file is large

sensor=pd.read_csv('SensorData.csv', encoding=result['encoding'])

sensor=sensor[['Temperature', 'Moisture', 'Nitrogen', 'Phosphorous',
       'Potassium', 'pH', 'ElectricalConductivity']]

sensor = sensor.dropna(how='any',axis=0)
sensor.reset_index(inplace=True, drop=True)

lst=[]
for i in range(len(sensor)):
    lst.append(float(sensor['Temperature'][i]))

lst1=[]
for i in range(len(sensor)):
    lst1.append(sensor['Moisture'][i])

lst2=[]
for i in range(len(sensor)):
    lst2.append(sensor['pH'][i])

lst3=[]
for i in range(len(sensor)):
    lst3.append(sensor['ElectricalConductivity'][i])

for i in range(len(lst)):
    if (lst[i]>80 or lst[i]<-40 or lst1[i]<0 or lst1[i]>100 or lst2[i]>9):
        sensor= sensor.drop(index=i)

sensor.reset_index(inplace=True, drop=True)

# Crop Prediction
crop=pd.read_csv('CropData.csv')

crop=crop[['N', 'P', 'K', 'temperature', 'humidity', 'ph',
       'rainfall', 'Sand%', 'Clay%', 'Silt%', 'label']]

crop=crop[['N', 'P', 'K', 'temperature', 'ph', 'rainfall','label']]

# Changing rainfall to Moisture
crop.rename(columns = {'rainfall':'Moisture','N':'Nitrogen','P':'Phosphorous','K':'Potassium','ph':'pH','temperature':'Temperature'}, inplace = True)

X=crop[['Temperature','Moisture','Nitrogen', 'Phosphorous', 'Potassium','pH']]
Y=crop['label']

sensor=sensor[['Temperature','Moisture','Nitrogen', 'Phosphorous', 'Potassium','pH']]

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test=train_test_split(X,Y,test_size=0.2)

from sklearn.preprocessing import MinMaxScaler
mms = MinMaxScaler()
X_train_sc= mms.fit_transform(X_train)

X_test_sc = mms.transform(X_test)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(max_depth=14,n_estimators=1000)
rfc.fit(X_train_sc, Y_train)

from sklearn.metrics import accuracy_score
acc_crop=accuracy_score(rfc.predict(X_test_sc),Y_test)
print("The accuracy of the model in crop prediction is ")
print(acc_crop*100)

import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument("csv_file", help="")
args = parser.parse_args()

with open(args.csv_file, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    l1 = []
    l2 = []
    for row in csv_reader:
        l2.extend(row)

    l2=l2[0:6]
    l1.append(l2)

# input=pd.read_csv('input.csv',header=None)
# input.columns=['Temperature', 'Moisture', 'Nitrogen', 'Phosphorous', 'Potassium',
#        'pH', 'Electric Conductivity']

X_exp=l1

input_crop=mms.transform(X_exp)

predict_crop=rfc.predict(input_crop)

file = open("/home/pi/Documents/Debjani/CropFertilizerPrediction/crop.txt","a")
file.write(predict_crop[0])
file.write("\n")
file.close()

#Crop Prediction
# for i in range(5):
#     print("The crop for the following condition: ")
#     print(X_exp.iloc[i])
#     print("=>>", end=" ")
#     print(predict_crop[i])
#     print('\n')

# sensor_crop=sensor.copy()

# sensor_crop['crop']=predict_crop

# print(sensor_crop)
