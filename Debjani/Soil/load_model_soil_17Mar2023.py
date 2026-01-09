# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 11:29:48 2018

@author: mohit123
"""
import numpy as np
from keras import applications
from keras.models import Sequential
from keras.layers import Convolution2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Input
from keras.models import Model
from keras import optimizers
import keras.utils as image
import sys
import os.path

'''
if os.path.isfile("/home/ggpi/Documents/Debjani/Soil/checkpython.txt"):
    f = open("/home/ggpi/Documents/Debjani/Soil/checkpython.txt", "a")
else:
    f = open("/home/ggpi/Documents/Debjani/Soil/checkpython.txt", "w")

f.write('Check Done')
f.close()
'''

np.random.seed(1337)
classifier = Sequential()

classifier.add(Convolution2D(32, (3, 3), input_shape = (256, 256, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2)))
classifier.add(Convolution2D(16, (3, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2)))
classifier.add(Convolution2D(8, (3, 3), activation = 'relu'))
classifier.add(MaxPooling2D(pool_size = (2, 2)))



classifier.add(Flatten())

#hidden layer
classifier.add(Dense(units = 128, activation = 'relu'))
classifier.add(Dropout(rate = 0.5))

#output layer
classifier.add(Dense(units = 5, activation = 'softmax'))

classifier.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])


'''
from keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

training_set = train_datagen.flow_from_directory(
        'train',
        target_size=(128, 128),
        batch_size=64,
        class_mode='categorical' )
label_map = (training_set.class_indices)

print(label_map)

itr = test_set = test_datagen.flow_from_directory(
        'testing/test1',
        target_size=(128, 128),
        batch_size=377,
        class_mode='categorical')

X, y = itr.next()
k = 0
'''
classifier.load_weights('keras_soil_trained_model_weights.h5')



img_path = sys.argv[1]
img = image.load_img(img_path, target_size=(256, 256))
img_tensor = image.img_to_array(img)
img_tensor = np.expand_dims(img_tensor, axis=0)
img_tensor /= 255.

#print(img_tensor.shape)


#for layer in classifier.layers:
#    g=layer.get_config()
#    h=layer.get_weights()
#    print (g)
#    print (h)

#scores = classifier.evaluate_generator(test_set,62/32)
arr = classifier.predict(img_tensor, batch_size=377, verbose=1)
res = np.argmax(arr, axis = -1)
#print(res)

if os.path.isfile("/home/pi/Documents/Debjani/Soil/Soil_Type.txt"):
    file = open("/home/pi/Documents/Debjani/Soil/Soil_Type.txt", "a")
else:
    file = open("/home/pi/Documents/Debjani/Soil/Soil_Type.txt", "w")


if(res == 0):
    file.write('Clay\n')
elif(res == 1):
    file.write('Loam\n')
elif(res == 2):
    file.write('Loamy_Sand\n')
elif(res == 3):
    file.write('Sand\n')
elif(res == 4):
    file.write('Sandy_Loam\n')

file.close()
