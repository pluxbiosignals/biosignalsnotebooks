
"""
Processing capabilities that are more general than the remaining modules categories.

Available Functions
-------------------
[Public]

poincare
    With this function the user can easily generate a Poincaré Plot (Heart rate variability
    analysis).

smooth
    Function intended to smooth a signal through the application of the convolution operation
    between a moving average window (the signal is segmented into multiple parts) and a fixed window
    (from one of the predefined formats 'hanning', 'blackman'...) in order to a weigh be attributed
    to each sample inside the moving window.

Observations/Comments
---------------------
None

/\
"""

import numpy
from .detect import tachogram


def poincare(data, sample_rate, signal=False, in_seconds=False):
    """
    Function for generation of Poincaré Plot (Heart rate variability analysis)

    ----------
    Parameters
    ----------
    data : list
        ECG signal or R peak list. When the input is a raw signal the input flag signal should be
        True.

    sample_rate : int
        Sampling frequency.

    signal : boolean
        If true, then the data argument contains the set of the ECG acquired samples.

    in_seconds : boolean
        If the R peaks list defined as the input argument "data" contains the sample numbers where
        the R peaks occur,
        then in_seconds needs to be True.

    Returns
    -------
    out : list, list, float, float
        Poincaré plot x axis and y axis, respectively. Additionally it will be returned SD1 and SD2
        parameters.

    """

    # Generation of tachogram.
    tachogram_data = tachogram(data, sample_rate, signal=signal, in_seconds=in_seconds,
                               out_seconds=True)[0]

    # Poincaré Plot (x and y axis).
    x_axis = tachogram_data[:-1]
    y_axis = tachogram_data[1:]

    # Poincaré Parameters.
    tachogram_diff = numpy.diff(tachogram_data)
    sdsd = numpy.std(tachogram_diff)
    sdnn = numpy.std(tachogram_data)

    sd1 = numpy.sqrt(0.5 * numpy.power(sdsd, 2))
    sd2 = numpy.sqrt(2 * numpy.power(sdnn, 2) - numpy.power(sd1, 2))

    return x_axis, y_axis, sd1, sd2


def smooth(input_signal, window_len=10, window='hanning'):
    """
    @brief: Smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the beginning and end part of the output signal.

    ----------
    Parameters
    ----------
    input_signal: array-like
        the input signal
    window_len: int
        the dimension of the smoothing window. the default is 10.
    window: string.
        the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'.
        flat window will produce a moving average smoothing. the default is 'hanning'.

    Returns
    -------
    out :   signal_filt: array-like the smoothed signal.

    @example:
                time = linspace(-2,2,0.1)
                input_signal = sin(t)+randn(len(t))*0.1
                signal_filt = smooth(x)


    @see also:  numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman,
                numpy.convolve, scipy.signal.lfilter


    @todo: the window parameter could be the window itself if an array instead
    of a string

    @bug: if window_len is equal to the size of the signal the returning
    signal is smaller.
    """

    if input_signal.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if input_signal.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return input_signal

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("""Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'""")

    sig = numpy.r_[2 * input_signal[0] - input_signal[window_len:0:-1],
                   input_signal, 2 * input_signal[-1] - input_signal[-2:-window_len-2:-1]]

    if window == 'flat':  # moving average
        win = numpy.ones(window_len, 'd')
    else:
        win = eval('numpy.' + window + '(window_len)')

    sig_conv = numpy.convolve(win / win.sum(), sig, mode='same')

    return sig_conv[window_len: -window_len]

# 25/09/2018 18h58m :)
