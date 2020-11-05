"""
 Functions intended to handle android sensor recordings from the OpenSignals mobile app. The file format is always .txt

 Available Functions:
 -------------------
 [Public]

 re_sample_data: function to re-sample android sensor data from a non-equidistant sampling to an equidistant sampling


 Available Functions
-------------------
[Private]

_calc_avg_sampling_rate: function to calculate the average sampling rate of signals recorded with an android sensor


Observations/Comments
---------------------
None

/\
"""

import numpy as np
import scipy.interpolate as scp
from .aux_functions import _calc_time_precision, _truncate_time, _truncate_value


def re_sample_data(time_axis, data, start=0, stop=-1, shift_time_axis=False, sampling_rate=None, kind_interp='linear'):
    '''
    function to re-sample android sensor data from a non-equidistant sampling to an equidistant sampling
    Parameters
    ----------
    time_axis (N, array_like): A 1D array containing the original time axis of the data

    data (...,N,..., array_like): A N-D array containing data columns that are supposed to be interpolated.
                                  The length of data along the interpolation axis has to be the same size as time.

    start (int, optional): The sample from which the interpolation should be started. When not specified the
                           interpolation starts at 0. When specified the signal will be cropped to this value.

    stop (int, optional): The sample at which the interpolation should be stopped. When not specified the interpolation
                          stops at the last value. When specified the signal will be cropped to this value.

    shift_time_axis (bool, optional): If true the time axis will be shifted to start at zero and will be converted to seconds.

    sampling_rate (int, optional): The sampling rate in Hz to which the signal should be re-sampled.
                                   The value should be > 0.
                                   If not specified the signal will be re-sampled to the next tens digit with respect to
                                   the approximate sampling rate of the signal (i.e. approx. sampling of 99.59 Hz will
                                   be re-sampled to 100 Hz).

    kind_interp (string, optional): Specifies the kind of interpolation method to be used as string.
                                    If not specified, 'linear' interpolation will be used.
                                    Available options are: ‘linear’, ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’,
                                    ‘previous’, ‘next’.

    Returns
    -------

    the new time_axis, the interpolated data, and the sampling rate

    '''

    # crop the data and time to specified start and stop values
    if start != 0 or stop != -1:
        time_axis = time_axis[start:stop]

        # check for dimensionality of the data
        if data.ndim == 1:  # 1D array

            data = data[start:stop]

        else:  # multidimensional array

            data = data[start:stop, :]

    # get the original time origin
    time_origin = time_axis[0]

    # shift time axis (shifting is done in order to simplify the calculations)
    time_axis = time_axis - time_origin
    time_axis = time_axis * 1e-9

    # calculate the approximate sampling rate and round it to the next tens digit
    if sampling_rate is None:

        # get the average sampling rate
        sampling_rate = _calc_avg_sampling_rate(time_axis)

    # create new time axis
    time_inter = np.arange(time_axis[0], time_axis[-1], 1 / sampling_rate)

    # check for the dimensionality of the data array.
    if data.ndim == 1:  # 1D array

        # create the interpolation function
        inter_func = scp.interp1d(time_axis, data, kind=kind_interp)

        # calculate the interpolated column and save it to the correct column of the data_inter array
        data_inter = inter_func(time_inter)

        # truncate the interpolated data
        data_inter = np.array([_truncate_value(value) for value in data_inter])

    else:  # multidimensional array

        # create dummy array
        data_inter = np.zeros([time_inter.shape[0], data.shape[1]])

        # cycle over the columns of data
        for col in range(data.shape[1]):
            # create the interpolation function
            inter_func = scp.interp1d(time_axis, data[:, col], kind=kind_interp)

            # calculate the interpolated data
            di = inter_func(time_inter)

            # truncate the interpolated data and save the data to the correct column of the dat_inter array
            data_inter[:, col] = np.array([_truncate_value(value) for value in di])

    # check if time is not supposed to be shifted
    if not shift_time_axis:
        # shift back
        time_inter = time_inter * 1e9
        time_inter = time_inter + time_origin
    else:

        # calculate the precision needed
        precision = _calc_time_precision(sampling_rate)

        # truncate the time axis to the needed precision
        time_inter = [_truncate_time(value, precision) for value in time_inter]

    # return the interpolated time axis and data
    return time_inter, data_inter, sampling_rate

# ==================================================================================================
# ================================= Private Functions ==============================================
# ==================================================================================================


def _calc_avg_sampling_rate(time_axis, unit='seconds', round=True):
    '''
    function to calculate the average sampling rate of signals recorded with an android sensor. The sampling rate is
    rounded to the next tens digit if specified(i.e 34.4 Hz = 30 Hz | 87.3 Hz = 90 Hz).
    sampling rates below 5 Hz are set to 1 Hz.

    Parameters
    ----------
    time_axis (N array_like): The time axis of the sensor
    unit (string, optional): the unit of the time_axis. Either 'seconds' or 'nanoseconds' can be used.
                             If not specified 'seconds' is used
    round (boolean, true): Boolean to indicate whether the sampling rate should be rounded to the next tens digit

    Returns
    -------
    avg_sampling_rate: the average sampling rate of the sensor

    '''

    # check the input for unit and set the dividend accordingly
    if(unit == 'seconds'):

        dividend = 1

    elif(unit == 'nanoseconds'):

        dividend = 1e9

    else:  # invalid input

        raise IOError('The value for unit is not valid. Use either seconds or nanoseconds')


    # calculate the distance between sampling points
    # data[:,0] is the time axis
    sample_dist = np.diff(time_axis)

    # calculate the mean distance
    mean_dist = np.mean(sample_dist)

    # calculate the sampling rate and add it to the list
    # 1e9 is used because the time axis is in nanoseconds
    avg_sampling_rate = dividend / mean_dist

    # round the sampling rate if specified
    if(round):
        avg_sampling_rate = _round_sampling_rate(avg_sampling_rate)

    return avg_sampling_rate


def _round_sampling_rate(sampling_rate):
    """
    Function for round the sampling rate to the nearest tens digit. Sampling rates below 5 Hz are set to 1 Hz

    Parameters
    ----------
    sampling_rate: A sampling rate

    Returns
    -------
    rounded_sampling rate: the sampling rounded to the next tens digit
    """
    # check if sampling rate is below 5 Hz in that case always round to one
    if sampling_rate < 5:

        # set sampling rate to 1
        rounded_sampling_rate = 1

    else:

        # round to the nearest 10 digit
        rounded_sampling_rate = round(sampling_rate/10) * 10

    return rounded_sampling_rate
