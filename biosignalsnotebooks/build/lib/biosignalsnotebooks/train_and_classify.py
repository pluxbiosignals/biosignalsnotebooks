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


def windowing(signal, sampling_rate=1000, time_window=.25, overlap=0):
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
	overlap : float
		Percentage of overlap relative to the time window.

    Returns
    -------
        Windowed signal

    """
    if  overlap < 0 or overlap >= 1:
        raise ValueError("overlap should be a float in [0, 1)")
    over = 1 - overlap
    
    app_window = int(sampling_rate * time_window)

    num_windows = int(len(signal) / (app_window*over))
    signal_windows = np.zeros(shape=(num_windows, app_window))

    for i, win in enumerate(range(0, len(signal), int(over*app_window))):
        if win + app_window < len(signal) and i < num_windows:
            signal_windows[i] = signal[win:win + app_window]
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
        try:
            features[i] = np.concatenate(fea)
        except ValueError:
            features[i] = fea

    return features


def normalize_features(features, type="min_max"):
    """
    -----
    Brief
    -----
    Function to normalize features.

    -----------
    Description
    -----------
    Normalization is the process to bring every feature to the same scale. If type is "min_max", every feature is
    brought to the range of (0, 1). This assures that no feature will be more relevant than the others when given as
    input for machine learning algorithms. If type is "stand", the features are standarized with mean 0 and standard
    deviation 1. The default behavior is to normalize by min_max.

    It is assumed that the input array has the shape (samples, features). This is the shape returned by the function
    features_extraction from this module.

    ----------
    Parameters
    ----------
    features: numpy.array
        Array containing the features with shape (samples, features). This array can be obtained with the function
        features_extraction from this module.
    type: str
        Specifies the type of normalization.

    Returns
    -------
        Array of normalized or standardized features.
    """
    for i, feature in enumerate(np.transpose(features)):
        if type == "stand":
            features[:, i] = feature - np.mean(feature)
            features[:, i] = feature/np.std(feature)
        else:
            features[:, i] = (feature-np.min(feature))
            features[:, i] =  feature / np.ptp(feature)
    return features