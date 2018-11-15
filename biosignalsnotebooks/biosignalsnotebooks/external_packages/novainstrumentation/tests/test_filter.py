import os
import numpy


import novainstrumentation
import novainstrumentation as ni

from scipy import signal

from sklearn.utils.testing import assert_array_almost_equal, \
assert_true, assert_less
# assert_almost_equal, assert_array_equal, assert_equal


base_dir = os.path.dirname(novainstrumentation.__file__)

def test_emg_filter_params():
    fname = base_dir + '/code/data/emg.txt'

    t, emg = numpy.loadtxt(fname)
    env_ni = ni.lowpass(abs(emg), order=2, f=10,fs=1000)

    b,a = signal.butter(2,Wn=10/(1000.0/2.0))
    env_ref = signal.lfilter(b,a,abs(emg))

    assert_array_almost_equal(env_ni,env_ref)


def test_emg_filter_values():
    f_name = base_dir + '/code/data/emg.txt'

    t, emg = numpy.loadtxt(f_name)
    env_ni = ni.lowpass(abs(emg),order=2,f=10,fs=1000.)

    b,a = signal.butter(2,Wn=10/(1000.0/2.0))
    env_ref = signal.lfilter(b,a,abs(emg))

    assert_array_almost_equal(env_ni,env_ref)


#def test_fail():
#    assert False
