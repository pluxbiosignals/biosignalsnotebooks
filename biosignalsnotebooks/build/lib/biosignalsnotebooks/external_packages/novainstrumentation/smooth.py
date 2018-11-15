import numpy


def smooth(input_signal, window_len=10, window='hanning'):
    """
    @brief: Smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the beginning and end part of the output signal.

    @param: input_signal: array-like
                the input signal
            window_len: int
                the dimension of the smoothing window. the default is 10.
            window: string.
                the type of window from 'flat', 'hanning', 'hamming',
                'bartlett', 'blackman'. flat window will produce a moving
                average smoothing. the default is 'hanning'.

    @return: signal_filt: array-like
                the smoothed signal.

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
        raise ValueError("""Window is on of 'flat', 'hanning', 'hamming',
'bartlett', 'blackman'""")

    sig = numpy.r_[2 * input_signal[0] - input_signal[window_len:0:-1],
                input_signal,
                2 * input_signal[-1] - input_signal[-2:-window_len-2:-1]]

    if window == 'flat':  # moving average
        win = numpy.ones(window_len, 'd')
    else:
        win = eval('numpy.' + window + '(window_len)')

    sig_conv = numpy.convolve(win / win.sum(), sig, mode='same')

    return sig_conv[window_len: -window_len]
