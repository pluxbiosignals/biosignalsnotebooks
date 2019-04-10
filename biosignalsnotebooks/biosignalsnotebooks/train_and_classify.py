# coding=utf-8
"""
Functions intended to be used in machine learning problems.

Available Functions
-------------------
[Public]

windowing
    Function to window the input signal, that return the windowed signal.

zero_crossing_rate
    Get the zero-crossing rate of the input signal.

features_extraction
    Function to extract features given in functions, that returns an array with the set of features
    for each time window.

Observations/Comments
---------------------
None

/\
"""
import numpy as np


def windowing(signal, sampling_rate=1000, time_window=.25):
    """
    -----
    Brief
    -----
    Function to window the input signal, that return the windowed signal.

    -----------
    Description
    -----------
    Machine learning pipelines usually use features to represent each sample of the input signals.
    In order to extract those features, it is required to window the signal in time intervals,
    in the case of time series, that may be or may not be of the same duration with or without overlap.

    This function allows to window the input signal in similar time windows with or without overlap.

    ----------
    Parameters
    ----------
    signal : list or numpy.array
        Signal to be windowed.
    sampling_rate : int
        Sampling rate of the input signal.
    time_window : float or int
        Time in seconds of each window.

    Returns
    -------
        Windowed signal

    """
    # TODO: Add overlap
    app_window = int(sampling_rate * time_window)

    num_windows = len(signal) // app_window
    signal_windows = np.zeros(shape=(num_windows, app_window))

    for i in range(num_windows):
        signal_windows[i] = signal[i * app_window:(i + 1) * app_window]
    return signal_windows


def zero_crossing_rate(signal):
    """
    -----
    Brief
    -----
    Get the zero-crossing rate of the input signal.

    -----------
    Description
    -----------
    Zero-crossing rate is a widely used feature used to represent a signal. This feature gives the number of times
    a signal cross the zero, which means, the number of times it changes polarity.

    This function returns an int indicating the number of times the input signal crosses the zero value.

    ----------
    Parameters
    ----------

    signal : list or numpy.array
        Input signal.

    Returns
    -------
        Number of times the input signal crosses the zero value.
    """
    return (np.diff(np.sign(signal)) != 0).sum()


def features_extraction(windowed_signal, functions):
    """
    -----
    Brief
    -----
    Function to extract features given in functions, that returns an array with the set of features
    for each time window.

    -----------
    Description
    -----------
    Machine learning pipelines usually use features to represent each sample of the input signals.
    Those features should be relevant in the sense that they should be useful to distinguish between the classes
    of each specific problem, and not redundant, as the usage of redundant features usually improves the complexity
    of the problem without improving its results.

    This function allows to extract features from the various windows provided in windowed_signal.

    ----------
    Parameters
    ----------
    windowed_signal: list or numpy.array
        Input windowed signal (if your signal is not windowed, you can use the function windowing of this module).
    functions: list
        List of functions that will be applied to each window. For example: [numpy.mean, numpy.std]

    Returns
    -------
        Array of features with shape (n_windows, n_features).
    """
    features = np.zeros(shape=(windowed_signal.shape[0], len(functions)))

    for i, window in enumerate(windowed_signal):
        fea = []
        for f in functions:
            fea.append(f(window))
        features[i] = fea

    return features
