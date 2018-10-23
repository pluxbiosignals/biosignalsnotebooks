"""
    File that contains the Python code to be executed in "signal_samples" Notebook.
"""


IMPORT_CODE = """
import biosignalsnotebooks as ost
import numpy

# Base packages used in OpenSignals Tools Notebooks for plotting data
from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models.tools import *
output_notebook(hide_banner=True)
"""

PLOTS_SIGNAL_SAMPLES = """\
signal_dict, file_header = ost.load(signal_samples_dir + file, get_header=True)
mac_addresses = list(signal_dict.keys())

mac_0 = mac_addresses[0]
chn_0 = list(signal_dict[mac_0].keys())[0]
sample_rate = file_header[mac_0]["sampling rate"]
time = numpy.linspace(0, len(signal_dict[mac_0][chn_0]) / sample_rate,
                      len(signal_dict[mac_0][chn_0]))
grid_layout = []
for mac in mac_addresses:
    channels = list(signal_dict[mac].keys())
    for chn in channels:
        fig = figure(x_axis_label='Time (s)', y_axis_label='Raw Data',
                     title=mac + "@" + chn, **ost.opensignals_kwargs("figure"))
        fig.line(time, signal_dict[mac][chn],
                 **ost.opensignals_kwargs("line"))
        grid_layout.append([fig])
ost.opensignals_style([item for sublist in grid_layout for item in sublist])
grid_plot = gridplot(grid_layout, **ost.opensignals_kwargs("gridplot"))
show(grid_plot)"""

# 21/09/2018 16h57m :)
