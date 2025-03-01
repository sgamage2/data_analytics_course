import time_series_generator as gen
import data_point as dp

import math
import matplotlib.pyplot as plt
import csv
import numpy as np

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM


def load_series_from_file(start_timestamp, filename):
    with open(filename, newline='') as file:
        reader = csv.reader(file)
        series = []
        timestamp = start_timestamp    # Start here
        for i, row in enumerate(reader):
            if i > 0:   # Ignore first row with column names
                sample_X = np.array(row[1:])    # Ignore timestamp
                series.append(dp.DataPoint(timestamp, sample_X, False, False))
                timestamp = timestamp + 1/365

    return series


def get_data(start_timestamp, filename):
    print("get_data: Loading data from filename={}".format(filename))
    series = load_series_from_file(start_timestamp, filename)
    dimension = len(series[0].X)
    print("\t dimension={}".format(dimension))
    return dimension, series


def plot_series(series, title):
    t = [point.t for point in series]
    x1 = [point.X[0] for point in series]
    # x2 = [point.X[1] for point in series]

    plt.plot(t, x1, label=title+' - dimension-1', linewidth=0.5)
    # plt.plot(t, x2, label=title+'_dimension-2')

    plt.title(title)
    plt.xlabel("t")
    plt.ylabel("y")
    plt.legend(loc='upper right')


###################################################################################################
"""
Fit an LSTM network to a 2-D time series prediction
"""
def test_LSTM_model():
    dimension, train_series = get_data(2013, "/home/sunanda/Sunanda/PhD Study/Data Analytics/data_analytics_course/assignment_1/data/item1_train.csv")
    plot_series(train_series, "Training series")

    # LSTM Architecture
    input_layer_units = dimension   # Dimensionality of time series data
    hidden_layer_1_units = 200
    hidden_layer_2_units = 50
    output_layer_units = input_layer_units  # We want to simultaneously predict all dimensions of time-series data

    input_timesteps = 5
    output_timesteps = 1    # This must be 1, because for now we only have the capability to predict one-step ahead

    # Training params
    batch_size = 25 # Mini batch size in GD/ other algorithm
    epcohs = 200 # 50 is good

    # Create network
    model = Sequential()
    # model.add(LSTM(hidden_layer_1_units, batch_input_shape=(batch_size, input_timesteps, input_layer_units), stateful=True))
    model.add(LSTM(hidden_layer_1_units, input_shape=(input_timesteps, input_layer_units)))
    model.add(Dense(output_layer_units))
    model.compile(loss='mae', optimizer='adam')

    # Train network
    X_train, Y_train = gen.prepare_dataset(train_series, input_timesteps, output_timesteps)
    history = model.fit(X_train, Y_train, epochs=epcohs, batch_size=batch_size, verbose=2)
                        # , validation_data=(test_X, test_y), shuffle=False)

    # Plot training history
    plt.figure()
    plt.title("Training history")
    plt.plot(history.history['loss'], label='training_loss')
    plt.xlabel("Epoch")
    # plt.plot(history.history['val_loss'], label='test')
    plt.legend()


    # Predict on test data
    dim2, test_series = get_data(2017, "/home/sunanda/Sunanda/PhD Study/Data Analytics/data_analytics_course/assignment_1/data/item1_test.csv")
    test_t_range = (test_series[0].t, test_series[-1].t)
    X_test, Y_test = gen.prepare_dataset(test_series, input_timesteps, output_timesteps)

    Y_predicted = model.predict(X_test)

    Y_predicted_series = gen.convert_to_series(Y_predicted, test_t_range)
    Y_test_series = gen.convert_to_series(Y_test, test_t_range)
    # plot_series("Y_test")
    plt.figure()
    plot_series(train_series, "Y_train_set_true")
    plot_series(Y_test_series, "Y_test_true")
    plot_series(Y_predicted_series, "Y_test_predicted")
    plt.title("Test prediction")


    # # Predict on training data
    # Y_predicted_on_train = model.predict(X_train)
    # train_t_range = (train_series[0].t, train_series[-1].t)
    # Y_predicted_on_train_series = gen.convert_to_series(Y_predicted_on_train, train_t_range)
    #
    # plt.figure()
    # plot_series(train_series, "Y_train_set_true")
    # plot_series(Y_predicted_on_train_series, "Y_predicted_on_train_set")
    # plt.title("Train set prediction")

    plt.show()
    pass


###################################################################################################

# Call test functions

test_LSTM_model()