import time


def tic():
    """@brief Saves the current time.
    @see also tac()
    """

    global _tic
    _tic = time.time()


def tac(label=''):
    """@brief This function prints in the screen the difference between
    the time saved with function tic.py and current time.

    @param label String: if something is desired to print (default = '').

    @see also tic()
    """

    global _tic

    delta_t = time.time() - _tic

    if label != '':
        print('%s - %3.4f s' % (label, delta_t))
    else:
        print('%3.4f s' % delta_t)
