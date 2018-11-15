import numpy
import os
import matplotlib.pyplot as plt
from sklearn.utils.testing import assert_array_almost_equal, \
assert_true, assert_less
import novainstrumentation

from novainstrumentation.waves import stdwave
from novainstrumentation.waves import waves
base_dir = os.path.dirname(novainstrumentation.__file__)

def test_stdwaves(show_graph = 0):
    fname = base_dir + '/code/data/xyzcal.txt'
    t, xcal, ycal, zcal = numpy.loadtxt(fname)

    if show_graph == 1:
        plt.plot(t, xcal, 'r-', t, ycal, 'b-', t, zcal, 'k-')
        plt.show()

    test_matrix = numpy.vstack([t, xcal, ycal, zcal]).transpose()
    reference_values = numpy.std(test_matrix,0)
    test_values = stdwave(test_matrix)

    assert_array_almost_equal(test_values, reference_values, 6 ,"\n ERROR: waves.stdwaves function not working properly")

def test_waves():
    t, s = numpy.loadtxt(base_dir + '/code/data/cleanecg.txt')
    test_matrix = numpy.array([20, 40, 87, 107, 156, 175, 225, 244, 291, 311, 355, 375, 418, 438, 482,
                501, 550, 569, 624, 644, 694, 713, 764, 784, 834, 854, 905, 925, 978])
    x = waves(s,  test_matrix, -10, 100)
    plt.plot(x[0,:])
    plt.show()

test_waves()

