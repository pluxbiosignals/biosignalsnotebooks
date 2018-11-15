from pylab import *
from numpy import *

from novainstrumentation.waves.waves import waves
from novainstrumentation.waves.meanwave import meanwave

def plotheatmap( signal, events,lmin=0,lmax=0,dt=0.01,color='r'):

    w=waves(signal, events, lmin, lmax)
    w_=meanwave(w)
   # ws_=stdwave(w)
    t_=(arange(len(w_))+lmin)*dt
    
    for iw in w:
        plot(t_,iw,lw=3,alpha=.15,color=color) 

    plot(t_,w_,lw=2,color='k')
    #plot(t_,w_+ws_,lw=0.5,color='k',ls='--')
    #plot(t_,w_-ws_,lw=0.5,color='k',ls='--')
