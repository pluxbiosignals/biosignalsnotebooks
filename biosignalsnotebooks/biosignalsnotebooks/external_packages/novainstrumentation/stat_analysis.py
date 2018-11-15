# -*- coding: utf-8 -*-

import numpy as np
from scipy.stats import gaussian_kde


def scott_density(signal):
    #Based on seaborn 0.4
    s_k = np.asarray(signal, np.float)
    bw, widths, gridsize, cut = 'scott', .8, 100, 3 
    kde = gaussian_kde(s_k, bw)
    if isinstance(bw, str):
        bw = 'scotts' if bw == 'scott' else bw
        bw = getattr(kde, '%s_factor' % bw)()
    support_min = max(min(s_k) - bw * cut, -np.inf)
    support_max = min(max(s_k) + bw * cut,  np.inf)
    y = np.linspace(support_min, support_max, gridsize)
    dens = kde.evaluate(y)
    scl = 1 / (dens.max() / (widths / 2))
    dens *= scl

    return dens, y


def matrix_recurrence(signal):  
    N = len(signal)
    S = np.ones((N,N))
    for j in np.arange(N):
        for i in np.arange(N):
            ij = abs(signal[j]-signal[i])
            if ij <= 0.1*np.std(signal):
                S[i,j] = 0
    
    return S