from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, Reshape, Conv2D, BatchNormalization, MaxPooling2D


def define_model():
    """
    Defines the CNN model
    :return:
    """

    model = Sequential()
    model.add(Reshape((64, 64, 3), input_shape=(1, 64, 64, 3)))

    # Conv Block 1
    model.add(Conv2D(16, (5, 5), name='conv_layer_1', strides=2))
    model.add(BatchNormalization(name='batch_norm_layer_1'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # Conv Block 2
    model.add(Conv2D(32, (3, 3), name='conv_layer_2', strides=1))
    model.add(BatchNormalization(name='batch_norm_layer_2'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # Conv Block 3
    model.add(Conv2D(64, (3, 3), name='conv_layer_3', strides=1))
    model.add(BatchNormalization(name='batch_norm_layer_3'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # FC Layers
    model.add(Flatten())
    model.add(Dense(128, name='regression_fc_1'))
    model.add(Activation('relu'))
    model.add(Dense(64, name='rl_fc_1'))
    model.add(Activation('relu'))
    model.add(Dense(5, name='rl_fc_2'))
    model.add(Activation('linear'))

    return model
