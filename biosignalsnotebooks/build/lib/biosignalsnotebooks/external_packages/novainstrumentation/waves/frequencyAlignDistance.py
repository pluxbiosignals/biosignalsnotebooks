from numpy import *
import numpy as np
from scipy import interpolate
from pylab import *

def frequencyAlignDistance(f1,w1,f2,w2):
    
    w1=smooth(w1)
    w2=smooth(w2)
    
#    return msedistance(w2[:100],w1[:100])
    
    m1=argmax(w1)
    m2=argmax(w2)
    
    f1=f1/float(f1[m1])
    f2=f2/float(f2[m2])
    
    w1=w1/w1[m1]
    w2=w2/w2[m2]
    
#    plot(f1,w1)
#    plot(f2,w2)
    
    nf=f1[3:103]
        
    f_interp_w2=interpolate.interp1d(f2,w2)
    
    iw2=f_interp_w2(nf)
    
    plot(nf,iw2)
    plot(nf,w1[3:103])
    
    s2=iw2
    s1=w1[3:103]
    
    r=np.sqrt(np.sum(((s1-s2)**2)/s1 ))
    
    return r
    
#    return msedistance(iw2,w1[3:103])