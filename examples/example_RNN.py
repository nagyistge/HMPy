#!/usr/bin/env python

# Luis Enrique Coronado Zuniga
# You are free to use, change, or redistribute the code in any way you wish
# but please maintain the name of the original author.
# This code comes with no warranty of any kind.


#%%
from numpy import*
from nep_gauss import*
from nep_segment import*
import timeit

dir_path = os.getcwd()
print dir_path

#Configuration of the models
create_models = False
features = False

#Define the name of the gesture
name_model1 = "arriba"
name_model2 = "izquierda"
name_model3 = "derecha"

#Define the path to save the models
path_to_save = dir_path + "/data_examples/Gaussian_Models/"

#Define the path of the gesture folders
path_to_load = dir_path + "/data_examples/wereable_acc_models_aligned/"

#Define id (name) of the files in the datatest, example <acc(1)>.txt, example <acc(2)>.txt , ....
files_id = "acc"
#threashlod
th = 400
#Crate a new model
create_models = True

#Define the number of training examples
training_examples1 = 10
training_examples2 = 10
training_examples3 = 10

gest1 = GestureModel(name_model1,path_to_load,path_to_save,training_examples1)
gest2 = GestureModel(name_model2,path_to_load,path_to_save,training_examples2)
gest3 = GestureModel(name_model3,path_to_load,path_to_save,training_examples3)

#Create a list of models
list_models = [gest1,gest2,gest3]

value = equal_inputs(list_models, "min")
print value*3

if(create_models == True):
    gest1.buildModel("DNN", "3IMU_acc", features, value=value)
    gest2.buildModel("DNN", "3IMU_acc", features, value=value)
    gest3.buildModel("DNN", "3IMU_acc", features, value=value)
    
#Update list of models
list_models = [gest1,gest2,gest3]

# Import libraries
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout, Embedding, LSTM, Bidirectional
import timeit
print "Libraries loaded"


dnn_dataset = concatenate((list_models[0].dnn_dataset,list_models[1].dnn_dataset), axis=0)
i = 2
n = size(list_models)

while(i < n):
    dnn_dataset = concatenate((dnn_dataset,list_models[i].dnn_dataset), axis=0)
    i = i + 1
X = dnn_dataset

#Outputs
n_classes = size(list_models)
Y = set_outputs(n_classes,training_examples1)

print Y

n_examples, n_inputs = shape(X)
print shape(X)
print shape(Y)

seed = 7
random.seed(seed)
print "Data loaded"

max_features = 1000
maxlen = 500
model = Sequential()
model.add(Embedding(max_features, 128, input_length=maxlen))
model.add(Bidirectional(LSTM(64)))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))

# try using different optimizers and different optimizer configs
model.compile('adam', 'binary_crossentropy', metrics=['accuracy'])

print "Model compiled"

# nb_epoch = iterations
# batch_size =  instances that are evaluated before a weight update in the network is performed

# Fit the net
#verbose=0 to avoid error in jypiter, ipython

model.fit(X, Y, nb_epoch=100, batch_size=3, verbose=0)
toc=timeit.default_timer()
tm = toc -tic

print "Fit complete in" , toc - tic , "seconds"


#%%

tic=timeit.default_timer()
print "Evaluation"
scores = model.evaluate(X, Y)
print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))

predictions = model.predict(X)
# round predictions
for x in predictions:
    print(round(x[0]),round(x[1]),round(x[2]) )
toc=timeit.default_timer()

tm = toc -tic
print tm

#%%
# Save the model
from keras.models import model_from_json

# serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk")


# load json and create model
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded model from disk")

#%%
 
# evaluate loaded model on test data
loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
score = loaded_model.evaluate(X, Y, verbose=0)

predictions = loaded_model.predict(X)
# round predictions
for x in predictions:
    print(round(x[0]),round(x[1]),round(x[2]) )
toc=timeit.default_timer()

print tm
