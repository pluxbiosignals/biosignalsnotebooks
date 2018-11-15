import numpy as np

def wavedistance(meanwave,waves,fdistance):
    
    return np.array([fdistance(wave,meanwave) for wave in waves])