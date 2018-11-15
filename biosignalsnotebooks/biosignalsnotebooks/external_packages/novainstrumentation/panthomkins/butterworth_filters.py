from novainstrumentation import filter


def butter_lowpass_filter(data, cutoff, fs):
    y = filter.lowpass(data, cutoff, order=2, fs=fs)
    return y


def butter_bandpass_filter(data, cutoffa, cutoffb, fs):
    y = filter.bandpass(data, cutoffa, cutoffb, fs=fs, order=2)
    return y


def butter_bandstop_filter(data, cutoffa, cutoffb, fs):
    y = filter.bandstop(data, cutoffa, cutoffb, fs=fs, order=2)
    return y


def butter_high_pass(data, cutoff, fs):
    y = filter.highpass(data, cutoff, order=2, fs=fs)
    return y
