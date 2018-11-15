"""
novainstrumentation

peak finding module
"""

from numpy import array, clip, argsort, sort
import numpy as np
#from pylab import find
#from scipy.signal import argrelmax

#### FROM SCIPY
#### Given that the new version failed to compile in some linux versions



def _boolrelextrema(data, comparator,
                  axis=0, order=1, mode='clip'):
    """
    Calculate the relative extrema of `data`.

    Relative extrema are calculated by finding locations where
    ``comparator(data[n], data[n+1:n+order+1])`` is True.

    Parameters
    ----------
    data : ndarray
        Array in which to find the relative extrema.
    comparator : callable
        Function to use to compare two data points.
        Should take 2 numbers as arguments.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n,n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.  'wrap' (wrap around) or
        'clip' (treat overflow as the same as the last (or first) element).
        Default 'clip'.  See numpy.take

    Returns
    -------
    extrema : ndarray
        Indices of the extrema, as boolean array of same shape as data.
        True for an extrema, False else.

    See also
    --------
    argrelmax, argrelmin

    Examples
    --------
    array([False, False,  True, False, False], dtype=bool)

    """
    if((int(order) != order) or (order < 1)):
        raise ValueError('Order must be an int >= 1')

    datalen = data.shape[axis]
    locs = np.arange(0, datalen)

    results = np.ones(data.shape, dtype=bool)
    main = data.take(locs, axis=axis, mode=mode)
    for shift in iter(range(1, order + 1)):
        plus = data.take(locs + shift, axis=axis, mode=mode)
        minus = data.take(locs - shift, axis=axis, mode=mode)
        results &= comparator(main, plus)
        results &= comparator(main, minus)
        if(~results.any()):
            return results
    return results


def argrelmin(data, axis=0, order=1, mode='clip'):
    """
    Calculate the relative minima of `data`.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    data : ndarray
        Array in which to find the relative minima.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n, n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.
        Available options are 'wrap' (wrap around) or 'clip' (treat overflow
        as the same as the last (or first) element).
        Default 'clip'. See numpy.take

    Returns
    -------
    extrema : ndarray
        Indices of the minima, as an array of integers.

    See also
    --------
    argrelextrema, argrelmax

    Notes
    -----
    This function uses `argrelextrema` with np.less as comparator.

    """
    return argrelextrema(data, np.less, axis, order, mode)


def argrelmax(data, axis=0, order=1, mode='clip'):
    """
    Calculate the relative maxima of `data`.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    data : ndarray
        Array in which to find the relative maxima.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n, n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.
        Available options are 'wrap' (wrap around) or 'clip' (treat overflow
        as the same as the last (or first) element).
        Default 'clip'.  See `numpy.take`.

    Returns
    -------
    extrema : ndarray
        Indices of the maxima, as an array of integers.

    See also
    --------
    argrelextrema, argrelmin

    Notes
    -----
    This function uses `argrelextrema` with np.greater as comparator.

    """
    return argrelextrema(data, np.greater, axis, order, mode)


def argrelextrema(data, comparator, axis=0, order=1, mode='clip'):
    """
    Calculate the relative extrema of `data`.

    .. versionadded:: 0.11.0

    Parameters
    ----------
    data : ndarray
        Array in which to find the relative extrema.
    comparator : callable
        Function to use to compare two data points.
        Should take 2 numbers as arguments.
    axis : int, optional
        Axis over which to select from `data`.  Default is 0.
    order : int, optional
        How many points on each side to use for the comparison
        to consider ``comparator(n, n+x)`` to be True.
    mode : str, optional
        How the edges of the vector are treated.  'wrap' (wrap around) or
        'clip' (treat overflow as the same as the last (or first) element).
        Default is 'clip'.  See `numpy.take`.

    Returns
    -------
    extrema : ndarray
        Indices of the extrema, as an array of integers (same format as
        np.argmin, np.argmax).

    See also
    --------
    argrelmin, argrelmax

    """
    results = _boolrelextrema(data, comparator,
                              axis, order, mode)
    if ~results.any():
        return (np.array([]),) * 2
    else:
        return np.where(results)


#### FROM SCIPY 



def peaks(signal, tol=None):
    """ This function detects all the peaks of a signal and returns those time
    positions. To reduce the amount of peaks detected, a threshold is
    introduced so only the peaks above that value are considered.

    Parameters
    ----------
    x: array-like
     the signal with the peaks to detect.
    tol: int
      the threshold used to limit the peak detection. in case none is given,
      the value used is the minimum of the signal (detection of peaks in all
      signal)

    Returns
    -------
    peaks: array-like
      the time sample where the peak occurs.

    Example
    -------
    >>> peaks([1,2,4,3,2,5,7,7,4,9,2])
    array([2, 9])
    >>> peaks([1,2,-4,-3,-5,4,5])
    array([1, 3])
    >>> peaks([1,-4,-3,4,5],0)
    array([], dtype=int32)
    """

    if (tol is None):
        tol = min(signal)
    pks = argrelmax(clip(signal, tol, signal.max()))
    return pks[0]


#def post_peak(v, v_post):
#    """ Detects the next peak """
#    return array([v_post[find(v_post > i)[0]] for i in v])


#def prior_peak(v, v_prior):
#    """ Detects the previous peak """
#    return array([v_prior[find(v_prior < i)[-1]] for i in v])


def clean_near_peaks(signal, peaks_, min_distance):
    """ Given an array with all the peaks of the signal ('peaks') and a
    distance value ('min_distance') and the signal, by argument, this function
    erases all the unnecessary peaks and returns an array with only the maximum
    peak for each period of the signal (the period is given by the
    min_distance).

    Parameters
    ----------
    signal: array-like
      the original signal.
    peaks: array-like
      the peaks to filter.
    min_distance: int
      the distance value to exclude the unnecessary peaks.

    Returns
    -------
    fp: array-like
      the new peaks, after filtering just the maximum peak per period.

    See also: clean_near_events()
    """

    #order all peaks
    
    ars = argsort(signal[peaks_])
    
    pp = peaks(ars)

    fp = []

    #clean near peaks
    while len(pp) > 0:
        fp += [pp[-1]]
        pp = pp[abs(pp - pp[-1]) > min_distance]

    return sort(array(fp))


def clean_near_events(points, min_distance):
    """ Given an array with some specific points of the signal and a distance
    value, this function erases all the surplus points and returns an array
    with only one point (the first point) per distance samples values

    Parameters
    ----------
    points: array-like
      the events to filter.
    min_distance: int
      the distance value to exclude the unnecessary events.

    Returns
    -------
    fp: array-like
      the new events, after filtering just one per period.
    Example
    -------
    >>> clean_near_events([1,3,5,50,65,68,83,88],10)
    array([ 1, 50, 65, 83])

    See also: clean_near_peaks()
    """

    fp = []
    points = array(points)
    while len(points) > 0:
        fp += [points[0]]
        points = points[abs(points - points[0]) > min_distance]

    return array(fp)
    
from numpy import ceil

def bigPeaks(s,th,min_peak_distance=5,peak_return_percentage=0.1):
    p=peaks(s,th)
    pp=[]
    if len(p)==0:
        pp=[]
    else:
        p=clean_near_peaks(s,p,min_peak_distance)
    
        if len(p)!=0:
            ars=argsort(s[p])
            pp=p[ars]
            
            num_peaks_to_return=ceil(len(p)*peak_return_percentage)
            
            pp=pp[-int(num_peaks_to_return):]
        else:
            pp==[]
    return pp
