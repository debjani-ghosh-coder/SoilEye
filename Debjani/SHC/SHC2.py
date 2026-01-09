

import pandas as pd
import argparse
import csv
import os
import sys
import time
from io import BytesIO
from xhtml2pdf import pisa
from string import Template as HTMLTemplate

# Set MPLCONFIGDIR to a writable directory
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

parser = argparse.ArgumentParser()
parser.add_argument("csv_file1", help="Path to farmer_details.csv")
parser.add_argument("csv_file2", help="Path to testing.csv")
parser.add_argument("soil_image", help="Path to soil image")
parser.add_argument("pdf_filename", help="Name for the generated PDF")
args = parser.parse_args()

# Assign variables
csv_file1 = args.csv_file1
csv_file2 = args.csv_file2
soil_image = args.soil_image
pdf_filename = args.pdf_filename

with open(args.csv_file1, newline='') as csvfile1:
    ssd = pd.read_csv(csvfile1,header=None, delimiter=',', on_bad_lines='skip', encoding='utf-8')

ssd.columns=['Name','Email Id','Address','Geo Position (GPS)','Date of Sample Collection','Survey No., Khasra No,/ Dag No,','Farm Size']

#irr=['Irrigated (Bore well)','Non-Irrigated','Irrigated (Pipeline)','Irrigated (Drip Irrigation)','Non-Irrigated']

#ssd['Irrigation Status']=irr

#Basic details
ssd1=ssd[['Name', 'Email Id', 'Address']]
#Farm details
ssd2=ssd[['Date of Sample Collection', 'Survey No., Khasra No,/ Dag No,',
       'Farm Size','Geo Position (GPS)']]

SSD1=ssd1.T
SSD2=ssd2.T

Lst=[]
f='Farmer'
for i in range(len(ssd)):
    I=str(i+1)
    F=f+I
    Lst.append(F)
print(Lst)

SSD1.columns=Lst
SSD2.columns=Lst

Personal_Info=[]
Farm_Info=[]

for i in range(len(ssd)):
    x=SSD1[[Lst[i]]]
    x = x.style.set_caption('Farmer Details')
    Personal_Info.append(x)

    y=SSD2[[Lst[i]]]
    y=y.style.set_caption('Farm Details')
    Farm_Info.append(y)

with open(args.csv_file2, newline='', encoding='us-ascii', errors='replace') as csvfile2:
    details = csv.reader(csvfile2)
    l = []
    for row in details:
        l.extend(row)
        
lst=[float(x) for x in l]

#Changing units
#N
lst[2]=1.35*10*lst[2]
#P
lst[3]=1.35*10*lst[3]
#K
lst[4]=1.35*10*lst[4]
#EC
lst[6]=0.1*lst[6]


input=pd.DataFrame(columns=['Temperature', 'Moisture', 'Nitrogen', 'Phosphorous', 'Potassium',
       'pH', 'Electric Conductivity'])
input.loc[0]=lst

input['Salinity']=input['Electric Conductivity']

input=input[['Nitrogen', 'Phosphorous', 'Potassium',
       'pH', 'Electric Conductivity','Salinity','Temperature', 'Moisture']]



parameters=input.columns

inputs=input.iloc[0:1,:]

SHC=input.melt( 
        var_name="Parameter", 
        value_name="Test value")

# # Ideal Range
# # Tempertaure=> 20-30
# # Moisture=> (Paddy, Sugarcane=> 80-85), (Cotton, Maize=> 50-60)=> 50-75%
# # N=> 280-560
# # P=> 11-26
# # K=> 120-280
# # pH=> >7, =7, <7
# # Electrical Conductivity=> 0-2 dS/m

std=['280-560','11-26','120-280','7, Neutral','0-2','2-4','20-30','50-75']

unit=['Kg/Ha','Kg/Ha','Kg/Ha','H Potenz','dS/m','dS/m','°C','%']

SHC['Unit']=unit

SHC['Rating']=''

# # N
if (SHC['Test value'][0]<280):
    SHC.loc[0, 'Rating']='Low'
elif(SHC['Test value'][0]>=280 and SHC['Test value'][0]<=560):
    SHC.loc[0, 'Rating']='Medium'
elif(SHC['Test value'][0]>560):
    SHC.loc[0, 'Rating']='High'

# P
if (SHC['Test value'][1]<11):
    SHC.loc[1, 'Rating']='Low'
elif(SHC['Test value'][1]>=11 and SHC['Test value'][1]<=26):
    SHC.loc[1, 'Rating']='Medium'
elif(SHC['Test value'][1]>26):
    SHC.loc[1, 'Rating']='High'

# K
if (SHC['Test value'][2]<120):
    SHC.loc[2, 'Rating']='Low'
elif(SHC['Test value'][2]>=120 and SHC['Test value'][2]<=280):
    SHC.loc[2, 'Rating']='Medium'
elif(SHC['Test value'][2]>280):
    SHC.loc[2, 'Rating']='High'

# pH
if (SHC['Test value'][3]<6):
    SHC.loc[3, 'Rating']='Acidic'
elif(SHC['Test value'][3]>=6 and SHC['Test value'][3]<7):
    SHC.loc[3, 'Rating']='Slightly Acidic'
elif(SHC['Test value'][3]==7):
    SHC.loc[3, 'Rating']='Neutral'
elif(SHC['Test value'][3]>7 and SHC['Test value'][3]<=8):
    SHC.loc[3, 'Rating']='Slightly Basic'
elif(SHC['Test value'][3]>8):
    SHC.loc[3, 'Rating']='Basic'

# EC
if (SHC['Test value'][4]<0):
    SHC.loc[4, 'Rating']='Low'
elif(SHC['Test value'][4]>=0 and SHC['Test value'][4]<=2):
    SHC.loc[4, 'Rating']='Normal'
elif(SHC['Test value'][4]>2):
    SHC.loc[4, 'Rating']='High'

# Salinity
if (SHC['Test value'][5]<2):
    SHC.loc[5, 'Rating']='Low'
elif(SHC['Test value'][5]>=2 and SHC['Test value'][5]<=4):
    SHC.loc[5, 'Rating']='Normal'
elif(SHC['Test value'][5]>4):
    SHC.loc[5, 'Rating']='High'

# Temperature
if (SHC['Test value'][6]<20):
    SHC.loc[6, 'Rating']='Cool'
elif(SHC['Test value'][6]>=20 and SHC['Test value'][6]<=30):
    SHC.loc[6, 'Rating']='Ideal'
elif(SHC['Test value'][6]>30):
    SHC.loc[6, 'Rating']='Hot'

# Moisture
if (SHC['Test value'][7]<50):
    SHC.loc[7, 'Rating']='Low'
elif(SHC['Test value'][7]>=50 and SHC['Test value'][7]<=75):
    SHC.loc[7, 'Rating']='Medium'
elif(SHC['Test value'][7]>75):
    SHC.loc[7, 'Rating']='High'

SHC['Normal Level']=std

print("Soil Health Card")
print(SHC)

def color_rating(val):
    if val == 'Low':
        color = 'yellow'
    elif val == 'High':
        color = 'red'
    elif val == 'Neutral':
        color = 'grey'
    elif val == 'Ideal':
        color = 'green'
    elif val == 'Normal':
        color = 'orange'
    elif 'Acidic' in val:
        color = 'red'
    elif 'Basic' in val:
        color = 'yellow'
    else:
        color = 'black'
    return 'background-color: %s' % color

# apply the function to the 'Rating' column and export the styled DataFrame as an HTML file
SHC_c =SHC.style.applymap(color_rating, subset=['Rating'])
# styled_df.to_file('styled_dataframe.html', render_links=True)


import warnings

# suppress the UserWarnings
warnings.filterwarnings("ignore", message="X does not have valid feature names, but MinMaxScaler was fitted with feature names")
warnings.filterwarnings("ignore", message="X has feature names, but RandomForestClassifier was fitted without feature names")

# Crop Prediction

crop=pd.read_csv('/home/pi/Documents/Debjani/SHC/CropData.csv')

crop=crop[['N', 'P', 'K', 'temperature', 'humidity', 'ph',
       'rainfall', 'Sand%', 'Clay%', 'Silt%', 'label']]

crop=crop[['N', 'P', 'K', 'temperature', 'ph', 'rainfall','label']]

# Changing rainfall to Moisture
crop.rename(columns = {'rainfall':'Moisture','N':'Nitrogen','P':'Phosphorous','K':'Potassium','ph':'pH','temperature':'Temperature'}, inplace = True)

X=crop[['Temperature','Moisture','Nitrogen', 'Phosphorous', 'Potassium','pH']]
Y=crop['label']

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

# print("The accuracy of the model in crop prediction is ")
# print(acc_crop*100)

import chardet

with open(args.csv_file2, newline='') as csvfile2:
    input_crop=pd.read_csv(csvfile2,header=None)

input_crop.columns=['Temperature', 'Moisture', 'Nitrogen', 'Phosphorous','Potassium', 'pH', 'ElectricalConductivity']
input_crop=input_crop[['Temperature', 'Moisture', 'Nitrogen', 'Phosphorous','Potassium', 'pH']]

X_exp_crop=input_crop.loc[0]
# X_exp_crop=X_exp_crop.values
X_exp_crop=[X_exp_crop]

X_exp_crop_sc=mms.transform(X_exp_crop)
predict_crop=rfc.predict(input_crop)

# Fertilizer Prediction
ferti=pd.read_csv("/home/pi/Documents/Debjani/SHC/FertilizerData.csv")

# Removing 'Humidity' and 'Soil Type' column
ferti=ferti[['Temperature', 'Moisture',
       'Crop Type', 'Nitrogen', 'Phosphorous', 'Potassium', 'Fertilizer Name']]

from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
ferti['Crop Type']=le.fit_transform(ferti['Crop Type'])

x = ferti[['Temperature', 'Moisture', 'Crop Type', 'Nitrogen', 'Phosphorous',
       'Potassium']]
y = ferti['Fertilizer Name']

x_train, x_test, y_train, y_test=train_test_split(x,y,test_size=0.1)



x_train_sc= mms.fit_transform(x_train)

x_test_sc = mms.transform(x_test)

rfc = RandomForestClassifier(max_depth=14,n_estimators=1000)


rfc.fit(x_train_sc,y_train)
rfc.predict(x_test_sc)

from sklearn.metrics import accuracy_score
acc_ferti=accuracy_score(rfc.predict(x_test_sc),y_test)

# print("The accuracy of the model in fertilizer prediction is ")
# print(acc_ferti*100)



# Taking Random input and crop name for Fertilizer prediction
user_crop=['Sugarcane', 'Millets', 'Cotton', 'Paddy', 'Wheat', 'Oil seeds', 'Ground Nuts', 'Pulses', 'Barley', 'Tobacco', 'Maize']

user_crop=le.transform(user_crop)

import random as rd

with open(args.csv_file2, newline='') as csvfile2:
    input_ferti = csv.reader(csvfile2)
    a = []
    for row in input_ferti:
        a.extend(row)
    del a[5:7]

    a.append(user_crop[rd.randint(0,len(user_crop)-1)])

    a=[a]

x_exp_ferti=a
# Scaling 
x_exp_ferti_sc=mms.transform(x_exp_ferti)

#Fertilizer Prediction for random input
predict_ferti=rfc.predict(x_exp_ferti_sc)

# Soil Type detection
import numpy as np
from keras import applications
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Input
from keras.models import Model
from keras import optimizers
import keras.utils as image
import sys

np.random.seed(1337)
input_layer = Input(shape=(256, 256, 3))
x = Conv2D(32, (3, 3), activation='relu')(input_layer)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Conv2D(16, (3, 3), activation='relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Conv2D(8, (3, 3), activation='relu')(x)
x = MaxPooling2D(pool_size=(2, 2))(x)
x = Flatten()(x)
x = Dense(units=128, activation='relu')(x)
x = Dropout(rate=0.5)(x)
output_layer = Dense(units=5, activation='softmax')(x)

classifier = Model(inputs=input_layer, outputs=output_layer)

classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

classifier.load_weights('/home/pi/Documents/Debjani/SHC/TrainedModelWeights.h5')


# with open(args.csv_file1, newline='') as csvfile1:
#     ssd = pd.read_csv(csvfile1,header=None)

img_path = sys.argv[3]
img = image.load_img(img_path, target_size=(256, 256))
img_tensor = image.img_to_array(img)
img_tensor = np.expand_dims(img_tensor, axis=0)
img_tensor /= 255.

print(img_tensor.shape)

arr = classifier.predict(img_tensor, batch_size=377, verbose=1)
res = np.argmax(arr, axis = -1)
soil_type=[]
if(res == 0):
    soil_type.append('Clay')
elif(res == 1): 
    soil_type.append('Loam')
elif(res == 2): 
    soil_type.append('Loamy_Sand')
elif(res == 3): 
    soil_type.append('Sand')
elif(res == 4): 
    soil_type.append('Sandy_Loam')

soil_type=soil_type[0]
predict_crop=predict_crop[0]
predict_ferti=predict_ferti[0]

predict_cf=pd.DataFrame(columns=['Type','Prediction'])

predict_cf['Type']=['Soil Type','Crop predicted','Fertilizer predicted']
predict_cf['Prediction']=[soil_type,predict_crop,predict_ferti]

#print(predict_cf)

n=len(ssd)-1
#print("The Farmer Survey number taken is (Last Survey No.)",n+1)

from io import StringIO, BytesIO
from xhtml2pdf import pisa
from string import Template as HTMLTemplate

# Convert dataframes to HTML
html1 = Personal_Info[n].to_html()
html2 = Farm_Info[n].to_html()
html3=predict_cf.to_html()
html4 = SHC_c.to_html()


# Create HTML template
html_template = HTMLTemplate('''
   <html>
     <head>
       <style>
         table, th, td {
           border: 1px solid black;
           border-collapse: collapse;
           padding: 5px;
         }
       </style>
     </head>
     <body>
       <h1>Farmer Information</h1>
       $html1
       $html2
       <h1>Soil Health Card</h1>
       $html3
       $html4
     </body>
   </html>
''')
template = '''
<html>
  <head>
    <style>
      table, th, td {{
        border-collapse: collapse;
        padding: 5px;
      }}
    </style>
  </head>
  <body>
    <h1>Farmer Information</h1>
    {html1}
    {html2}
    <h1>Soil Health Card</h1>
    {html3}
    {html4}
  </body>
</html>
'''

# Replace the placeholders with the actual HTML tables
html_content = template.format(html1=html1, html2=html2, html3=html3, html4=html4)
# Convert HTML to PDF
pdf = BytesIO()
pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), pdf)
# Save PDF to Apache's served directory with the provided filename
file_path = "/var/www/html/" + pdf_filename
with open(file_path, 'wb') as f:
    f.write(pdf.getvalue())
# Write the HTML content to a file
with open('/home/pi/Documents/Debjani/SHC/generated.html', 'w') as f:
    f.write(html_content)


# Merge HTML content
#html = html_template.substitute(html1=html1, html2=html2, html3=html3, html4=html4)

# Convert HTML to PDF
#pdf = BytesIO()
#pisa.CreatePDF(BytesIO(html.encode('utf-8')), pdf)

#destination_folder = "/home/pi/Documents/Debjani/SHC/"
#file_name = "SoilHealthCard.pdf"
#file_path = destination_folder + file_name

# Save PDF to file
#with open(file_path, 'wb') as f:
 #   f.write(pdf.getvalue())
# At the end of SHC.py after PDF generation
print(f"PDF generated successfully: {pdf_filename}")

soil_type_file = os.path.expanduser("/home/pi/Documents/Debjani/Soil/Soil_Type.txt")
crop_file = os.path.expanduser("/home/pi/Documents/Debjani/Soil/crop.txt")
fertilizer_file = os.path.expanduser("/home/pi/Documents/Debjani/Soil/fertilizer.txt")

# Ensure directories exist
os.makedirs(os.path.dirname(soil_type_file), exist_ok=True)
os.makedirs(os.path.dirname(crop_file), exist_ok=True)

# Write predictions to respective files
with open(soil_type_file, 'w') as f:
    f.write(predict_cf.loc[predict_cf['Type'] == 'Soil Type', 'Prediction'].iloc[0])

with open(crop_file, 'w') as f:
    f.write(predict_cf.loc[predict_cf['Type'] == 'Crop predicted', 'Prediction'].iloc[0])

with open(fertilizer_file, 'w') as f:
    f.write(predict_cf.loc[predict_cf['Type'] == 'Fertilizer predicted', 'Prediction'].iloc[0])

print("Predictions successfully written to text files.")
