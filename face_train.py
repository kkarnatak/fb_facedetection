import random

import numpy as np
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, UpSampling2D
from keras.optimizers import SGD, Adam
from keras.utils import np_utils
from keras.models import load_model
from keras import backend as K

from face_input_processing import extract_data, resize_with_pad, IMAGE_SIZE

################################################################################

class Dataset(object):

    def __init__(self):
        self.X_train = None
        self.X_valid = None
        self.X_test = None
        self.Y_train = None
        self.Y_valid = None
        self.Y_test = None

    # support only binary classification for now, thus 2 class limit
    def read(self, img_rows=IMAGE_SIZE, img_cols=IMAGE_SIZE, img_channels=3, nb_classes=2):

        images, labels = extract_data('./data/')
        labels = np.reshape(labels, [-1])

        X_train, X_test, y_train, y_test =  \
            train_test_split(images, labels, test_size=0.3, random_state=random.randint(0, 200))
        X_valid, X_test, y_valid, y_test = \
            train_test_split(images, labels, test_size=0.5, random_state=random.randint(0, 200))

        if K.image_dim_ordering() == 'th':
            X_train = X_train.reshape(X_train.shape[0], 3, img_rows, img_cols)
            X_valid = X_valid.reshape(X_valid.shape[0], 3, img_rows, img_cols)
            X_test = X_test.reshape(X_test.shape[0], 3, img_rows, img_cols)
            input_shape = (3, img_rows, img_cols)
        else:
            X_train = X_train.reshape(X_train.shape[0], img_rows, img_cols, 3)
            X_valid = X_valid.reshape(X_valid.shape[0], img_rows, img_cols, 3)
            X_test = X_test.reshape(X_test.shape[0], img_rows, img_cols, 3)
            input_shape = (img_rows, img_cols, 3)

        # the data, shuffled and split between train and test sets
        print('X_train shape:', X_train.shape)
        print(X_train.shape[0], 'train samples')
        print(X_valid.shape[0], 'valid samples')
        print(X_test.shape[0], 'test samples')

        # convert class vectors to binary class matrices
        Y_train = np_utils.to_categorical(y_train, nb_classes)
        Y_valid = np_utils.to_categorical(y_valid, nb_classes)
        Y_test = np_utils.to_categorical(y_test, nb_classes)

        X_train = X_train.astype('float32')
        X_valid = X_valid.astype('float32')
        X_test = X_test.astype('float32')
        X_train /= 255
        X_valid /= 255
        X_test /= 255

        self.X_train = X_train
        self.X_valid = X_valid
        self.X_test = X_test
        self.Y_train = Y_train
        self.Y_valid = Y_valid
        self.Y_test = Y_test

################################################################################

class Model(object):

    FILE_PATH = './store/model.h5'

    def __init__(self):
        self.model = None

    def build_model(self, dataset, nb_classes=2):
        self.model = Sequential()

        self.model.add(Conv2D(128, (3, 3), padding='same', input_shape=dataset.X_train.shape[1:]))
        self.model.add(Activation('relu'))
        self.model.add(Conv2D(128, (3, 3)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(64, (3, 3), padding='same'))
        self.model.add(Activation('relu'))
        self.model.add(Conv2D(64, (3, 3)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(32, (3, 3), padding='same'))
        self.model.add(Activation('relu'))
        self.model.add(Conv2D(32, (3, 3)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(UpSampling2D(size=(2, 2), data_format=None))

        self.model.add(Conv2D(64, (3, 3), padding='same'))
        self.model.add(Activation('relu'))
        self.model.add(Conv2D(64, (3, 3)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(32, (3, 3), padding='same'))
        self.model.add(Activation('relu'))
        self.model.add(Conv2D(32, (3, 3)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Flatten())
        self.model.add(Dense(512))
        self.model.add(Activation('relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(nb_classes))
        self.model.add(Activation('softmax'))

        self.model.summary()

    def custom_generator(src_dir, batch_size=128, N_classes=2, imsize=224):
        while True  :
            xs = []
            ys = []
            for _ in xrange(batch_size):
                imgName = np.random.choice(os.listdir(src_dir))
                img = cv2.imread(src_dir + imgName)
                img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_tensor = cv2.resize(img, (imsize, imsize)).transpose((2,0,1))
                img_class = int(imgName[:3])
                y = np.zeros((N_classes,))
                y[img_class] = 1
                xs.append(img_tensor)
                ys.append(y)
            yield(np.asarray(xs), np.asarray(ys))
            
    def generator(features, labels, batch_size):
        # Create empty arrays to contain batch of features and labels#
        batch_features = np.zeros((batch_size, 224, 224, 3))
        batch_labels = np.zeros((batch_size,1))
        while True:
            for i in range(batch_size):
                # choose random index in features
                index= random.choice(len(features),1)
                batch_features[i] = some_processing(features[index])
                batch_labels[i] = labels[index]
            yield batch_features, batch_labels

    
    def train(self, dataset, batch_size=16, nb_epoch=40, data_augmentation=True):
        #sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        # use ADAM optimizer as it gave slightly better results
        # TODO compare the same on big dataset

        adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer=adam,
                           metrics=['accuracy'])
        if not data_augmentation:
            print('Not using data augmentation.')
            self.model.fit(dataset.X_train, dataset.Y_train,
                           batch_size=batch_size,
                           nb_epoch=nb_epoch,
                           validation_data=(dataset.X_valid, dataset.Y_valid),
                           shuffle=True)
        else:
            print('Using real-time data augmentation.')

            # this will do preprocessing and realtime data augmentation
            datagen = ImageDataGenerator(
                featurewise_center=False,             # set input mean to 0 over the dataset
                samplewise_center=False,              # set each sample mean to 0
                featurewise_std_normalization=False,  # divide inputs by std of the dataset
                samplewise_std_normalization=False,   # divide each input by its std
                zca_whitening=False,                  # apply ZCA whitening
                rotation_range=20,                     # randomly rotate images in the range (degrees, 0 to 180)
                width_shift_range=0.2,                # randomly shift images horizontally (fraction of total width)
                height_shift_range=0.2,               # randomly shift images vertically (fraction of total height)
                horizontal_flip=True,                 # randomly flip images
                vertical_flip=False)                  # randomly flip images

            # compute quantities required for featurewise normalization
            # (std, mean, and principal components if ZCA whitening is applied)
            datagen.fit(dataset.X_train)

            # fit the model on the batches generated by datagen.flow()
            self.model.fit_generator(datagen.flow(dataset.X_train, dataset.Y_train,
                                                  batch_size=batch_size),
                                     samples_per_epoch=dataset.X_train.shape[0],
                                     nb_epoch=nb_epoch,
                                     validation_data=(dataset.X_valid, dataset.Y_valid))
            
            # upgrade it to new fit_generator
            #self.model.fit_generator(self.generator(features=dataset.X_train, 
            #             labels=dataset.Y_valid, batch_size=batch_size),
            #             samples_per_epoch=dataset.X_train.shape[0],
            #             nb_epoch=nb_epoch)


    def save(self, file_path=FILE_PATH):
        print('Model Saved.')
        self.model.save(file_path)

    def load(self, file_path=FILE_PATH):
        print('Model Loaded.')
        self.model = load_model(file_path)

    def predict(self, image):
        if K.image_dim_ordering() == 'th' and image.shape != (1, 3, IMAGE_SIZE, IMAGE_SIZE):
            image = resize_with_pad(image)
            image = image.reshape((1, 3, IMAGE_SIZE, IMAGE_SIZE))
        elif K.image_dim_ordering() == 'tf' and image.shape != (1, IMAGE_SIZE, IMAGE_SIZE, 3):
            image = resize_with_pad(image)
            image = image.reshape((1, IMAGE_SIZE, IMAGE_SIZE, 3))
        image = image.astype('float32')
        image /= 255
        result = self.model.predict_proba(image)
        print(result)
        result = self.model.predict_classes(image)

        return result[0]

    def evaluate(self, dataset):
        score = self.model.evaluate(dataset.X_test, dataset.Y_test, verbose=0)
        print("%s: %.2f%%" % (self.model.metrics_names[1], score[1] * 100))

################################################################################

if __name__ == '__main__':
    dataset = Dataset()
    dataset.read()

    model = Model()
    model.build_model(dataset)
    model.train(dataset, nb_epoch=20)
    model.save()

    model = Model()
    model.load()
    model.evaluate(dataset)