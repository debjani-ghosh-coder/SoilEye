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




# Fertilizer Recommendation
ferti=pd.read_csv("FertilizerData.csv")

# Removing 'Humidity' and 'Soil Type' column
ferti=ferti[['Temperature', 'Moisture',
       'Crop Type', 'Nitrogen', 'Phosphorous', 'Potassium', 'Fertilizer Name']]

from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
ferti['Crop Type']=le.fit_transform(ferti['Crop Type'])

x = ferti[['Temperature', 'Moisture', 'Crop Type', 'Nitrogen', 'Phosphorous',
       'Potassium']]
y = ferti['Fertilizer Name']

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test=train_test_split(x,y,test_size=0.1)

from sklearn.preprocessing import MinMaxScaler

mms = MinMaxScaler()
x_train_sc= mms.fit_transform(x_train)

x_test_sc = mms.transform(x_test)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(max_depth=14,n_estimators=1000)


rfc.fit(x_train_sc,y_train)
rfc.predict(x_test_sc)

from sklearn.metrics import accuracy_score
acc_ferti=accuracy_score(rfc.predict(x_test_sc),y_test)
print("The accuracy of the model in fertilizer prediction is ")
print(acc_ferti*100)

# Removing pH column
sensor=sensor[['Temperature', 'Moisture','Nitrogen', 'Phosphorous', 'Potassium']]

# Taking Random input and crop name for Fertilizer prediction
user_crop=['Sugarcane', 'Millets', 'Cotton', 'Paddy', 'Wheat', 'Oil seeds', 'Ground Nuts', 'Pulses', 'Barley', 'Tobacco', 'Maize']

user_crop=le.transform(user_crop)

# input=pd.read_csv('input.csv',header=None)
# input.columns=['Temperature', 'Moisture', 'Nitrogen', 'Phosphorous', 'Potassium',
#        'pH', 'Electric Conductivity']


import argparse
import csv
import random as rd


parser = argparse.ArgumentParser()
parser.add_argument("csv_file", help="")
args = parser.parse_args()

with open(args.csv_file, newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    l1 = []
    l2 = []
    for row in csv_reader:
        l2.extend(row)
    del l2[5:7]

    l2.append(user_crop[rd.randint(0,len(user_crop))])

    l1.append(l2)

x_exp=l1


# Scaling 
input_ferti=mms.transform(x_exp)

#Fertilizer Prediction for random input
predict_ferti=rfc.predict(input_ferti)

file = open("/home/pi/Documents/Debjani/CropFertilizerPrediction/fertilizer.txt","a")
file.write(predict_ferti[0])
file.write("\n")
file.close()
