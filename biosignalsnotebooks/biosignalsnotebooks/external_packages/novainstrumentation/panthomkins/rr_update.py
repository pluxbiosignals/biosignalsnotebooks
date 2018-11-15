import numpy as np


def rr_1_update(rr_1, NFound, Found):
    if np.logical_and(NFound <= 7, NFound > 0):
        rr_1[0:NFound - 1] = np.ediff1d(Found[0:NFound, 0])
    elif NFound > 7:
        rr_1 = np.ediff1d((Found[NFound - 7:NFound - 1, 0]))

    rr_average_1 = np.mean(rr_1)

    return rr_1, rr_average_1


def rr_2_update(rr_2, NFound, Found, rr_low_limit, rr_high_limit):
    if NFound > 0:
        delta = np.ediff1d(Found[NFound - 1:NFound, 0])
        if np.logical_and(delta >= rr_low_limit, delta <= rr_high_limit):
            pos = np.mod(NFound, 7)
            if (pos == 0):
                rr_2[7] = delta
            else:
                rr_2[pos] = delta
        rr_average_2 = np.mean(rr_2)
        rr_low_limit = 0.92 * rr_average_2
        rr_high_limit = 1.16 * rr_average_2
        rr_missed_limit = 1.66 * rr_average_2
        flag = 0

        if delta > rr_missed_limit:
            flag = 1
    else:
        rr_average_2 = np.mean(rr_2)
        flag = 0

    return rr_2, rr_average_2, flag, rr_low_limit, rr_high_limit


def sync(Found, NFound, ecg, N):
    R = np.ones(NFound, dtype=int)

    for ii in range(0, NFound):
        xtemp = Found[ii, 0]

        if (xtemp - 60 > 0):
            indInf = xtemp - 60
        else:
            indInf = 0

        if (xtemp + 60 < N):
            indSup = xtemp + 60
        else:
            indSup = N

        ind = range(int(indInf), int(indSup))

        xlook = ecg[ind]
        R[ii] = indInf + np.where(xlook == max(ecg[ind]))[0][0]

    return R
