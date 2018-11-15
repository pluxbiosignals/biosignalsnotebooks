
from numpy import *

def computemeanwave(signal, events, fdist, lmin=0,lmax=0):
# Output: Array with mean wave, standard deviation and distance to the mean wave 
#    acordding to fdist  

    if (lmin==0) & (lmax==0):
        lmax=mean(diff(events))/2
        lmin=-lmax
    w=waves(signal, events, lmin, lmax)
    w_=meanwave(w)
    d=wavedistance(w_,w,fdist)
    ws=stdwave(w)
    
    return (w_, ws, d)