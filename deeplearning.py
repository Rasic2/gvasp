from keras.datasets import imdb
from keras import models
from keras import layers
from matplotlib import pyplot as plt
import numpy as np
from matplotlib import pyplot as plt

(train_data,train_labels),(test_data,test_labels)=imdb.load_data(num_words=10000)

def vectorize_sequences(sequences,dimension=10000):
	results=np.zeros((len(sequences),dimension))
	for i,sequence in enumerate(sequences):
		results[i,sequence]=1.
	return results

x_train=vectorize_sequences(train_data)
x_test=vectorize_sequences(test_data)
y_train=np.asarray(train_labels).astype('float32')
y_test=np.asarray(test_labels).astype('float32')

model=models.Sequential()
model.add(layers.Dense(16,activation='relu',input_shape=(10000,)))
model.add(layers.Dense(16,activation='relu'))
model.add(layers.Dense(1,activation='sigmoid'))

model.compile(optimizer='rmsprop',loss='binary_crossentropy',metrics=['accuracy'])
model.fit(x_train,y_train,epochs=4,batch_size=512)

results=model.evaluate(x_test,y_test)
print(results)
