
def plotheatmap2(s,valmin,valmax,points=100):
    
    import numpy as np
    import matplotlib.cm as cm
    import matplotlib.mlab as mlab
    import matplotlib.pylab as plt

    x = range(1,len(s))
    y = np.linspace(valmin, valmax, points)
    X, Y = np.meshgrid(x, y)
    Z = mlab.bivariate_normal(X, Y)*0.0

    for i in range(len(s)):
        Z1 = mlab.bivariate_normal(X, Y, 3.0, 3.0, i, s[i])
        Z=Z1+Z

    im = plt.imshow(Z, interpolation='bilinear', cmap=cm.gray,
                origin='lower')
#extent=[-3,3,-3,3])
    return Z