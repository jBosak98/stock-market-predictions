# -*- coding: utf-8 -*-
"""Copy of regresion-prediction_stock_prices.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/193LDXhDAtIF6yD59ekIJJdMqoBpDmJ-T

#Read in data
"""
import sys
import csv
import scipy
import numpy
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential, layers, callbacks
from tensorflow.keras.layers import Dense, LSTM, Dropout, GRU, Bidirectional
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
from IPython.core.pylabtools import figsize
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import seaborn as sns

# check if there is a file in args
if len(sys.argv) <= 1:
    exit("Too less arguments calling script")


#Read in data
dataset = pd.read_csv(sys.argv[1], header = 0)
print('the total numbers of rows from a CSV file: ' + str(len(dataset)))

#Drop Nan columns
dataset = dataset.dropna()
print(dataset.head)
print(dataset.dtypes)
print('Before: ' + str(len(dataset)))

# convert , to normal number

"""Clean file"""

import pandas as pd

dataset = dataset.replace(",", "", regex=True)
dataset = dataset.rename(columns = {'Data': 'Date'} )
# check format
print(dataset.dtypes)
# Change formay
dataset["Date"]= pd.to_datetime(dataset["Date"])
dataset['High'] = dataset['High'].astype('float32')
dataset['Open'] = dataset['Open'].astype('float32')
dataset['Low'] = dataset['Low'].astype('float32')
dataset['Close'] = dataset['Close'].astype('float32')
dataset['Volume'] = dataset['Volume'].astype('float32')
# check format
print(dataset.dtypes)
# sort old -> young
# dataset.sort_values(by='Date', inplace=True)
# Double check the result
dataset.head()
print(dataset)

import matplotlib.pyplot as plt

plt.figure(figsize = (18,9))
plt.plot(range(dataset.shape[0]),(dataset['Low'] + dataset['High'])/2.0)
plt.xticks(range(0,dataset.shape[0],500),dataset['Date'].loc[::500],rotation=45)
plt.xlabel('Date',fontsize=18)
plt.ylabel('Mid Price',fontsize=18)
plt.show()

train_size = int(len(dataset)*0.7)
train_dataset, test_dataset = dataset.iloc[:train_size], dataset.iloc[train_size:]

print('Dimension of train data: ',train_dataset.shape)
print('Dimension of test data: ', test_dataset.shape)

# Plot train and test data
plt.figure(figsize = (18,9))
plt.plot(train_dataset.Low, label = "Train")
plt.plot(test_dataset.Low, label = "Test")
# plt.xlabel('Time (day)')
# plt.ylabel('Daily water consumption ($m^3$/capita.day)')
plt.legend(['Train set', 'Test set'], loc='upper right')
#plt.savefig('C:/Users/nious/Documents/Medium/LSTM&GRU/2.jpg', format='jpg', dpi=1000)
plt.title('High Values in Train and Test Dataset')
plt.show()

# Split train data to X and y
X_train = train_dataset.drop(['Close','Date'], axis = 1)
print(X_train.shape)
y_train = train_dataset.loc[:,['Close']].to_numpy()
print(y_train.shape)
# Split test data to X and y
X_test = test_dataset.drop(['Close','Date'], axis = 1)
print(X_test.shape)
y_test = test_dataset.loc[:,['Close']].to_numpy()
print(y_test.shape)

train_size = int(len(X_test)*0.9)
x_dataset = X_test.iloc[train_size:]
print(x_dataset.shape)
print(train_size)
y_train_size = int(len(y_test)*0.9)
y_dataset = test_dataset.loc[:,['Close']].iloc[y_train_size:]

print(y_dataset.shape)

# Different scaler for input and output
scaler_x = MinMaxScaler(feature_range = (0,1))
scaler_y = MinMaxScaler(feature_range = (0,1))

# Fit the scaler using available training data
input_scaler = scaler_x.fit(X_train)
output_scaler = scaler_y.fit(y_train)

# Apply the scaler to training data
train_y_norm = output_scaler.transform(y_train)
train_x_norm = input_scaler.transform(X_train)

# Apply the scaler to test data
test_y_norm = output_scaler.transform(y_test)
test_x_norm = input_scaler.transform(X_test)

# Create a 3D input
def create_dataset (X, y, time_steps = 1):
    Xs, ys = [], []
    for i in range(len(X)-time_steps):
        v = X[i:i+time_steps, :]
        Xs.append(v)
        ys.append(y[i+time_steps])
    return np.array(Xs), np.array(ys)
TIME_STEPS = 30
X_test, y_test = create_dataset(test_x_norm, test_y_norm,   
                                TIME_STEPS)
X_train, y_train = create_dataset(train_x_norm, train_y_norm, 
                                  TIME_STEPS)
print('X_train.shape: ', X_test.shape)
print('y_train.shape: ', y_train.shape)
print('X_test.shape: ', X_test.shape)
print('y_test.shape: ', y_train.shape)

# Create LSTM
def create_model(units, m):
    model = Sequential()
    model.add(m (units = units, return_sequences = True,
                input_shape = [X_train.shape[1], X_train.shape[2]]))
    model.add(Dropout(0.2))
    model.add(m (units = units))
    model.add(Dropout(0.2))
    model.add(Dense(units = 1))
    #Compile model
    model.compile(loss='mse', optimizer='adamax', metrics= 'accuracy')
    return model

def create_model_bilstm(units):
    model = Sequential()
    model.add(Bidirectional(LSTM(units = units,                             
              return_sequences=True),
              input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Bidirectional(LSTM(units = units)))
    model.add(Dense(1))
    #Compile model
    model.compile(loss='mse', optimizer='adam',  metrics= 'accuracy')
    return model

model_lstm = create_model(128, LSTM)
# model_bilstm = create_model_bilstm(128)
# model_gru = create_model(64, GRU)

# Fit LSTM
def fit_model(model):
    early_stop = keras.callbacks.EarlyStopping(monitor = 'val_loss',
                                              patience = 50)
    
    history = model.fit(X_train, y_train, 
                        epochs = 10,  
                        validation_split = 0.2, # validation_data = (test_X, test_y)
                        batch_size = 128,  
                        verbose = 2,
                        shuffle = False,
                        callbacks = [early_stop])
    return history

#the best batch_size = 128, units = 128, 128, 1, optimizer='adamax'

history_lstm = fit_model(model_lstm)
# history_bilstm = fit_model(model_bilstm)
# history_gru = fit_model(model_gru)
model_lstm.save("my_model")