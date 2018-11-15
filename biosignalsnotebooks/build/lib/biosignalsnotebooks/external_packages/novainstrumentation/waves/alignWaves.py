from pylab import *
from numpy import *
from ..peaks import peaks
import doctest


def align(w,signals,mode):
    """ Align various waves in a specific point.
    
    Given a mode of alignment, this function computes the specific time point of 
    a wave where all the waves would be aligned. With the difference between the
    time point of the reference wave and the time points of all the other waves, 
    we have the amount of samples the waves will move to align in the specific 
    point computed. 
   
    Parameters
    ----------
    w: array-like
      the input signal to use as a reference of alignment (all the other signals
      will be aligned with this one).
    signals: array-like or matrix-like
      the input signals to align. 
    mode: string
      the mode used in the alignment, from 'max', 'min', 'peak', 'peak_neg', 
      'infMaxAlign' and 'infMinAlign'. 

    Returns
    -------
    nw: a masked array
      a new set of aligned signals in a masked array (some cells have NAN values
      due to the alignment).
        
    Example
    -------
    >>> align([6,3,4,5,2,2],[10,30,28,26,13,20],'max')
    [masked_array(data = [30.0 28.0 26.0 13.0 20.0 --],
                 mask = [False False False False False  True],
           fill_value = 1e+20)
    ]
    >>> align([6,3,4,5,2,2],[10,30,28,26,13,20],'peak')
    [masked_array(data = [-- -- 10.0 30.0 28.0 26.0],
                 mask = [ True  True False False False False],
           fill_value = 1e+20)
    ]
    >>> align([34,4,8],[[100,550,278,67,613,120],[10,470,230,189,856,420]],'min')
    [masked_array(data = [278.0 67.0 613.0 120.0 -- --],
                 mask = [False False False False  True  True],
           fill_value = 1e+20)
    , masked_array(data = [-- 10.0 470.0 230.0 189.0 856.0],
                 mask = [ True False False False False False],
           fill_value = 1e+20)
    ]
    """ 
    
    nw = []
    
    if len(shape(signals))==1:       
        signals = [signals]
               
    for i in range(len(signals)):
        
        if (mode == 'max'):
            al = maxAlign(w,signals[i])
        elif (mode == 'min'):
            al = minAlign(w,signals[i])
        elif (mode == 'peak'):
            al = peakAlign(w,signals[i])
        elif (mode == 'peak_neg'):
            al = peakNegAlign(w,signals[i])
        elif (mode == 'infMaxAlign'):
            al = infMaxAlign(w,signals[i])
        elif (mode == 'infMinAlign'):
            al = infMinAlign(w,signals[i])
                
        nw += [ moveWave(signals[i],al) ]
          
    return nw


def moveWave(w,move):
    """ Move a signal in time.
    
    This function returns a signal created by a shifting in time on the original
    signal. 
   
    Parameters
    ----------
    w: array-like
      the input signal to move.
    move: int
      the ammount of samples to shift the signal (if <0 the signal moves back, 
      if >0 the signal moves forward).

    Returns
    -------
    nw: a masked array
      a new aligned signal in a masked array (some cells have NAN values
      due to the alignment).
        
    
    See also: align()
    """ 
    
    nw = ma.masked_all(len(w))
    
    if (move == 0): 
        #don't move
        nw[0:] = w[0:]  
    elif (move>0):
        #forward
        nw[move:len(w)] = w[:len(w)-move]  
    else:
        #backwards
        nw[:len(w)-abs(move)] = w[abs(move):len(w)]
   
    return nw


def maxAlign(refw,w):
    """ Difference between the maximums positions of the signals.
    
    Given the position in time of each maximum value (argmax) of the signals, 
    this function returns the difference, in samples, between those two events.
    The first signal introduced is the reference signal.
     
   
    Parameters
    ----------
    refw: array-like
      the input reference signal.
    w: array-like
      the input signal.

    Returns
    -------
    al: int
      the difference between the two events position
        
    Example
    -------
    >>> maxAlign([5,7,3,20,13],[0,5,0,4,7])
    -1
    
    See also: minAlign(), peakAlign(), peakNegAlign(), infMaxAlign(), infMinAlign()
    """ 
       
    return argmax(refw)-argmax(w)


def minAlign(refw,w):
    """ Difference between the minimums positions of the signals.
    
    Given the position in time of each minimum value (argmin) of the signals, 
    this function returns the difference, in samples, between those two events.
    The first signal introduced is the reference signal.
     
   
    Parameters
    ----------
    refw: array-like
      the input reference signal.
    w: array-like
      the input signal.

    Returns
    -------
    al: int
      the difference between the two events position
        
    Example
    -------
    >>> minAlign([5,7,3,20,13],[0,5,-4,4,7])
    0
    
    See also: maxAlign(), peakAlign(), peakNegAlign(), infMaxAlign(), infMinAlign()
    """ 
       
    return argmin(refw)-argmin(w)


def peakAlign(refw,w):
    """ Difference between the maximum peak positions of the signals.
    
    This function returns the difference, in samples, between the peaks position 
    of the signals. If the reference signal has various peaks, the one 
    chosen is the peak which is closer to the middle of the signal, and if the 
    other signal has more than one peak also, the chosen is the one closer to
    the reference peak signal. 
    The first signal introduced is the reference signal.
     
   
    Parameters
    ----------
    refw: array-like
      the input reference signal.
    w: array-like
      the input signal.

    Returns
    -------
    al: int
      the difference between the two events position
        
    Example
    -------
    >>> peakAlign([5,7,3,20,13,5,7],[5,1,8,4,3,10,3])
    1
    
    See also: maxAlign(), minAlign(), peakNegAlign(), infMaxAlign(), infMinAlign()
    """ 
    
    p_mw = array ( peaks(array(refw),min(refw)) )
    p_w = array ( peaks(array(w),min(w)) )
    
         
    if (len(p_mw)>1):      
        min_al = argmin(abs( (len(refw)/2) - p_mw))       #to choose the peak closer to the middle of the signal  
        p_mw=p_mw[min_al]  
    if (list(p_w) == [] ):
        p_w = p_mw
    elif (len(p_w)>1):        
        min_al = argmin(abs(p_w - p_mw))       #to choose the peak closer to the peak of the reference signal
        p_w=p_w[min_al]
          
    
    return int(array(p_mw-p_w))


def peakNegAlign(refw,w):
    """ Difference between the minimum peak positions of the signals.
    
    This function returns the difference, in samples, between the minimum peaks 
    position of the signals. If the reference signal has various peaks, the one 
    chosen is the peak which is closer to the middle of the signal, and if the 
    other signal has more than one peak also, the chosen is the one closer to
    the reference peak signal. 
    The first signal introduced is the reference signal.
     
   
    Parameters
    ----------
    refw: array-like
      the input reference signal.
    w: array-like
      the input signal.

    Returns
    -------
    al: int
      the difference between the two events position
        
    Example
    -------
    >>> peakNegAlign([5,7,3,20,13,5,7],[5,1,8,4,3,10,3])
    1
    
    See also: maxAlign(), minAlign(), peakAlign(), infMaxAlign(), infMinAlign()
    """ 
    
    p_mw = array ( peaks(-array(refw),min(-array(refw)) ) )
    p_w = array ( peaks(-array(w),min(-array(w)) ) )
           
    if (len(p_mw)>1):      
        min_al = argmin(abs( (len(refw)/2) - p_mw))     #to choose the peak closer to the middle of the signal  
        p_mw=p_mw[min_al]
   
    if (list(p_w) == [] ):
        p_w = p_mw
    elif (len(p_w)>1):        
        min_al = argmin(abs(p_w - p_mw))    #to choose the peak closer to the peak of the reference signal
        p_w=p_w[min_al]
          
    return int(array(p_mw-p_w))


def infMaxAlign(refw,w):
    """ Difference between the maximum peak positions of the signal's derivative
    
    This function returns the difference, in samples, between the maximum peaks 
    position of the derivative signal.
    The first signal introduced is the reference signal.
     
   
    Parameters
    ----------
    refw: array-like
      the input reference signal.
    w: array-like
      the input signal.

    Returns
    -------
    al: int
      the difference between the two events position
    
    Example
    -------
    >>> infMaxAlign([97,87,45,65,34],[57,10,84,93,32])
    1
    
    See also: maxAlign(), minAlign(), peakAlign(), peakNegAlign(), 
    infMinAlign()
    """ 
    
    return argmax(diff(refw))-argmax(diff(w))


def infMinAlign(refw,w):
    """ Difference between the minimum peak positions of the signal's derivative
    
    This function returns the difference, in samples, between the minimum peaks 
    position of the derivative signal.
    The first signal introduced is the reference signal.
     
   
    Parameters
    ----------
    refw: array-like
      the input reference signal.
    w: array-like
      the input signal.

    Returns
    -------
    al: int
      the difference between the two events position
    
    Example
    -------
    >>> infMinAlign([67,87,45,65,34],[57,63,84,12,32])
    -1
    
    See also: maxAlign(), minAlign(), peakAlign(), peakNegAlign(), 
    infMaxAlign()
    """ 
    
    return argmin(diff(refw))-argmin(diff(w))

