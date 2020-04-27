#import pylab as pl
import numpy as np
from os import path
from numpy import abs, linspace, sin, pi, int16
import pandas


def plotfft(s, fmax, doplot=False):
    """ This functions computes the fft of a signal, returning the frequency
    and their magnitude values.

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

    fs = abs(np.fft.fft(s))
    f = linspace(0, fmax / 2, int(len(s) / 2))
    if doplot:
        #pl.plot(f[1:int(len(s) / 2)], fs[1:int(len(s) / 2)])
        pass
    return (f[1:int(len(s) / 2)].copy(), fs[1:int(len(s) / 2)].copy())


def synthbeats2(duration, meanhr=60, stdhr=1, samplingfreq=250):
    #Minimaly based on the parameters from:
    #http://physionet.cps.unizar.es/physiotools/ecgsyn/Matlab/ecgsyn.m
    #Inputs: duration in seconds
    #Returns: signal, peaks

    ibi = 60 / float(meanhr) * samplingfreq

    sibi = ibi - 60 / (float(meanhr) - stdhr) * samplingfreq

    peaks = np.arange(0, duration * samplingfreq, ibi)

    peaks[1:] = peaks[1:] + np.random.randn(len(peaks) - 1) * sibi

    if peaks[-1] >= duration * samplingfreq:
        peaks = peaks[:-1]
    peaks = peaks.astype('int')
    signal = np.zeros(duration * samplingfreq)
    signal[peaks] = 1.0

    return signal, peaks


# def synthbeats(duration, meanhr=60, stdhr=1, samplingfreq=250, sinfreq=None):
#     #Minimaly based on the parameters from:
#     #http://physionet.cps.unizar.es/physiotools/ecgsyn/Matlab/ecgsyn.m
#     #If freq exist it will be used to generate a sin instead of using rand
#     #Inputs: duration in seconds
#     #Returns: signal, peaks
#
#     t = np.arange(duration * samplingfreq) / float(samplingfreq)
#     signal = np.zeros(len(t))
#
#     print(len(t))
#     print(len(signal))
#
#     if sinfreq == None:
#
#         npeaks = 1.2 * (duration * meanhr / 60)
#         # add 20% more beats for some cummulative error
#         hr = pl.randn(npeaks) * stdhr + meanhr
#         peaks = pl.cumsum(60. / hr) * samplingfreq
#         peaks = peaks.astype('int')
#         peaks = peaks[peaks < t[-1] * samplingfreq]
#
#     else:
#         hr = meanhr + sin(2 * pi * t * sinfreq) * float(stdhr)
#         index = int(60. / hr[0] * samplingfreq)
#         peaks = []
#         while index < len(t):
#             peaks += [index]
#             index += int(60. / hr[index] * samplingfreq)
#
#     signal[peaks] = 1.0
#
#     return t, signal, peaks


def load_with_cache(file_, recache=False, sampling=1,
                    columns=None, temp_dir='.', data_type='int16'):
    """@brief This function loads a file from the current directory and saves
    the cached file to later executions. It's also possible to make a recache
    or a subsampling of the signal and choose only a few columns of the signal,
    to accelerate the opening process.

    @param file String: the name of the file to open.
    @param recache Boolean: indication whether it's done recache or not
    (default = false).
    @param sampling Integer: the sampling step. if 1, the signal isn't
    sampled (default = 1).
    @param columns Array-Like: the columns to read from the file. if None,
    all columns are considered (default = None).

    @return data Array-Like: the data from the file.
    TODO: Should save cache in a different directory
    TODO: Create test function and check size of generated files
    TODO: receive a file handle
    """

    
    
    cfile = '%s.npy' % file_

    if (not path.exists(cfile)) or recache:
        if columns == None:
            data = np.loadtxt(file_)[::sampling, :]
        else:
            data = np.loadtxt(file_)[::sampling, columns]

        np.save(cfile, data.astype(data_type))
    else:
        data = np.load(cfile)
    return data


def load_data(filename):
    """
    :rtype : numpy matrix
    """
    data = pandas.read_csv(filename, header=None, delimiter='\t', skiprows=9)
    return data.as_matrix()
    

