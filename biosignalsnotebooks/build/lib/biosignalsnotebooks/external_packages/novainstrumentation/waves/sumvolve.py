from numpy import *

def sumvolve(x,window):
    lw=len(window)
    res=zeros(len(x)-lw,'d')
    for i in range(len(x)-lw):
        res[i]=sum(abs(x[i:i+lw]-window))/float(lw)
        #res[i]=sum(abs(x[i:i+lw]*window))
    return res
