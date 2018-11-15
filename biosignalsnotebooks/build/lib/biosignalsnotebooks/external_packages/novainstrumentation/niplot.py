from pylab import axis, draw, close, gcf, gca


def zoom(event):
    ax = gca()
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    # edit the scale if needed
    base_scale = 1.1

    xdata = event.xdata     # get event x location
    ydata = event.ydata     # get event y location

    # performs a prior check in order to not exceed figure margins
    if xdata != None and ydata != None:
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

        ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
        ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
        ax.figure.canvas.draw()

    return zoom


def on_key_press(event):

    # keyboard zoom-in
    if event.key == '+':
        a = axis()
        w = a[1] - a[0]
        axis([a[0] + w * .2, a[1] - w * .2, a[2], a[3]])
        draw()

    # keyboard zoom-out
    if event.key in ['-', '\'']:
        a = axis()
        w = a[1] - a[0]
        axis([a[0] - w / 3.0, a[1] + w / 3.0, a[2], a[3]])
        draw()

    # right displacement
    if event.key in ['.', 'right']:
        a = axis()
        w = a[1] - a[0]
        axis([a[0] + w * .2, a[1] + w * .2, a[2], a[3]])
        draw()

    # left displacement
    if event.key in [',', 'left']:
        a = axis()
        w = a[1] - a[0]
        axis([a[0] - w * .2, a[1] - w * .2, a[2], a[3]])
        draw()

    # up displacement
    if event.key == 'up':
        a = axis()
        w = a[3] - a[2]
        axis([a[0], a[1], a[2] + w * .2, a[3] + w * .2])
        draw()

    # down displacement
    if event.key == 'down':
        a = axis()
        w = a[3] - a[2]
        axis([a[0], a[1], a[2] - w * .2, a[3] - w * .2])
        draw()

    # close figure
    if event.key == 'q':
        close()
        # NOTE: We should make the disconnect (mpl_disconect(cid)
        # But since the figure is destroyed we may keep this format
        # if implemented the mpl_connect should use the return cid

    # print('you pressed', event.key, event.xdata, event.ydata)
    # TODO: Reset zoom with an initial default value -> suggest 'r' key


def on_key_release(event):
    # print('you released', event.key, event.xdata, event.ydata)
    pass


def niplot():
    """
    This script extends the native matplolib keyboard bindings.
    This script allows to use the `up`, `down`, `left`, and `right` keys
    to move the visualization window. Zooming can be performed using the `+`
    and `-` keys. Finally, the scroll wheel can be used to zoom under cursor.

    Returns
    -------

    """
    fig = gcf()
    cid = fig.canvas.mpl_connect('key_press_event',  # @UnusedVariable
                                 on_key_press)
    cid = fig.canvas.mpl_connect('key_release_event',  # @UnusedVariable
                                 on_key_release)
    cid = fig.canvas.mpl_connect('scroll_event', zoom)

