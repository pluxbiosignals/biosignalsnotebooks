import os
import numpy


import novainstrumentation

from novainstrumentation import load_with_cache

from sklearn.utils.testing import assert_array_almost_equal, \
assert_true, assert_less
# assert_almost_equal, assert_array_equal, assert_equal


base_dir = os.path.dirname(novainstrumentation.__file__)


def test_load_with_cache():
    fname = base_dir + '/code/data/bvp.txt'
    fname_npy = fname + '.npy'

    direct_d = numpy.loadtxt(fname)

    cache_d = load_with_cache(fname, data_type='float')

    #Check that the data was correctly read
    assert_array_almost_equal(direct_d, cache_d, decimal=5)

    #Guarantee that the file was created
    assert_true(os.path.exists(fname_npy))

    #The file should be smaller that the original
    assert_less(os.path.getsize(fname_npy), os.path.getsize(fname))

    os.remove(fname_npy)


def test_fail():
    assert False
