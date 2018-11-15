import os
from numpy import array, loadtxt
from novainstrumentation import peaks, peakdelta
from numpy.testing import TestCase, assert_array_equal, run_module_suite

path = '..' + os.path.sep + 'data' + os.path.sep


class TestPeaks(TestCase):

    def test_peaks_cleanecg(self):
        t, s = loadtxt(path + 'cleanecg.txt')
        pr = array([20,  87, 156, 225, 291, 355, 418, 482, 550, 624, 694, 764, 834, 905, 978])
        assert_array_equal(pr, peaks(s, 75))

    def test_peaks_eda(self):
        t, s = loadtxt(path + 'eda.txt')
        pr = array([95, 146, 346])
        assert_array_equal(pr, peaks(s, 600))


class TestPeakdelta(TestCase):
    def test_peakdelta_cleanecg(self):
        t, s = loadtxt(path + 'cleanecg.txt')
        pr = array([20, 40, 87, 107, 156, 175, 225, 244, 291, 311, 355, 375, 418, 438, 482,
                    501, 550, 569, 624, 644, 694, 713, 764, 784, 834, 854, 905, 925, 978])
        assert_array_equal(pr, peakdelta(s, 50)[0][:, 0].astype(int))

    def test_peakdelta_eda(self):
        t, s = loadtxt(path + 'eda.txt')
        pks = peakdelta(s, 50)

        prmax = array([0, 95, 278, 346])
        prmin = array([47, 255, 313])

        assert_array_equal(prmax, pks[0][:, 0].astype(int))
        assert_array_equal(prmin, pks[1][:, 0].astype(int))

if __name__ == "__main__":
    run_module_suite()
