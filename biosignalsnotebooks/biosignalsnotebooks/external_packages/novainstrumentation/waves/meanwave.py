from numpy import mean

def meanwave(signals):
    """ This function computes the meanwave of various signals.
    
    Given a set of signals, with the same number of samples, this function 
    returns an array representative of the meanwave of those signals - which is
    a wave computed with the mean values of each signal's samples. 
    
    Parameters
    ----------
    signals: matrix-like
      the input signals.

    Returns
    -------
    mw: array-like
      the resulted meanwave  
    """
    
    return mean(signals,0)
