# coding=utf-8
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

plotfft
    This functions computes the Fast Fourier Transform of a signal, returning the frequency and magnitude values.

lowpass
    For a given signal s rejects (attenuates) the frequencies higher than the cutoff frequency f and passes the
    frequencies lower than that value by applying a Butterworth digital filter.

highpass
    For a given signal s rejects (attenuates) the frequencies lower then the cutoff frequency f and passes the
    frequencies higher than that value by applying a Butterworth digital filter.

bandstop
    For a given signal s rejects (attenuates) the frequencies within a certain range (between f1 and f2) and passes the
    frequencies outside that range by applying a Butterworth digital filter.

bandpass
    For a given signal s passes the frequencies within a certain range (between f1 and f2) and rejects (attenuates) the
    frequencies outside that range by applying a Butterworth digital filter.

Observations/Comments
---------------------
None

/\
"""

import numpy
from scipy.signal import filtfilt, butter, lfilter
from .aux_functions import _interpolated_segments
from .detect import tachogram
from .visualise import plot


def poincare(data, sample_rate, signal=False, in_seconds=False):
    """
    -----
    Brief
    -----
    Function for generation of Poincaré Plot (Heart rate variability analysis).

    -----------
    Description
    -----------
    ECG signals measure the electric potential in the heart of the subject. In normal conditions, it is expeted that the
    the electric potential to be similar in different heartbeats and that the rhythm of those heartbeats to be
    maintained if all the conditions are maintained. Thus, by plotting the current RR interval against the previous one,
    it is expected that the values to be maintained. Poincaré plot, is this representation, which allows to analyse the
    heart rate variability.

    This function returns the x and y axis of a Poincaré plot and also the standard deviations of the more
    representative directions of the data points.

    ----------
    Parameters
    ----------
    data : list
        ECG signal or R peak list. When the input is a raw signal the input flag signal should be
        True.

    sample_rate : int
        Sampling frequency.

    signal : boolean
        If True, then the data argument contains the set of the ECG acquired samples.

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
    -----
    Brief
    -----
    Smooth the data using a window with requested size.

    -----------
    Description
    -----------
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal (with the window size) in both ends so that
    transient parts are minimized in the beginning and end part of the output signal.

    The results of the application of this functions is analogous to the application of a mean filter in image
    processing. The results is the smoothed input_signal.

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


def plotfft(s, fmax, doplot=False):
    """
    -----
    Brief
    -----
    This functions computes the Fast Fourier Transform of a signal, returning the frequency and magnitude values.

    -----------
    Description
    -----------
    Fast Fourier Transform (FFT) is a method to computationally calculate the Fourier Transform of discrete finite
    signals. This transform converts the time domain signal into a frequency domain signal by abdicating the temporal
    dimension.

    This function computes the FFT of the input signal and returns the frequency and respective amplitude values.

    ----------
    Parameters
    ----------
    s: array-like
      the input signal.
    fmax: int
      the sampling frequency.
    doplot: boolean
      a variable to indicate whether the plot is done or not.

    Returns
    -------
    f: array-like
      the frequency values (xx axis)
    fs: array-like
      the amplitude of the frequency values (yy axis)
    """

    fs = abs(numpy.fft.fft(s))
    f = numpy.linspace(0, fmax / 2, int(len(s) / 2))
    if doplot:
        plot(list(f[1:int(len(s) / 2)]), list(fs[1:int(len(s) / 2)]))
    return f[1:int(len(s) / 2)].copy(), fs[1:int(len(s) / 2)].copy()


def lowpass(s, f, order=2, fs=1000.0, use_filtfilt=False):
    """
    -----
    Brief
    -----
    For a given signal s rejects (attenuates) the frequencies higher than the cutoff frequency f and passes the
    frequencies lower than that value by applying a Butterworth digital filter.

    -----------
    Description
    -----------
    Signals may have frequency components of multiple bands. If our interest is to have an idea about the behaviour
    of low frequency bands, we should apply a low pass filter, which would attenuate the higher frequencies of the
    signal. The degree of attenuation is controlled by the parameter "order", that as it increases, allows to better
    attenuate frequencies closer to the cutoff frequency. Notwithstanding, the higher the order, the higher the
    computational complexity and the higher the instability of the filter that may compromise the results.

    This function allows to apply a low pass Butterworth digital filter and returns the filtered signal.

    ----------
    Parameters
    ----------
    s: array-like
        signal
    f: int
        the cutoff frequency
    order: int
        Butterworth filter order
    fs: float
        sampling frequency
    use_filtfilt: boolean
        If True, the signal will be filtered once forward and then backwards. The result will have zero phase and twice
        the order chosen.

    Returns
    -------
    signal: array-like
        filtered signal

    """
    b, a = butter(order, f / (fs/2))

    if use_filtfilt:
        return filtfilt(b, a, s)

    return lfilter(b, a, s)


def highpass(s, f, order=2, fs=1000.0, use_filtfilt=False):
    """
    -----
    Brief
    -----
    For a given signal s rejects (attenuates) the frequencies lower then the cutoff frequency f and passes the
    frequencies higher than that value by applying a Butterworth digital filter.

    -----------
    Description
    -----------
    Signals may have frequency components of multiple bands. If our interest is to have an idea about the behaviour
    of high frequency bands, we should apply a high pass filter, which would attenuate the lower frequencies of the
    signal. The degree of attenuation is controlled by the parameter "order", that as it increases, allows to better
    attenuate frequencies closer to the cutoff frequency. Notwithstanding, the higher the order, the higher the
    computational complexity and the higher the instability of the filter that may compromise the results.

    This function allows to apply a high pass Butterworth digital filter and returns the filtered signal.

    ----------
    Parameters
    ----------
    s: array-like
        signal
    f: int
        the cutoff frequency
    order: int
        Butterworth filter order
    fs: float
        sampling frequency
    use_filtfilt: boolean
        If True, the signal will be filtered once forward and then backwards. The result will have zero phase and twice
        the order chosen.

    Returns
    -------
    signal: array-like
        filtered signal

    """

    b, a = butter(order, f * 2 / (fs/2), btype='highpass')
    if use_filtfilt:
        return filtfilt(b, a, s)

    return lfilter(b, a, s)


def bandstop(s, f1, f2, order=2, fs=1000.0, use_filtfilt=False):
    """
    -----
    Brief
    -----
    For a given signal s rejects (attenuates) the frequencies within a certain range (between f1 and f2) and passes the
    frequencies outside that range by applying a Butterworth digital filter.

    -----------
    Description
    -----------
    Signals may have frequency components of multiple bands. If our interest is to have an idea about the behaviour
    of all frequency bands except a specific band, we should apply a band stop filter, which would attenuate the
    frequencies of that band of the signal. The degree of attenuation is controlled by the parameter "order", that as it
    increases, allows to better attenuate frequencies closer to the cutoff frequencies. Notwithstanding, the higher the
    order, the higher the computational complexity and the higher the instability of the filter which may compromise the
    results.

    This function allows to apply a band stop Butterworth digital filter and returns the filtered signal.

    ----------
    Parameters
    ----------
    s: array-like
        signal
    f1: int
        the lower cutoff frequency
    f2: int
        the upper cutoff frequency
    order: int
        Butterworth filter order
    fs: float
        sampling frequency
    use_filtfilt: boolean
        If True, the signal will be filtered once forward and then backwards. The result will have zero phase and twice
        the order chosen.

    Returns
    -------
    signal: array-like
        filtered signal

    """
    b, a = butter(order, [f1 * 2 / fs, f2 * 2 / fs], btype='bandstop')
    if use_filtfilt:
        return filtfilt(b, a, s)
    return lfilter(b, a, s)


def bandpass(s, f1, f2, order=2, fs=1000.0, use_filtfilt=False):
    """
    -----
    Brief
    -----
    For a given signal s passes the frequencies within a certain range (between f1 and f2) and rejects (attenuates) the
    frequencies outside that range by applying a Butterworth digital filter.

    -----------
    Description
    -----------
    Signals may have frequency components of multiple bands. If our interest is to have an idea about the behaviour
    of a specific frequency band, we should apply a band pass filter, which would attenuate all the remaining
    frequencies of the signal. The degree of attenuation is controlled by the parameter "order", that as it increases,
    allows to better attenuate frequencies closer to the cutoff frequency. Notwithstanding, the higher the order, the
    higher the computational complexity and the higher the instability of the filter that may compromise the results.

    This function allows to apply a band pass Butterworth digital filter and returns the filtered signal.

    ----------
    Parameters
    ----------
    s: array-like
        signal
    f1: int
        the lower cutoff frequency
    f2: int
        the upper cutoff frequency
    order: int
        Butterworth filter order
    fs: float
        sampling frequency
    use_filtfilt: boolean
        If True, the signal will be filtered once forward and then backwards. The result will have zero phase and twice
        the order chosen.

    Returns
    -------
    signal: array-like
        filtered signal

    """
    b, a = butter(order, [f1 * 2 / fs, f2 * 2 / fs], btype='bandpass')

    if use_filtfilt:
        return filtfilt(b, a, s)

    return lfilter(b, a, s)


def mean_wave(segments):
    """
    -----
    Brief
    -----
    Compute the mean wave of a set of waves/segments.

    -----------
    Description
    -----------
    Calculate the mean wave of a set of waves/segments, which consists on averaging all point corresponding to the same
    point in time. The resulting points are then ordered in time to form the new mean wave. If the input waves have
    different numbers of points, they are interpolated to the length of the largest wave before the computation.

    This function allows to calculate the mean wave of the input segments.

    ----------
    Parameters
    ----------
    segments: array-like
        Waves or segments considered to compute the mean wave.

    Returns
    -------
    mean_wave: array-like
        mean wave of the input waves/segments.
    """
    segments = _interpolated_segments(segments)
    organized_segment = segments.copy().T
    mean_wave = [numpy.mean(seg) for seg in organized_segment]

    return mean_wave
# 25/09/2018 18h58m :)
