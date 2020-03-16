
"""
List of functions intended to support the Jupyter Notebooks, encapsulating code that the user
don't need to access in a normal view.

Set of functions invoked in OpenSignals Tools Notebooks to present some graphical results.
These function are only designed for a single end, but we made them available to the user if he
want to explore graphical functionalities with practical examples.

Bokeh is the base package of this module, ensuring an interactive and attractive data plotting
integrable in web pages and applications like our Jupyter Notebooks.

Available Functions
-------------------
[Public]

css_style_apply
    Function that apply the css configurations to the Jupyter Notebook pages.
plot_compare_act_config
    With this function is generated a gridplot showing the differences in muscular activation
    detection results when the input arguments of detect_emg_activations function are changed.
plot_median_freq_evol
    Representation of a plot that shows the median power frequency evolution time series of
    an acquired EMG signal.
plot_sample_rate_compare
    Gridplot showing differences in ECG signal morphology as a consequence of changing the
    acquisition sampling rate.
acquire_subsamples_gp1 [Old Version]
    Graphical function that shows the differences in ECG signals accordingly to the chosen
    sampling rate.
plot_resp_slow
    Function invoked in order to present the RIP signal together the rectangular signal that
    identifies the inhalation and exhalation stages.
plot_resp_diff
    Similar do plot_resp_slow but in this particular case is presented the 1st derivative of RIP
    signal instead of the orignal acquired data.


Available Functions
-------------------
[Private]

_inhal_exhal_segments
    Auxiliary function for determination of the RIP sensor samples where inhalation and exhalation
    periods start and end.

Observations/Comments
---------------------
None

/\
"""

from os.path import exists as pathexist

import numpy
import requests
import math
import os
import scipy.integrate as integrate
# import novainstrumentation as ni
from .process import smooth, plotfft, lowpass
from .visualise import plot, opensignals_kwargs, opensignals_color_pallet, opensignals_style, dispersion
from .detect import detect_emg_activations
from .aux_functions import _generate_bokeh_file
from IPython.core.display import HTML
from bokeh.plotting import figure, show, save
from bokeh.models.annotations import Title
from bokeh.io import output_notebook
from bokeh.layouts import gridplot, layout
from bokeh.models import BoxAnnotation, Arrow, VeeHead, Range1d, LinearAxis
output_notebook(hide_banner=True)


def css_style_apply():
    """
    -----
    Brief
    -----
    Function that apply the css configurations to the Jupyter Notebook pages.

    -----------
    Description
    -----------
    Taking into consideration that, ultimately, biosignalsnotebooks Jupyter Notebooks are web pages,
    then a CSS file with the style options for customization of biosignalsnotebooks environment become
    particularly important.

    With CSS, the Jupyter Notebook template can be adapted in order to acquire the opensignals
    format, by changing background color, color pallet, font style...

    This function simply injects an HTML statement containing the style configurations.

    Returns
    -------
    out : IPython.core.display.HTML
        An IPython object that contains style information to be applied in the web page.

    """

    path = "styles/theme_style.css"
    if pathexist(path):
        style = open(path, "r").read()
    else:
        style = open("../../" + path, "r").read()

    print(".................... CSS Style Applied to Jupyter Notebook .........................")
    return HTML("<div id='style_import'>" + style + "</div>")


# /////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////// Plotting Auxiliary Functions //////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////

# =================================================================================================
# =================================== Acquire Category ============================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%% sampling_rate_and_aliasing.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_sample_rate_compare(data_dict, file_name=None):
    """
    -----
    Brief
    -----
    Is a plotting function that shows a sequence of ECG plots, demonstrating the relevance of
    choosing a wright sampling rate.

    -----------
    Description
    -----------
    Function intended to generate a Bokeh figure with Nx2 format, being N the number of keys of
    'data_dict' - one for each sampling rate (10, 100, 1000 Hz).

    At the first column is plotted a 10 seconds segment of the ECG signal at a specific
    sampling rate, while in the second column it will be presented a zoomed section of the ECG
    signal with 1 second, in order to the see the effect of choosing a specific sampling rate.

    Applied in the Notebook titled "Problems of a smaller sampling rate (aliasing)".

    ----------
    Parameters
    ----------
    data_dict : dict
        Dictionary that contains the data to be plotted
        ({"<sampling_rate_1>": {"time": <time_axis_1>, "data": <data_1>},
          "<sampling_rate_2>": {"time": <time_axis_2>, "data": <data_2>},
          ...})

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    """

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    nbr_rows = len(list(data_dict.keys()))

    # List that store the figure handler.
    list_figures = plot([[]] * nbr_rows * 2, [[]] * nbr_rows * 2, y_axis_label="Raw Data",
                        x_axis_label="Time (s)", grid_lines=nbr_rows, grid_columns=2,
                        grid_plot=True, get_fig_list=True, show_plot=False)

    # Generation of Bokeh Figures.
    grid_list = []
    for iter, sample_rate in enumerate(list(data_dict.keys())):
        # List of figures in a valid gridplot format (each entry will define a row and each
        # subentry a column of the gridplot)
        grid_list += [[]]

        # Plotting of 10 seconds segment.
        # [Figure tile]
        title_unzoom = Title()
        title_unzoom.text = 'Sampling Rate: ' + sample_rate + " Hz"
        list_figures[2 * iter].title = title_unzoom

        # [Plot generation]
        list_figures[2 * iter].line(data_dict[sample_rate]["time"][:10 * int(sample_rate)],
                                    data_dict[sample_rate]["data"][:10 * int(sample_rate)],
                                    **opensignals_kwargs("line"))

        # Storage of customized figure.
        grid_list[-1] += [list_figures[2 * iter]]

        # Plotting of a zoomed section with 1 second.
        # [Figure tile]
        title_zoom = Title()
        title_zoom.text = 'Zoomed section @ ' + sample_rate + " Hz"
        list_figures[2 * iter + 1].title = title_zoom

        # [Plot generation]
        list_figures[2 * iter + 1].line(data_dict[sample_rate]["time"][:int(sample_rate)],
                                        data_dict[sample_rate]["data"][:int(sample_rate)],
                                        **opensignals_kwargs("line"))

        # Storage of customized figure.
        grid_list[-1] += [list_figures[2 * iter + 1]]

    # Organisation of figures in a gridplot.
    grid_plot_1 = gridplot(grid_list, **opensignals_kwargs("gridplot"))

    # Show representations.
    show(grid_plot_1)
    #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')

# [Old Version to be removed]
def acquire_subsamples_gp1(input_data, file_name=None):
    """
    Function invoked for plotting a grid-plot with 3x2 format, showing the differences in ECG
    signals accordingly to the chosen sampling frequency.

    Applied in the cell with tag "subsampling_grid_plot_1".

    ----------
    Parameters
    ----------
    input_data : dict
        Dictionary with ECG signal to present.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.
    """

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    # Number of acquired samples (Original sample_rate = 4000 Hz)
    fs_orig = 4000
    nbr_samples_orig = len(input_data)
    data_interp = {"4000": {}}
    data_interp["4000"]["data"] = input_data
    data_interp["4000"]["time"] = numpy.linspace(0, nbr_samples_orig / fs_orig, nbr_samples_orig)

    # Constants
    time_orig = data_interp["4000"]["time"]
    data_orig = data_interp["4000"]["data"]

    # ============ Interpolation of data accordingly to the desired sampling frequency ============
    # sample_rate in [3000, 1000, 500, 200, 100] - Some of the available sample frequencies at PLUX
    # acquisition systems
    # sample_rate in [50, 20] - Non-functional sampling frequencies (Not available at PLUX devices
    # because of their limited application)
    for sample_rate in [3000, 1000, 500, 200, 100, 50, 20]:
        fs_str = str(sample_rate)
        nbr_samples_interp = int((nbr_samples_orig * sample_rate) / fs_orig)
        data_interp[fs_str] = {}
        data_interp[fs_str]["time"] = numpy.linspace(0, nbr_samples_orig / fs_orig,
                                                     nbr_samples_interp)
        data_interp[fs_str]["data"] = numpy.interp(data_interp[fs_str]["time"], time_orig,
                                                   data_orig)

    # List that store the figure handler.
    list_figures = []

    # Generation of Bokeh Figures.
    for iter_nbr, sample_rate in enumerate(["4000", "3000", "1000", "500", "200", "100"]):
        # If figure number is a multiple of 3 or if we are generating the first figure...
        if iter_nbr == 0 or iter_nbr % 2 == 0:
            list_figures.append([])

        # Plotting phase.
        list_figures[-1].append(figure(x_axis_label='Time (s)', y_axis_label='Raw Data',
                                       title="Sampling Frequency: " + sample_rate + " Hz",
                                       **opensignals_kwargs("figure")))
        list_figures[-1][-1].line(data_interp[sample_rate]["time"][:int(sample_rate)],
                                  data_interp[sample_rate]["data"][:int(sample_rate)],
                                  **opensignals_kwargs("line"))

# =================================================================================================
# ==================================== Detect Category ============================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% r_peaks.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_ecg_pan_tompkins_steps(time, orig_ecg, pre_process_ecg, sampling_rate, titles):
    """
    -----
    Brief
    -----
    With this plotting function it will be possible to plot simultaneously (in pairs) "Original"/
    "Filtered"/"Differentiated"/"Rectified"/"Integrated" ECG signals used at "Pan-Tompkins R Peaks
    Detection Algorithm".

    -----------
    Description
    -----------
    Function intended to generate a Bokeh figure with 1x2 format, being 1 the of rows and 2 the number
    of columns.

    At the first column is plotted the ECG signal resulting from pre-process step i while in the second
    column it is presented the ECG signal resulting from pre-process step i+1.

    Applied in the Notebook titled "Event Detection - R Peaks (ECG)".

    ----------
    Parameters
    ----------
    time : list
        List containing the time-axis sequence of values.

    orig_ecg : list
        Sequence of sampled values (Original ECG).

    pre_process_ecg : list
        Sequence of sampled values (Pre-Processed ECG).

    sampling_rate : int
        Acquisition sampling rate (Hz)

    titles : list
        List containing the title of each subplot.

    """

    if len(titles) == 2:
        # Representation of the output of Step 1 of Pan-Tompkins R-Peak Detection Algorithm.
        # List that store the figure handler
        list_figures_1 = [[]]

        # Plotting of Original Signal
        list_figures_1[-1].append(figure(x_axis_label='Time (s)', y_axis_label='Raw Data',
                                         title=titles[0], **opensignals_kwargs("figure")))
        list_figures_1[-1][-1].line(time[:sampling_rate], orig_ecg[:sampling_rate], **opensignals_kwargs("line"))

        # Plotting of Filtered Signal
        list_figures_1[-1].append(figure(x_axis_label='Time (s)', y_axis_label='Raw Data',
                                         title=titles[1], **opensignals_kwargs("figure")))
        list_figures_1[-1][-1].line(time[:sampling_rate], pre_process_ecg[:sampling_rate], **opensignals_kwargs("line"))

        # Grid-Plot.
        opensignals_style([item for sublist in list_figures_1 for item in sublist])
        grid_plot_1 = gridplot(list_figures_1, **opensignals_kwargs("gridplot"))
        show(grid_plot_1)
    else:
        raise RuntimeError("The field 'title' must be a list of strings with size 2 !")


def plot_ecg_pan_tompkins_peaks(time, orig_ecg, integrated_ecg, sampling_rate, possible_peaks,
                                probable_peaks, definitive_peaks):
    """
    -----
    Brief
    -----
    With this plotting function it will be possible to demonstrate which "peaks" are being
    detected in each stage of Pan-Tompkins Algorithm (possible, probable, definitive).

    -----------
    Description
    -----------
    Function intended to generate a Bokeh figure containing all peaks detected in a temporal
    segment (of ECG integrated signal) with 2 seconds.

    "Possible Peaks" are marked with the smallest circle while "Probable Peaks" and "Definitive
    Peaks" are highlighted with medium and large size circles.

    Applied in the Notebook titled "Event Detection - R Peaks (ECG)".

    ----------
    Parameters
    ----------
    time : list
        List containing the time-axis sequence of values.

    orig_ecg : list
        Sequence of sampled values (Original ECG).

    integrated_ecg : list
        Sequence of sampled values (Integrated ECG).

    sampling_rate : int
        Acquisition sampling rate (Hz)

    possible_peaks : list
        List containing all "Possible Peaks" detected from Pan-Tompkins R Peak Detection
        Algorithm.

    probable_peaks : list
        List containing all "Probable Peaks" detected from Pan-Tompkins R Peak Detection
        Algorithm.

    definitive_peaks : list
        List containing all "Definitive Peaks" detected from Pan-Tompkins R Peak Detection
        Algorithm.
    """

    # List that store the figure handler
    list_figures = []

    # Plotting of a signal segment with 2 seconds
    segment_data = numpy.array(orig_ecg[:2 * sampling_rate])
    segment_int = numpy.array(integrated_ecg[:2 * sampling_rate])
    segment_time = numpy.array(time[:2 * sampling_rate])

    # Peaks list for the 2 seconds window
    possible_peaks_wind = numpy.array(possible_peaks)[numpy.array(possible_peaks) < len(segment_int)]
    probable_peaks_wind = numpy.array(probable_peaks)[numpy.array(probable_peaks) < len(segment_int)]
    definitive_peaks_wind = numpy.array(definitive_peaks)[numpy.array(definitive_peaks) < len(segment_int)]

    list_figures.append(figure(x_axis_label='Time (s)', y_axis_label='Raw Data', **opensignals_kwargs("figure")))
    list_figures[-1].line(segment_time, segment_int, **opensignals_kwargs("line"))
    list_figures[-1].circle(segment_time[definitive_peaks_wind], segment_int[definitive_peaks_wind], size=30, color="#00893E", legend_label="Definitive Peaks")
    list_figures[-1].circle(segment_time[probable_peaks_wind], segment_int[probable_peaks_wind], size=20, color="#009EE3", legend_label="Probable Peaks")
    list_figures[-1].circle(segment_time[possible_peaks_wind], segment_int[possible_peaks_wind], size=10, color="#302683", legend_label="Possible Peaks")

    # Show figure.
    opensignals_style(list_figures)
    show(list_figures[-1])


# =================================================================================================
# ==================================== Extract Category ===========================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% emg_parameters.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_emg_graphical_durations(max_time, min_time, avg_time, std_time):
    """
    -----
    Brief
    -----
    This plotting function ensures a graphical representation of maximum, minimum and average time
    durations of the muscular activation periods.

    -----------
    Description
    -----------
    Function intended to generate a single Bokeh figure graphically describing and identifying
    some statistical parameters related with the time duration of the muscular activation periods
    that compose the input EMG signal.

    Applied in the Notebook titled "EMG Analysis - Time and Frequency Parameters".

    ----------
    Parameters
    ----------
    max_time : float
        Time duration of the longest EMG muscular activation.

    min_time : float
        Time duration of the shortest EMG muscular activation.

    avg_time : float
        Average time duration of the EMG muscular activation set.

    std_time : int
        Standard deviation of the muscular activation time duration relatively to avg_time.
    """

    # List that store the figure handler
    list_figures_1 = []
    color_1 = "#009EE3"
    color_2 = "#00893E"
    color_3 = "#E84D0E"
    color_4 = "#CF0272"

    # Plotting of Burst duration distribution
    list_figures_1.append(figure(x_axis_label='Time (s)', **opensignals_kwargs("figure"), x_range=[0, max_time], y_range=[0, 1]))
    box_annotation_max = BoxAnnotation(left=0, right=max_time, top=0.33, bottom=0, fill_color=color_1, fill_alpha=0.5)
    list_figures_1[-1].rect(0, 0, width=0, height=0, fill_color=color_1, fill_alpha=0.5, legend_label="Maximum Burst Time")
    list_figures_1[-1].add_layout(box_annotation_max)

    box_annotation_avg = BoxAnnotation(left=0, right=avg_time, top=0.66, bottom=0.33, fill_color=color_2, fill_alpha=0.5)
    list_figures_1[-1].rect(0, 0, width=0, height=0, fill_color=color_2, fill_alpha=0.5, legend_label="Average Burst Time")
    list_figures_1[-1].add_layout(box_annotation_avg)

    box_annotation_min = BoxAnnotation(left=0, right=min_time, top=1, bottom=0.66, fill_color=color_3, fill_alpha=0.5)
    list_figures_1[-1].rect(0, 0, width=0, height=0, fill_color=color_3, fill_alpha=0.5, legend_label="Minimum Burst Time")
    list_figures_1[-1].add_layout(box_annotation_min)

    box_annotation_std = BoxAnnotation(left=avg_time, right=avg_time + std_time, top=0.55, bottom=0.44, fill_color=color_4, fill_alpha=0.5)
    list_figures_1[-1].rect(0, 0, width=0, height=0, fill_color=color_4, fill_alpha=0.5, legend_label="Average + Standard Deviation Time")
    list_figures_1[-1].add_layout(box_annotation_std)

    # Show figure.
    opensignals_style(list_figures_1)
    show(list_figures_1[-1])


def plot_emg_graphical_statistical(time, signal, max_sample_value, min_sample_value, avg_sample_value,
                                   std_sample_value, y_range=[-1.10, 1]):
    """
    -----
    Brief
    -----
    This plotting function ensures a graphical representation of maximum, minimum and average sample
    values registered on the entire EMG acquisition.

    -----------
    Description
    -----------
    Function intended to generate a single Bokeh figure with graphically describing and identifying
    some statistical parameters extracted from the analysis of the entire electromyographic (EMG) signal.

    Applied in the Notebook titled "EMG Analysis - Time and Frequency Parameters".

    ----------
    Parameters
    ----------
    time : list
        Time-axis linked to the acquired EMG signal samples.

    signal : list
        Acquired EMG signal samples.

    max_sample_value : float
        Maximum value registered in the acquired EMG samples.

    min_sample_value: float
        Minimum value registered in the acquired EMG samples.

    avg_sample_value : float
        Average value registered in the acquired EMG samples.

    std_sample_value : int
        Standard deviation of the acquired EMG sample values relatively to avg_sample_value.

    y_range : list
        Two elements list defining the start and ending points of the y axis range.
    """

    # List that store the figure handler
    list_figures = []

    # Plotting of EMG.
    list_figures.append(figure(x_axis_label='Time (s)', y_axis_label='Electric Tension (mV)', x_range=(0, time[-1] + 0.50 * time[-1]), y_range=y_range, **opensignals_kwargs("figure")))
    list_figures[-1].line(time, signal, legend_label="EMG Signal", **opensignals_kwargs("line"))

    # Representation of EMG and the determined parameters
    parameter_list = ["Maximum", "Minimum", "Average", "Standard Deviation"]
    for parameter in parameter_list:
        find_time_max = numpy.array(time)[numpy.where(numpy.array(signal) == max_sample_value)]
        find_time_min = numpy.array(time)[numpy.where(numpy.array(signal) == min_sample_value)]
        if parameter == "Maximum":
            list_figures[-1].circle(find_time_max, max_sample_value, radius = 0.5, fill_color=opensignals_color_pallet(),
                                    legend_label=parameter + " EMG")
        elif parameter == "Minimum":
            list_figures[-1].circle(find_time_min, min_sample_value, radius=0.5, fill_color=opensignals_color_pallet(),
                                    legend_label=parameter + " EMG")
        elif parameter == "Average":
            list_figures[-1].line([0, time[-1]], [avg_sample_value, avg_sample_value],
                                  legend_label=parameter + " EMG Sample", **opensignals_kwargs("line"))
        elif parameter == "Standard Deviation":
            box_annotation = BoxAnnotation(left=0, right=time[-1], top=avg_sample_value + std_sample_value,
                                           bottom=avg_sample_value - std_sample_value, fill_color="black",
                                           fill_alpha=0.3)
            list_figures[-1].rect(find_time_min, std_sample_value, width=0, height=0, fill_color="black", fill_alpha=0.3,
                                  legend_label="Average + Standard Deviation Zone")
            list_figures[-1].add_layout(box_annotation)

    # Show figure.
    opensignals_style(list_figures)
    show(list_figures[-1])


def plot_emg_rms_area(time, signal, rms, area):
    """
    -----
    Brief
    -----
    With the current function it will be plotted the EMG signals together with RMS line and the time-series that
    describes the evolution of the cumulative area.

    -----------
    Description
    -----------
    Function intended to generate a single Bokeh figure graphically describing and identifying
    Root Mean Square and Area parameters extracted from the analysis of the entire electromyographic (EMG) signal.

    Applied in the Notebook titled "EMG Analysis - Time and Frequency Parameters".

    ----------
    Parameters
    ----------
    time : list
        Time-axis linked to the acquired EMG signal samples.

    signal : list
        Acquired EMG signal samples.

    rms : float
        Root Mean Square value (amplitude estimator for the EMG signal under analysis).

    area : list
        List containing the sequential cumulative values of the area under the EMG signal curve.

    """

    # List that store the figure handler
    list_figures = []

    # Plotting of EMG area and RMS line
    list_figures.append(
        figure(x_axis_label='Frequency (Hz)', y_axis_label='Electric Tension (mV)', x_range=[0, time[-1]],
               y_range=[-1, 1], **opensignals_kwargs("figure")))
    list_figures[-1].line(time, signal, **opensignals_kwargs("line"))
    list_figures[-1].line([time[0], time[-1]], [rms, rms], legend_label="RMS Value", **opensignals_kwargs("line"))

    # Setting the second y axis range name and range
    list_figures[-1].extra_y_ranges = {"Area": Range1d(start=0, end=area[-1])}

    # Adding the second axis to the plot
    list_figures[-1].add_layout(LinearAxis(y_range_name="Area", axis_label='Area (mV.s)'), 'right')
    list_figures[-1].line(time[1:], area, legend_label="Area along time (cumulative)", y_range_name="Area",
                            **opensignals_kwargs("line"))

    # Show figure.
    opensignals_style(list_figures)
    show(list_figures[-1])


def plot_emg_spect_freq(freq_axis, power_axis, max_freq, median_freq):
    """
    -----
    Brief
    -----
    A plot with frequency power spectrum of the input EMG signal is presented graphically, highlighting maximum and
    median power frequency.

    -----------
    Description
    -----------
    Function intended to generate a single Bokeh figure graphically describing and identifying maximum and median
    power frequency on Power Spectrum.

    Applied in the Notebook titled "EMG Analysis - Time and Frequency Parameters".

    ----------
    Parameters
    ----------
    freq_axis : list
        List with the values of power spectrum frequency axis.

    power_axis : list
        List with the values of power spectrum y axis (relative weight of the frequency component on signal
        reconstruction.

    max_freq : float
        Frequency value registered when the maximum power is reached on the spectrum.

    median_freq : float
        Frequency value registered when the half of the total power is reached on the cumulative power spectrum.

    """

    # List that store the figure handler
    list_figures = []

    # Plotting of EMG Power Spectrum
    list_figures.append(
        figure(x_axis_label='Frequency (Hz)', y_axis_label='Relative Power (a.u.)', **opensignals_kwargs("figure")))
    list_figures[-1].line(freq_axis, power_axis, legend_label="Power Spectrum", **opensignals_kwargs("line"))
    list_figures[-1].patch(list(freq_axis) + list(freq_axis)[::-1], list(power_axis) + list(numpy.zeros(len(power_axis))),
                           fill_color=opensignals_color_pallet(), fill_alpha=0.5, line_alpha=0,
                           legend_label="Area Under Curve")
    list_figures[-1].line([median_freq, median_freq], [0, power_axis[numpy.where(freq_axis == median_freq)[0][0]]],
                          legend_label="Median Frequency", **opensignals_kwargs("line"))
    list_figures[-1].line([max_freq, max_freq], [0, power_axis[numpy.where(freq_axis == max_freq)[0][0]]],
                          legend_label="Maximum Power Frequency", **opensignals_kwargs("line"))

    # Show figure.
    opensignals_style(list_figures)
    show(list_figures[-1])

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% eeg_extract_alphaband.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def plot_eeg_signal_wind(time, signal, time_range, time_windows_evt_1, time_windows_evt_2,
                         y_axis_label="Electric Voltage", legend=["Eyes Opened", "Eyes Closed"]):
    """
    -----
    Brief
    -----
    Function intended to generate a single Bokeh figure that presents a graphical representation of an EEG
    signal, highlighting a set of time-windows (segments).

    -----------
    Description
    -----------
    The current function was mainly created to support "eeg_extract_alphaband" Jupyter Notebook, ensuring
    a graphical representation of an EEG signal segmented into time windows (of two types: eyes opened and
    eyes closed).

    Applied in the Notebook titled "EEG - Alpha Band Extraction".

    ----------
    Parameters
    ----------
    time : list
        List containing the time-axis linked to the acquired EEG data samples.

    signal : list
        List containing the acquired data samples.

    time_range : list
        A tuple containing the start and ending times of the visualisation window (start, end).

    time_windows_evt_1 : list tuples
        Each entry of this list will contain a tuple (start, end) identifying the start and ending points
        of the temporal segment under analysis [Event 1 - Eyes Opened].

    time_windows_evt_2 : list tuples
        Each entry of this list will contain a tuple (start, end) identifying the start and ending points
        of the temporal segment under analysis [Event 2 - Eyes Closed].

    y_axis_label : str
        A string where it is specified the label of the y axis.

    legend : list
        A list of strings containing the legends of the plots.
    """

    # Retrocompatibility.
    legend_label = legend

    # Range of the visualisation window.
    x_range = (time_range[0], time_range[1])

    # Get the list of beginning and ending points of the time windows [Eyes Opened]
    eyes_open_begin = []
    eyes_open_end = []
    for tuple in time_windows_evt_1:
        eyes_open_begin.append(tuple[0])
        eyes_open_end.append(tuple[1])

    # Get the list of beginning and ending points of the time windows [Eyes Closed]
    eyes_closed_begin = []
    eyes_closed_end = []
    for tuple in time_windows_evt_2:
        eyes_closed_begin.append(tuple[0])
        eyes_closed_end.append(tuple[1])

    list_figures = plot(time, signal, y_axis_label=y_axis_label, get_fig_list=True, show_plot=False, x_range=x_range)

    # Highlighting "Eyes Opened" and "Eyes Closed" bands.
    color_open_eyes = opensignals_color_pallet()
    color_closed_eyes = opensignals_color_pallet()

    # ["Eyes Opened"]
    box_annotations = []
    for i in range(0, len(eyes_open_begin)):
        box_annotations.append(BoxAnnotation(left=eyes_open_begin[i], right=eyes_open_end[i],
                                             fill_color=color_open_eyes, fill_alpha=0.1))
        list_figures[-1].add_layout(box_annotations[-1])
    list_figures[-1].circle([-100], [0], fill_color=color_open_eyes, fill_alpha=0.1, legend_label=legend_label[0])

    if len(time_windows_evt_2) != 0:
        # ["Eyes Closed"]
        for i in range(0, len(eyes_closed_begin)):
            box_annotations.append(
                BoxAnnotation(left=eyes_closed_begin[i], right=eyes_closed_end[i], fill_color=color_closed_eyes,
                              fill_alpha=0.1))
            list_figures[-1].add_layout(box_annotations[-1])
        list_figures[-1].circle([-100], [0], fill_color=color_closed_eyes, fill_alpha=0.1, legend_label=legend_label[1])

    # Show figure.
    show(list_figures[-1])


def plot_eeg_alpha_band(freq_axis_evt1, power_axis_evt1, freq_axis_evt2, power_axis_evt2, freq_range):
    """
    -----
    Brief
    -----
    Function intended to generate a single Bokeh figure graphically describing and identifying
    the alpha band linked with EEG researches and studies.

    -----------
    Description
    -----------
    The current function was mainly created to support "eeg_extract_alphaband" Jupyter Notebook, ensuring
    a graphical representation of an EEG signal segmented into time windows (of two types) and also the
    generation of the power spectrum where the alpha bands are highlighted.

    Applied in the Notebook titled "EEG - Alpha Band Extraction".

    ----------
    Parameters
    ----------
    freq_axis_evt1 : list
        Frequency axis of the power spectrum belonging to a "Eyes Opened" time window.

    power_axis_evt1 : list
        Power axis of the power spectrum belonging to a "Eyes Opened" time window.

    freq_axis_evt2 : list
        Frequency axis of the power spectrum belonging to a "Eyes Closed" time window.

    power_axis_evt2 : list
        Power axis of the power spectrum belonging to a "Eyes Closed" time window.

    freq_range : list
        List defining the range of frequencies to be presented on the visualisation window of our spectrum.
    """

    # Rename variables.
    freq_axis_eyes_closed = freq_axis_evt2
    freq_axis_eyes_opened = freq_axis_evt1
    power_spect_eyes_closed = power_axis_evt2
    power_spect_eyes_opened = power_axis_evt1

    # List that store the figure handler
    list_figures = plot([freq_axis_eyes_closed, freq_axis_eyes_opened],
                        [power_spect_eyes_closed, power_spect_eyes_opened],
                        title=["Estimated Power Spectral Density - Closed Eyes",
                               "Estimated Power Spectral Density - Opened Eyes"],
                        legend_label=["Bandpass Filtered Freq. Band", "Bandpass Filtered Freq. Band"],
                        x_axis_label="Frequency (Hz)", y_axis_label="PSD (uV^2/Hz)", grid_plot=True, grid_lines=1,
                        grid_columns=2, x_range=freq_range, show_plot=False, get_fig_list=True)

    # Indexes of Alpha Band.
    alpha_band_indexes_eyes_closed = numpy.where((numpy.array(freq_axis_eyes_closed) >= 8) &
                                                 (numpy.array(freq_axis_eyes_closed) <= 12))[0]
    alpha_band_indexes_eyes_opened = numpy.where((numpy.array(freq_axis_eyes_opened) >= 8) &
                                                 (numpy.array(freq_axis_eyes_opened) <= 12))[0]

    # Maximum Spectrum value.
    maxPower = numpy.max((numpy.max(power_spect_eyes_closed), numpy.max(power_spect_eyes_opened)))

    # Plotting of Alpha Band [Eyes Closed]
    list_figures[0].y_range = Range1d(0, 1.2 * maxPower)
    list_figures[0].patch(list(freq_axis_eyes_closed[alpha_band_indexes_eyes_closed]) + list(
        freq_axis_eyes_closed[alpha_band_indexes_eyes_closed])[::-1],
                          list(power_spect_eyes_closed[alpha_band_indexes_eyes_closed]) + list(
                              numpy.zeros(len(power_spect_eyes_closed[alpha_band_indexes_eyes_closed]))),
                          fill_color=opensignals_color_pallet(), fill_alpha=0.5, line_alpha=0,
                          legend_label="Alpha Band 8-12 Hz")

    # Plotting of Alpha Band [Eyes Opened]
    list_figures[1].y_range = Range1d(0, 1.2 * maxPower)
    list_figures[1].patch(list(freq_axis_eyes_opened[alpha_band_indexes_eyes_opened]) + list(
        freq_axis_eyes_opened[alpha_band_indexes_eyes_opened])[::-1],
                          list(power_spect_eyes_opened[alpha_band_indexes_eyes_opened]) + list(
                              numpy.zeros(len(power_spect_eyes_opened[alpha_band_indexes_eyes_opened]))),
                          fill_color=opensignals_color_pallet(), fill_alpha=0.5, line_alpha=0,
                          legend_label="Alpha Band 8-12 Hz")

    # Show figure.
    grid_plot_ref = gridplot([[list_figures[0], list_figures[1]]], **opensignals_kwargs("gridplot"))
    show(grid_plot_ref)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% hrv_parameters.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_post_ecto_rem_tachogram(tachogram_time, tachogram_data, tachogram_time_nn, tachogram_data_nn):
    """
    -----
    Brief
    -----
    Function intended to generate a single Bokeh figure containing the tachogram before and after
    removing the influence of ectopic heart beats.

    -----------
    Description
    -----------
    The current function was mainly created to support "hrv_parameters" Jupyter Notebook, ensuring
    a graphical representation of a tachogram (time-series presenting the evolution of RR interval duration
    along a trial) before and after applying an algorithm for removal of ectopic beats (abnormal cardiac periods/
    events).

    Applied in the Notebook titled "ECG Analysis - Heart Rate Variability Parameters".

    ----------
    Parameters
    ----------
    tachogram_time : list
        Time axis of the original tachogram (before ectopic beats removal).

    tachogram_data : list
        RR interval duration values linked to each entry of tachogram_time.

    tachogram_time_nn : list
        Time axis of the filtered tachogram (after ectopic beats removal).

    tachogram_data_nn : list
        RR interval duration values linked to each entry of tachogram_time_nn (including only normal RR intervals |
        non-ectopic).
    """

    # List that store the figure handler
    list_figures = []

    # Plotting of Tachogram
    list_figures.append(figure(x_axis_label='Time (s)', y_axis_label='Cardiac Cycle (s)', x_range=(0, tachogram_time[-1]),
                                 **opensignals_kwargs("figure")))
    list_figures[-1].line(tachogram_time, tachogram_data, legend_label="Original Tachogram", **opensignals_kwargs("line"))
    list_figures[-1].line(tachogram_time_nn, tachogram_data_nn, legend_label="Post Ectopy Removal Tachogram",
                            line_dash="dashed", **opensignals_kwargs("line"))

    # Apply OpenSignals style to the figure under analysis.
    opensignals_style(list_figures)

    # Show plot generated with the previous code instructions.
    show(list_figures[-1])


def plot_hrv_parameters(tachogram_time, tachogram_data, time_param_dict):
    """
    -----
    Brief
    -----
    This method ensures the generation of an intuitive graphical representation of Heart Rate Variability (HRV)
    parameters, extracted from the tachogram.

    -----------
    Description
    -----------
    The current function was mainly created to support "hrv_parameters" Jupyter Notebook, being responsible for
    graphically translating statistical HRV parameters extracted from the tachogram time-series.

    Applied in the Notebook titled "ECG Analysis - Heart Rate Variability Parameters".

    ----------
    Parameters
    ----------
    tachogram_time : list
        Time axis of the original tachogram (before ectopic beats removal).

    tachogram_data : list
        RR interval duration values linked to each entry of tachogram_time.

    time_param_dict : dict
        Dictionary containing the numerical values of the parameters that will be graphically translated by this
        function.
        The following keys must be available:
        >> "Maximum RR"
        >> "Minimum RR"
        >> "Average RR"
        >> "Maximum BPM"
        >> "Minimum BPM"
        >> "Average BPM"
        >> "SDNN"
    """

    # Check if all keys are available.
    temp_dict_keys = list(time_param_dict.keys())
    for dict_key in ["Maximum RR", "Minimum RR", "Average RR", "Maximum BPM", "Minimum BPM", "Average BPM", "SDNN"]:
        if dict_key not in temp_dict_keys:
            raise RuntimeError(dict_key + " key is not available in time_param_dict input")

    # List that store the figure handler
    list_figures = []

    # Conversion of RR interval duration to BPM.
    bpm_data = (1 / numpy.array(tachogram_data)) * 60

    # Plotting of Tachogram
    list_figures.append(
        figure(x_axis_label='Time (s)', y_axis_label='Cardiac Cycle (s)', x_range=(0, tachogram_time[-1] + 0.30 * tachogram_time[-1]),
               y_range=(0.6, 1), **opensignals_kwargs("figure")))
    list_figures[-1].line(tachogram_time, tachogram_data, legend_label="Original Tachogram", **opensignals_kwargs("line"))

    # Setting the second y axis range name and range of values
    list_figures[-1].extra_y_ranges = {"BPM": Range1d(start=60, end=95)}

    # Addition of the second axis to the plot
    list_figures[-1].add_layout(LinearAxis(y_range_name="BPM", axis_label='BPM'), 'right')

    list_figures[-1].line(tachogram_time, bpm_data, legend_label="Heart Rate (BPM)", y_range_name="BPM",
                            **opensignals_kwargs("line"))

    # Representation of Maximum, Minimum and Average Points
    dict_keys = time_param_dict.keys()
    for key in dict_keys:
        if ("Maximum" in key or "Minimum" in key) and "BPM" not in key:
            find_time = tachogram_time[numpy.where(tachogram_data == time_param_dict[key])[0][0]]
            list_figures[-1].circle(find_time, time_param_dict[key], radius=5,
                                      fill_color=opensignals_color_pallet(), legend_label=key)

        elif ("Maximum" in key or "Minimum" in key) and "BPM" in key:
            find_time = tachogram_time[numpy.where(bpm_data == time_param_dict[key])[0][0]]
            list_figures[-1].circle(find_time, time_param_dict[key], radius=5,
                                      fill_color=opensignals_color_pallet(), legend_label=key, y_range_name="BPM")

        elif "Average" in key and "BPM" not in key:
            list_figures[-1].line([0, tachogram_time[-1]], [time_param_dict[key], time_param_dict[key]],
                                    legend_label="Average RR", **opensignals_kwargs("line"))

        elif "SDNN" in key:
            box_annotation = BoxAnnotation(left=0, right=tachogram_time[-1], top=time_param_dict["Average RR"] + time_param_dict["SDNN"],
                                           bottom=time_param_dict["Average RR"] - time_param_dict["SDNN"],
                                           fill_color="black", fill_alpha=0.1)
            list_figures[-1].rect(find_time, time_param_dict[key], width=0, height=0, fill_color="black",
                                    fill_alpha=0.1, legend_label="SDNN")
            list_figures[-1].add_layout(box_annotation)

    # Apply OpenSignals style to the plot.
    opensignals_style(list_figures, toolbar="above")

    # Show plot.
    show(list_figures[-1])


def plot_hrv_power_bands(freqs, power_spect):
    """
    -----
    Brief
    -----
    Analysing tachogram data in the Fourier/Frequency domain could be extremely useful, being the current function
    dedicated to the graphical representation of the tachogram power spectrum together with meaningful frequency
    bands.

    -----------
    Description
    -----------
    Tachogram power spectrum is quite helpful for analysing heart rate variability.

    The obtained power spectrum should be segmented into multiple frequency bands:
    "ulf_band": [0.00, 0.003], "vlf_band": [0.003, 0.04], "lf_band": [0.04, 0.15], "hf_band": [0.15, 0.40]

    Each band reflects specific mechanisms, namely, thermoregulatory mechanisms (VLF), sympathetic modulation (LF)
    and parasympathetic modulation (HF) of HRV.

    Applied in the Notebook titled "ECG Analysis - Heart Rate Variability Parameters".

    ----------
    Parameters
    ----------
    freqs : list
        Frequency axis of the power spectrum (x axis).

    power_spect : list
        Relative weight of each frequency component in the Fourier decomposition applied to the tachogram (y axis of
        the power spectrum).
    """

    # Frequemcy Parameters
    freq_bands = {"ulf_band": [0.00, 0.003], "vlf_band": [0.003, 0.04], "lf_band": [0.04, 0.15],
                  "hf_band": [0.15, 0.40]}
    power_band = {}
    total_power = 0

    band_keys = freq_bands.keys()
    for band in band_keys:
        freq_band = freq_bands[band]
        freq_samples_inside_band = [freq for freq in freqs if freq >= freq_band[0] and freq <= freq_band[1]]
        power_samples_inside_band = [p for p, freq in zip(power_spect, freqs) if
                                     freq >= freq_band[0] and freq <= freq_band[1]]
        power = numpy.round(integrate.simps(power_samples_inside_band, freq_samples_inside_band), 5)

        # Storage of power inside each band
        power_band[band] = {}
        power_band[band]["Power Band"] = power
        power_band[band]["Freqs"] = freq_samples_inside_band
        power_band[band]["Power"] = power_samples_inside_band

        # Total power update
        total_power = total_power + power

    # List that store the figure handler
    list_figures = []

    # Plotting of Tachogram
    list_figures.append(figure(x_axis_label='Frequency (Hz)', y_axis_label='Power Spectral Density (s\u00B2 / Hz)',
                                 **opensignals_kwargs("figure")))
    list_figures[-1].line(freqs, power_spect, **opensignals_kwargs("line"))
    list_figures[-1].patch(power_band["ulf_band"]["Freqs"] + power_band["ulf_band"]["Freqs"][::-1],
                             power_band["ulf_band"]["Power"] + list(numpy.zeros(len(power_band["ulf_band"]["Power"]))),
                             fill_color=opensignals_color_pallet(), fill_alpha=0.5, line_alpha=0,
                             legend_label="ULF Band")
    list_figures[-1].patch(power_band["vlf_band"]["Freqs"] + power_band["vlf_band"]["Freqs"][::-1],
                             power_band["vlf_band"]["Power"] + list(numpy.zeros(len(power_band["vlf_band"]["Power"]))),
                             fill_color=opensignals_color_pallet(), fill_alpha=0.5, line_alpha=0,
                             legend_label="VLF Band")
    list_figures[-1].patch(power_band["lf_band"]["Freqs"] + power_band["lf_band"]["Freqs"][::-1],
                             power_band["lf_band"]["Power"] + list(numpy.zeros(len(power_band["lf_band"]["Power"]))),
                             fill_color=opensignals_color_pallet(), fill_alpha=0.5, line_alpha=0, legend_label="LF Band")
    list_figures[-1].patch(power_band["hf_band"]["Freqs"] + power_band["hf_band"]["Freqs"][::-1],
                             power_band["hf_band"]["Power"] + list(numpy.zeros(len(power_band["hf_band"]["Power"]))),
                             fill_color=opensignals_color_pallet(), fill_alpha=0.5, line_alpha=0, legend_label="HF Band")

    # Apply OpenSignals style.
    opensignals_style(list_figures)

    # Show plots.
    show(list_figures[-1])

# =================================================================================================
# ================================ Pre-Process Category ===========================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%% emg_fatigue_evaluation_median_freq.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_compare_act_config(signal, sample_rate, file_name=None):
    """
    -----
    Brief
    -----
    By invoking this function, a gridplot will be presented, in order to show the effect in muscular
    activation detection, when some input parameters of the algorithm are changed.

    -----------
    Description
    -----------
    It will be generated a Bokeh figure with 3x2 format, comparing the results of muscular
    activation algorithm when his input parameters are changed.

    At the first column are presented three plot zones, each plot zone is formed by an EMG signal,
    the smoothed signal and the muscular activation detection threshold.

    The smoothing level (SL) and threshold (TH) are customizable parameters, so, between these three
    figures, at least one of the parameters changed (each row of the gridplot shows graphical
    results obtained through the use of a specific set of algorithm parameter values [SL, TH] =
    [20, 10]% or [20, 50]% or [70, 10]%).

    At the second column is shown the result of applying muscular activation detection algorithm
    with the original EMG signal and a rectangular signal defining the start and end of each
    muscular activation period.

    Applied in the Notebook "Fatigue Evaluation - Evolution of Median Power Frequency".

    ----------
    Parameters
    ----------
    signal : list
        List with EMG signal to present.

    sample_rate : int
        Acquisitions sampling rate.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.
    """

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    time = numpy.linspace(0, len(signal) / sample_rate, len(signal))[0:14000]
    signal = numpy.array(signal[0:14000]) - numpy.average(signal[0:14000])

    # Muscular Activation Detection.
    muscular_activation_begin_20_10, muscular_activation_end_20_10, smooth_signal_20_10, \
    threshold_level_20_10 = detect_emg_activations(list(signal), sample_rate, smooth_level=20,
                                                   threshold_level=10)
    threshold_level_20_10 = (numpy.max(signal) * threshold_level_20_10) / \
                            numpy.max(smooth_signal_20_10)
    smooth_signal_20_10 = (numpy.max(signal) * numpy.array(smooth_signal_20_10)) / \
                          numpy.max(smooth_signal_20_10)
    activation_20_10 = numpy.zeros(len(time))
    for activation in range(0, len(muscular_activation_begin_20_10)):
        activation_20_10[muscular_activation_begin_20_10[activation]:
                         muscular_activation_end_20_10[activation]] = numpy.max(signal)

    muscular_activation_begin_20_50, muscular_activation_end_20_50, smooth_signal_20_50, \
    threshold_level_20_50 = detect_emg_activations(list(signal), sample_rate, smooth_level=20,
                                                   threshold_level=50)
    threshold_level_20_50 = (numpy.max(signal) * threshold_level_20_50) / \
                            numpy.max(smooth_signal_20_50)
    smooth_signal_20_50 = (numpy.max(signal) * numpy.array(smooth_signal_20_50)) / \
                          numpy.max(smooth_signal_20_50)
    activation_20_50 = numpy.zeros(len(time))
    for activation in range(0, len(muscular_activation_begin_20_50)):
        activation_20_50[muscular_activation_begin_20_50[activation]:
                         muscular_activation_end_20_50[activation]] = numpy.max(signal)

    muscular_activation_begin_70_10, muscular_activation_end_70_10, smooth_signal_70_10, \
    threshold_level_70_10 = detect_emg_activations(list(signal), sample_rate, smooth_level=70,
                                                   threshold_level=10)
    threshold_level_70_10 = (numpy.max(signal) * threshold_level_70_10) / \
                            numpy.max(smooth_signal_70_10)
    smooth_signal_70_10 = (numpy.max(signal) * numpy.array(smooth_signal_70_10)) / \
                          numpy.max(smooth_signal_70_10)
    activation_70_10 = numpy.zeros(len(time))
    for activation in range(0, len(muscular_activation_begin_70_10)):
        activation_70_10[muscular_activation_begin_70_10[activation]:
                         muscular_activation_end_70_10[activation]] = numpy.max(signal)

    # Plotting of data in a 3x2 gridplot format.
    plot_list = plot([list([]), list([]), list([]), list([]), list([]), list([])],
                     [list([]), list([]), list([]), list([]), list([]), list([])],
                     grid_lines=3, grid_columns=2, grid_plot=True, get_fig_list=True,
                     show_plot=False)

    combination = ["Smooth Level: 20 %  Threshold Level: 10 %", "Smooth Level: 20 %  "
                                                                "Threshold Level: 50 %",
                   "Smooth Level: 70 %  Threshold Level: 10 %"]
    detect_dict = {"Smooth Level: 20 %  Threshold Level: 10 %": [smooth_signal_20_10,
                                                                 threshold_level_20_10,
                                                                 activation_20_10],
                   "Smooth Level: 20 %  Threshold Level: 50 %": [smooth_signal_20_50,
                                                                 threshold_level_20_50,
                                                                 activation_20_50],
                   "Smooth Level: 70 %  Threshold Level: 10 %": [smooth_signal_70_10,
                                                                 threshold_level_70_10,
                                                                 activation_70_10]}
    for plot_aux in range(0, len(plot_list)):
        title = Title()
        combination_temp = combination[int(plot_aux / 2)]
        plot_list[plot_aux].line(time, signal, **opensignals_kwargs("line"))
        if plot_aux % 2 == 0:
            title.text = combination_temp
            plot_list[plot_aux].line(time, detect_dict[combination_temp][0],
                                 **opensignals_kwargs("line"))
            plot_list[plot_aux].line(time, detect_dict[combination_temp][1],
                                 **opensignals_kwargs("line"))
            plot_list[plot_aux].yaxis.axis_label = "Raw Data"
        else:
            title.text = "Result for " + combination_temp
            plot_list[plot_aux].line(time, detect_dict[combination_temp][2],
                                 **opensignals_kwargs("line"))

        # x axis labels.
        if plot_aux in [4, 5]:
            plot_list[plot_aux].xaxis.axis_label = "Time (s)"

        plot_list[plot_aux].title = title

    grid_plot_ref = gridplot([[plot_list[0], plot_list[1]], [plot_list[2], plot_list[3]],
                              [plot_list[4], plot_list[5]]], **opensignals_kwargs("gridplot"))
    show(grid_plot_ref)
    #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')


def plot_median_freq_evol(time_signal, signal, time_median_freq, median_freq, activations_begin,
                          activations_end, sample_rate, file_name=None):
    """
    -----
    Brief
    -----
    Graphical representation of the EMG median power frequency evolution time series.

    -----------
    Description
    -----------
    Function intended to generate a Bokeh figure with 2x1 format, where each muscular activation
    period is identified through a colored box and the plot that shows the median frequency
    evolution is also presented.

    In the first cell is presented the EMG signal, highlighting each muscular activation.
    The second cell has the same time scale as the first one (the two plots are synchronized), being
    plotted the evolution time series of EMG median frequency.

    Per muscular activation period is extracted a Median Power Frequency value (sample), so, our
    window is a muscular activation period.

    Median power frequency is a commonly used parameter for evaluating muscular fatigue.
    It is widely accepted that this parameter decreases as fatigue sets in.

    Applied in the Notebook "Fatigue Evaluation - Evolution of Median Power Frequency".

    ----------
    Parameters
    ----------
    time_signal : list
        List with the time axis samples of EMG signal.

    signal : list
        List with EMG signal to present.

    time_median_freq : list
        List with the time axis samples of the median frequency evolution time-series.

    median_freq : list
        List with the Median Frequency samples.

    activations_begin : list
        List with the samples where each muscular activation period starts.

    activations_end : list
        List with the samples where each muscular activation period ends.

    sample_rate : int
        Sampling rate of acquisition.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.
    """

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    list_figures_1 = plot([list(time_signal), list(time_median_freq)],
                          [list(signal), list(median_freq)],
                          title=["EMG Acquisition highlighting muscular activations",
                                 "Median Frequency Evolution"], grid_plot=True,
                          grid_lines=2, grid_columns=1, open_signals_style=True,
                          x_axis_label="Time (s)",
                          yAxisLabel=["Raw Data", "Median Frequency (Hz)"],
                          x_range=[0, 125], get_fig_list=True, show_plot=False)

    # Highlighting of each processing window
    for activation in range(0, len(activations_begin)):
        color = opensignals_color_pallet()
        box_annotation = BoxAnnotation(left=activations_begin[activation] / sample_rate,
                                       right=activations_end[activation] / sample_rate,
                                       fill_color=color, fill_alpha=0.1)
        box_annotation_copy = BoxAnnotation(left=activations_begin[activation] / sample_rate,
                                            right=activations_end[activation] / sample_rate,
                                            fill_color=color, fill_alpha=0.1)
        list_figures_1[0].add_layout(box_annotation)
        list_figures_1[1].add_layout(box_annotation_copy)

    gridplot_1 = gridplot([[list_figures_1[0]], [list_figures_1[1]]],
                          **opensignals_kwargs("gridplot"))
    show(gridplot_1)
    #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% digital_filtering.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_informational_band(freqs, power, signal, sr, band_begin, band_end,
                            legend="Signal Power Spectrum", x_lim=[], y_lim=[],
                            show_plot=False, file_name=None):
    """
    -----
    Brief
    -----
    With this function it is possible to present a plot containing the FFT Power Spectrum of an ECG
    signal, highlighting the informative frequency band.

    -----------
    Description
    -----------
    The FFT Power Spectrum, of an input signal, can be generated through plotfft function of
    novainstrumentation package (or periogram function of scipy package).
    The x axis (freqs) represents the frequency components of the signal, after decomposition was
    achieved by applying the Fourier Transform. The y axis (power) defines the relative weight of
    each frequency component (sinusoidal function) in the process of reconstructing the signal by
    re-summing of decomposition components.

    Additionally, it is also graphically presented a rectangular box showing which are the frequency
    components with relevant information for studying our input physiological signal.

    Note that each physiological signal has its own "informational band", whose limits should be
    specified in the input arguments "band_begin" and "band_end".

    Applied in the Notebook "Digital Filtering - A Fundamental Pre-Processing Step".

    ----------
    Parameters
    ----------
    freqs : list
        Frequency axis of power spectrum, defining which frequency components were used during the
        Fourier decomposition.

    power : list
        Power axis of power spectrum, defining the relative weight that each frequency component,
        inside "freqs", will have during the signal reconstruction.

    signal : list
        List containing the acquired signal samples.

    sr : int
        Sampling rate.

    band_begin : float
        Lower frequency inside the signal informational band.

    band_end : float
        Higher frequency inside the signal informational band.

    legend : str
        A string containing the legend that defines the power spectrum, for example: "ECG Power
        Spectrum".

    x_lim : list
        A list with length equal to 2, defining the first and last x value that should be presented.

    y_lim : list
        A list with length equal to 2, defining the first and last y value that should be presented.

    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    Returns
    -------
    out : bokeh figure
        Bokeh figure presenting the signal power spectrum and highlighting the informational band.
    """

    # Retrocompatibility.
    legend_label = legend

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    # ----------------------------- Verification procedure -----------------------------------------
    # Check if list is the type of input arguments x_lim and y_lim.
    if type(x_lim) is list and type(y_lim) is list:
        if len(x_lim) == 2 and len(y_lim) == 2:
            if len(x_lim) == 0:
                x_lim = [freqs[0], freqs[-1]]
            if len(y_lim) == 0:
                y_lim = [power[0], power[-1]]
        else:
            raise RuntimeError("The inputs arguments 'x_lim' and 'y_lim', when explicitly specified, "
                               "must be formed by two elements (defining the lower and upper limits "
                               "of the x and y axis).")
    else:
        raise RuntimeError("At least one of the input arguments (x_lim or y_lim) does not have a valid"
                           " type. The inputs must be lists.")

    # List that store the figure handler
    list_figures = []

    # Plotting of power spectrum
    list_figures.append(figure(x_axis_label='Frequency (Hz)', y_axis_label='Relative Weight', x_range=(x_lim[0], x_lim[-1]),
                                 y_range=(y_lim[0], y_lim[1]), **opensignals_kwargs("figure")))
    list_figures[-1].line(freqs, power, legend_label=legend_label,
                            **opensignals_kwargs("line"))

    # Highlighting of informational band
    color = opensignals_color_pallet()
    box_annotation = BoxAnnotation(left=band_begin, right=band_end, fill_color=color,
                                   fill_alpha=0.1)
    list_figures[-1].circle([-100], [0], fill_color=color, fill_alpha=0.1,
                              legend_label="Informational Band")
    list_figures[-1].add_layout(box_annotation)

    # # Determination of the maximum frequency
    # max_freq = max_frequency(signal, sr)
    #
    # # Rejection band(above maximum frequency)
    # color = "black"
    # box_annotations = BoxAnnotation(left=max_freq, right=max_freq + 5, fill_color=color,
    #                                 fill_alpha=0.1)
    #
    # # Show of the plots with the rejection band
    # list_figures[-1].circle([-100], [0], fill_color=color, fill_alpha=0.1, legend_label="Rejected Band")
    # list_figures[-1].add_layout(box_annotations)
    # list_figures[-1].add_layout(Arrow(end=VeeHead(size=15, line_color=color, fill_color=color,
    #                                                 fill_alpha=0.1), line_color=color,
    #                                     x_start=max_freq + 5, y_start=y_lim[1]/2,
    #                                     x_end=max_freq + 15, y_end=y_lim[1]/2))

    # Apply opensignals style.
    if len(numpy.shape(list_figures)) != 1:
        flat_list = [item for sublist in list_figures for item in sublist]
        opensignals_style(flat_list)
    else:
        opensignals_style(list_figures)

    # Present the generated plots.
    if show_plot is True:
        show(list_figures[-1])
        #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')

    return list_figures[-1]


def plot_before_after_filter(signal, sr, band_begin, band_end, order=1, x_lim=[], y_lim=[],
                             orientation="hor", show_plot=False, file_name=None):
    """
    -----
    Brief
    -----
    The use of the current function is very useful for comparing two power spectrum's (before and
    after filtering the signal).
    This function invokes "plot_informational_band" in order to get the power spectrum before
    applying the signal to the lowpass filter.

    -----------
    Description
    -----------
    The FFT Power Spectrum, of an input signal, can be generated through plotfft function of
    novainstrumentation package (or periogram function of scipy package).
    The x axis (freqs) represents the frequency components of the signal, after decomposition was
    achieved by applying the Fourier Transform. The y axis (power) defines the relative weight of
    each frequency component (sinusoidal function) in the process of reconstructing the signal by
    re-summing of decomposition components.

    It is presented a 1x2 gridplot for compaing the differences in frequency composition of the
    signal under analysis (before and after filtering).

    Additionally, it is also graphically presented a rectangular box showing which are the frequency
    components with relevant information for studying our input physiological signal.

    Applied in the Notebook "Digital Filtering - A Fundamental Pre-Processing Step".

    ----------
    Parameters
    ----------
    signal : list
        List containing the acquired signal samples.

    sr : int
        Sampling rate.

    band_begin : float
        Lower frequency inside the signal informational band.

    band_end : float
        Higher frequency inside the signal informational band.

    order : int
        Filter order.

    x_lim : list
        A list with length equal to 2, defining the first and last x value that should be presented.

    y_lim : list
        A list with length equal to 2, defining the first and last y value that should be presented.

    orientation : str
        If "hor" then the generated figures will be joined together in an horizontal gridplot.
        When "vert" the gridplot will be a vertical grid and when "same" the plots are generated at
        the same figure.

    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    Returns
    -------
    out : list
        List of Bokeh figures that compose the generated gridplot.
    """

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    # Generation of FFT power spectrum accordingly to the filter order.
    for i in range(0, order + 1):
        # Initialisation and appending of data to the figures list.
        if i == 0:
            # Power spectrum
            freqs_after, power_after = plotfft(signal, sr)
            figure_after = plot_informational_band(freqs_after, power_after, signal, sr,
                                                   band_begin, band_end,
                                                   legend="Signal Power Spectrum", x_lim=x_lim,
                                                   y_lim=y_lim)
            # List that store the figure handler
            list_figures = [[figure_after]]
        else:
            filter_signal = lowpass(signal, f=band_end, order=i, fs=sr)

            # Power spectrum
            freqs_after, power_after = plotfft(filter_signal, sr)

            if orientation != "same":
                figure_after = plot_informational_band(freqs_after, power_after, filter_signal, sr,
                                                       band_begin, band_end,
                                                       legend="Filtered FFT (Order " + str(i) + ")",
                                                       x_lim=x_lim, y_lim=y_lim)
                # Append data accordingly to the desired direction of representation.
                if orientation == "hor":
                    # Append to the figure list the power spectrum of the signal after filtering.
                    list_figures[-1].append(figure_after)
                elif orientation == "vert":
                    list_figures.append([figure_after])
            else:
                list_figures[-1][0].line(freqs_after, power_after, legend_label="Filtered FFT (Order " + str(i) + ")",
                                         **opensignals_kwargs("line"))

    # Show gridplot.
    grid_plot_1 = gridplot(list_figures, **opensignals_kwargs("gridplot"))

    if show_plot is True:
        show(grid_plot_1)

    return list_figures


def plot_low_pass_filter_response(show_plot=False, file_name=None):
    """
    -----
    Brief
    -----
    Taking into consideration the generic transfer function that defines the frequency response of
    a low-pass filter (|H|=1/(sqrt(1+(f/fc)^2n), where fc is the corner frequency and n is the
    filter order), the current function will generate a figure for comparing the frequency response
    accordingly to the filter order.

    -----------
    Description
    -----------
    In digital and analogical systems, a filter defines a system capable of attenuating specific
    frequency components of the signal that is applied to it.

    The filter behaviour can be mathematically defined through a transfer function, showing
    precisely the stop- and pass-bands.

    In the case of a low-pass filter, a structural parameter is the corner frequency (where the
    attenuation begins). Like the name suggests, all signal components with frequency below the
    corner frequency will be outputted without changes (they "pass" the filter), while components
    with frequency above the corner frequency suffers an attenuation (the bigger the difference
    between the frequency of the component and the corner frequency the bigger the attenuation).

    It is shown (in the same figure) the low-pass filter response for different order (1, 2, 3, 4,
    5, 6).

    Applied in the Notebook "Digital Filtering - A Fundamental Pre-Processing Step".

    ----------
    Parameters
    ----------
    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    file_name : str
        Path containing the destination folder where the Bokeh figure will be stored.

    Returns
    -------
    out : list
        List of Bokeh figures that compose the generated gridplot.
    """

    # Generation of the HTML file where the plot will be stored.
    #file_name = _generate_bokeh_file(file_name)

    # Frequency list.
    freqs = numpy.linspace(1, 1200, 100000)
    cutoff_freq = 40

    # Generation of filter response.
    gain_functions = []
    legend_strs = []
    for order in range(1, 7):
        gain = 20*numpy.log10(1 / (numpy.sqrt(1 + (freqs / cutoff_freq)**(2*order))))

        # Storage of the determined gain values.
        gain_functions.append(gain)
        if order == 1:
            legend_strs.append("1st order filter")
        elif order == 2:
            legend_strs.append("2nd order filter")
        elif order == 3:
            legend_strs.append("3rd order filter")
        else:
            legend_strs.append(str(order) + "th order filter")


    # Generation of a Bokeh figure with the opensignals style.
    fig_list = plot([freqs / cutoff_freq]*len(gain_functions), gain_functions, legend_label=legend_strs,
                    title="Filter Response", x_axis_label="Normalized Frequency",
                    y_axis_label="Gain (dB)", x_axis_type="log", x_range=(0.1, 40),
                    y_range=(-120, 5), show_plot=True, get_fig_list=True)

    # Inclusion of a colored region showing the ideal behaviour.
    color=opensignals_color_pallet()
    box_annotation = BoxAnnotation(left=0.1, right=1, top=0, bottom=-120,
                                   fill_color=color,
                                   fill_alpha=0.3)
    fig_list[0].circle([-100], [0], fill_color=color, fill_alpha=0.3, legend_label="Ideal Filter Response")
    fig_list[0].add_layout(box_annotation)

    # Show figure.
    if show_plot is True:
        show(fig_list[0])
        #HTML('<iframe width=100% height=350 src="generated_plots/' + file_name + '"></iframe>')

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% tachogram.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def plot_ecg_tachogram(time, signal, tachogram_time, tachogram, time_r_peaks, show_plot=True):
    """
    -----
    Brief
    -----
    Electrocardiographic (ECG) signal is a periodical biosignal, where it is observable each electrical
    event (depolarization/repolarization) responsible for the natural rhythmicity  of heart bump.
    Tachogram is a time-series that illustrates how cardiac cycles duration changes along time.

    -----------
    Description
    -----------
    As a periodical signal, heart-rate analysis is an interesting path to achieve clinical information about
    the heart functioning.

    A healthy heart should denote variability between cycles, which is a desirable adaptive physiological
    response, taking into consideration that human heart should adjust its functioning in accordance to
    the activity/stress level of the subject.

    R peaks are the most prominent structures in ECG signal, being typically used as a reference of each
    cardiac cycle.

    After detecting these peaks, RR intervals (cardiac cycle periods) can be determined and heart-rate
    variability (HRV) studies take place.

    Tachogram is the time-series that presents the evolution of cardiac cycle duration (in seconds) along time,
    becoming the main source of information to extract multiple HRV parameters.

    This function generates a 2x1 gridplot presenting the tachogram (top cell) and the respective ECG signal
    (bottom cell), highlighting each cardiac cycle.

    Applied in the Notebook "Generation of Tachogram from ECG".

    ----------
    Parameters
    ----------
    time : list
        List containing the time-axis samples of the ECG plot.

    signal : list
        List containing the data samples of the ECG plot.

    tachogram_time : list
        List with the time-axis of the tachogram.

    tachogram : list
        List with the tachogram values (RR interval durations).

    time_r_peaks : list
        This list contains the time-instants where each R peak is located.

    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    Returns
    -------
    out : list
        List of Bokeh figures that compose the generated gridplot.
    """

    # List that store the figure handler
    list_figures_1 = [[], []]

    # Plotting of Tachogram
    list_figures_1[0].append(
        figure(x_axis_label='Time (s)', y_axis_label='Cardiac Cycle (s)', title="Tachogram", x_range=(0, time[-1]),
               **opensignals_kwargs("figure")))
    list_figures_1[0][-1].line(tachogram_time, tachogram, **opensignals_kwargs("line"))

    # Plotting of ECG signal
    list_figures_1[1].append(
        figure(x_axis_label='Time (s)', y_axis_label='Raw Data', title="ECG Acquisition", x_range=(0, time[-1]),
               **opensignals_kwargs("figure")))
    list_figures_1[1][-1].line(time, signal, **opensignals_kwargs("line"))

    # Highlighting of each cardiac cycle
    for r_peak in range(0, len(time_r_peaks) - 1):
        color = opensignals_color_pallet()
        box_annotation = BoxAnnotation(left=time_r_peaks[r_peak], right=time_r_peaks[r_peak + 1], fill_color=color,
                                       fill_alpha=0.1)
        box_annotation_copy = BoxAnnotation(left=time_r_peaks[r_peak], right=time_r_peaks[r_peak + 1], fill_color=color,
                                            fill_alpha=0.1)
        list_figures_1[0][-1].add_layout(box_annotation)
        list_figures_1[1][-1].add_layout(box_annotation_copy)

    opensignals_style([item for sublist in list_figures_1 for item in sublist])

    grid_plot_1 = gridplot(list_figures_1, **opensignals_kwargs("gridplot"))

    if show_plot is True:
        show(grid_plot_1)

    return list_figures_1


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% poincare_plot.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def plot_poincare(tachogram_data, show_plot=True):
    """
    -----
    Brief
    -----
    Poincaré plot is an important non-linear analysis tool to explore and evaluate heart rate
    variability.

    -----------
    Description
    -----------
    Using the tachogram, Poincaré plot is generating by creating groups of consecutive RR intervals,
    i.e., two consecutive sample values of the tachogram will give origin to a Poincaré point.

    As a practical example, being tach[t] the tachogram time-series, (tach[0], tach[1]), (tach[1], tach[2]), ...,
    (tach[N-1], tach[N]) are the points of the Poincaré plot.

    From this plot it is possible to extract SD1 and SD2 parameters correspondent to the standard deviation along
    two specific axis.

    This function ensures an easy way to present the Poincaré plot together with the axis needed to estimate SD1 and SD2.

    Applied in the Notebook "Generation of Poincaré Plot from ECG Analysis".

    ----------
    Parameters
    ----------
    tachogram_data : list
        List containing the data samples of the Tachogram.

    show_plot : bool
        If True then the generated figure/plot will be shown to the user.

    Returns
    -------
    out : list
        List of Bokeh figures that compose the generated gridplot.
    """

    # Poincaré axes.
    rr_i = tachogram_data[:-1]
    rr_i_plus_1 = tachogram_data[1:]

    # Estimation of some relevant variables.
    avg_rr = numpy.average(tachogram_data)
    tachogram_diff = numpy.diff(tachogram_data)
    SDSD = numpy.std(tachogram_diff)
    SDNN = numpy.std(tachogram_data)

    SD1 = numpy.sqrt(0.5 * numpy.power(SDSD, 2))
    SD2 = numpy.sqrt(2 * numpy.power(SDNN, 2) - numpy.power(SD1, 2))

    # Plotting of Tachogram
    color_1 = "#CF0272"
    color_2 = "#F199C1"
    list_figures = dispersion(rr_i, rr_i_plus_1, 'RR\u1D62 (s)', 'RR\u1D62\u208A\u2081 (s)', show_plot=False)

    list_figures[-1].line([numpy.min(rr_i), numpy.max(rr_i)], [numpy.min(rr_i_plus_1), numpy.max(rr_i_plus_1)],
                            line_color="black", line_dash="dashed")
    list_figures[-1].line([numpy.min(rr_i), numpy.max(rr_i)],
                            [-numpy.min(rr_i) + 2 * avg_rr, -numpy.max(rr_i) + 2 * avg_rr], line_color="black",
                            line_dash="dashed")
    list_figures[-1].add_layout(Arrow(start=VeeHead(size=15, line_color=color_1, fill_color=color_1),
                                        end=VeeHead(size=15, line_color=color_1, fill_color=color_1),
                                        x_start=avg_rr - SD2 * math.cos(math.radians(45)),
                                        y_start=avg_rr - SD2 * math.sin(math.radians(45)),
                                        x_end=avg_rr + SD2 * math.cos(math.radians(45)),
                                        y_end=avg_rr + SD2 * math.cos(math.radians(45)), line_color=color_1,
                                        line_width=3))
    list_figures[-1].add_layout(Arrow(start=VeeHead(size=15, line_color=color_2, fill_color=color_2),
                                        end=VeeHead(size=15, line_color=color_2, fill_color=color_2),
                                        x_start=avg_rr - SD1 * math.sin(math.radians(45)),
                                        y_start=avg_rr + SD1 * math.cos(math.radians(45)),
                                        x_end=avg_rr + SD1 * math.sin(math.radians(45)),
                                        y_end=avg_rr - SD1 * math.cos(math.radians(45)), line_color=color_2,
                                        line_width=3))
    list_figures[-1].line([rr_i[0], rr_i[0]], [rr_i[0], rr_i[0]], legend_label="2 x SD1", line_color=color_2, line_width=2)
    list_figures[-1].line([rr_i[0], rr_i[0]], [rr_i[0], rr_i[0]], legend_label="2 x SD2", line_color=color_1, line_width=2)

    # Apply OpenSignals style.
    opensignals_style(list_figures)

    # Show plot.
    if show_plot is True:
        show(list_figures[-1])

    return list_figures

# =================================================================================================
# ===================================== Record Category ===========================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% resolution.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def plot_compare_resolutions(time, signal_res_1, signal_res_2, sampling_rate, y_axis_label="Temperature (ºC)",
                             time_start=110, time_end=150, y_range=[38, 40.5]):
    """
    -----
    Brief
    -----
    With the current function it will be presented a gridplot with 2 rows, where three plots are graphically
    represented

    -----------
    Description
    -----------
    Acquiring data with a right resolution ensures that posterior conclusions will be more reliable and effective.

    The current function is intended to generate a Bokeh figure with 2 rows. In the first row is shown a plot
    containing two synchronized signals acquired with different resolutions.

    The second gridplot row is divided into 2 cells, showing each one the previously presented multi resolution
    signals but in separate subfigures and in a zoomed format.

    Applied in the Notebook titled "Resolution - The difference between smooth and abrupt variations".

    ----------
    Parameters
    ----------
    time : list
        Time-axis linked to the acquired signal samples.

    signal_res_1 : list
        Acquired signal samples for the smallest resolution.

    signal_res_2 : list
        Acquired signal samples for the biggest resolution.

    sampling_rate : int
        Sampling rate of the acquisition.

    y_axis_label : str
        Descriptive text about the meaning behind the y axis.

    time_start : float
        Time-instant (in seconds) where the zoomed visualization window starts.

    time_end: float
        Time-instant (in seconds) where the zoomed visualization window ends.

    y_range : list
        A list with two elements, containing the delimiting values of the y axis range.
    """

    # Figure with the two plots
    figure_8_16 = figure(x_axis_label='Time (s)', y_axis_label=y_axis_label, **opensignals_kwargs("figure"))
    figure_8_16.line(time, signal_res_1, legend_label="8 Bits Acquisition", **opensignals_kwargs("line"))
    figure_8_16.line(time, signal_res_2, legend_label="16 Bits Acquisition", **opensignals_kwargs("line"))

    # Zoom window
    wind_start = int(sampling_rate * time_start)  # time_start seconds
    wind_end = int(sampling_rate * time_end)  # time_end seconds

    # Figure with 8 bits zoom
    figure_8 = figure(x_axis_label='Time (s)', y_axis_label=y_axis_label, title="8 Bits Acquisition",
                      y_range=y_range, **opensignals_kwargs("figure"))
    figure_8.line(time[wind_start:wind_end], signal_res_1[wind_start:wind_end], **opensignals_kwargs("line"))

    # Figure with 16 bits zoom
    figure_16 = figure(x_axis_label='Time (s)', y_axis_label=y_axis_label, title="16 Bits Acquisition",
                       y_range=y_range, **opensignals_kwargs("figure"))
    figure_16.line(time[wind_start:wind_end], signal_res_2[wind_start:wind_end],
                   **opensignals_kwargs("line"))

    # Show gridplot.
    opensignals_style([figure_8, figure_16, figure_8_16])
    #grid_plot = gridplot([[figure_8_16], [figure_8, figure_16]], **opensignals_kwargs("gridplot"))
    grid_plot = layout(children=[[figure_8_16], [figure_8, figure_16]], sizing_mode="scale_width")
    show(grid_plot)


# =================================================================================================
# =================================== Explain Category ============================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% respiration_slow.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# We stop here at 13h51m of 2nd October of 2018 :)
def plot_resp_slow(signal, rect_signal, sample_rate):
    """
    -----
    Brief
    -----
    Figure intended to represent the acquired RIP signal together with a rectangular signal defining
    inhalation and exhalation periods.

    -----------
    Description
    -----------
    Function design to generate a Bokeh figure containing the evolution of RIP signal, when
    slow respiration cycles occur, and the rectangular signal that defines the stages of
    inhalation and exhalation.

    Applied in the Notebook "Particularities of Inductive Respiration (RIP) Sensor ".

    ----------
    Parameters
    ----------
    signal : list
        List with the acquired RIP signal.

    rect_signal : list
        Data samples of the rectangular signal that identifies inhalation and exhalation
        segments.

    sample_rate : int
        Sampling rate of acquisition.
    """

    signal = numpy.array(signal) - numpy.average(signal)
    rect_signal = numpy.array(rect_signal)
    time = numpy.linspace(0, len(signal) / sample_rate, len(signal))

    # Inhalation and Exhalation time segments.
    # [Signal Binarisation]
    rect_signal_rev = rect_signal - numpy.average(rect_signal)
    inhal_segments = numpy.where(rect_signal_rev >= 0)[0]
    exhal_segments = numpy.where(rect_signal_rev < 0)[0]
    rect_signal_rev[inhal_segments] = numpy.max(rect_signal_rev)
    rect_signal_rev[exhal_segments] = numpy.min(rect_signal_rev)

    # [Signal Differentiation]
    diff_rect_signal = numpy.diff(rect_signal_rev)
    inhal_begin = numpy.where(diff_rect_signal > 0)[0]
    inhal_end = numpy.where(diff_rect_signal < 0)[0]
    exhal_begin = inhal_end
    exhal_end = inhal_begin[1:]

    # Generation of a Bokeh figure where data will be plotted.
    plot_aux = plot(list([0]), list([0]), showPlot=False)[0]

    # Edition of Bokeh figure (title, axes labels...)
    # [title]
    title = Title()
    title.text = "RIP Signal with slow cycles"
    plot_aux.title = title

    # [plot]
    plot_aux.line(time, signal, **opensignals_kwargs("line"))
    inhal_color = opensignals_color_pallet()
    exhal_color = opensignals_color_pallet()
    for inhal_exhal in range(0, len(inhal_begin)):
        if inhal_exhal == 0:
            legend_label = ["Inhalation", "Exhalation"]
        else:
            legend_label = [None, None]

        plot_aux.line(time[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]],
                  rect_signal_rev[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]],
                  line_width=2, line_color=inhal_color, legend_label=legend_label[0])

        if inhal_exhal != len(inhal_begin) - 1:
            plot_aux.line(time[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]],
                      rect_signal_rev[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]],
                      line_width=2, line_color=exhal_color, legend_label=legend_label[1])
        else:
            plot_aux.line(time[exhal_begin[inhal_exhal]:], rect_signal_rev[exhal_begin[inhal_exhal]:],
                      line_width=2, line_color=exhal_color, legend_label=legend_label[1])

    # [axes labels]
    plot_aux.xaxis.axis_label = "Time (s)"
    plot_aux.yaxis.axis_label = "Raw Data (without DC component)"

    show(plot_aux)



def plot_resp_diff(signal, rect_signal, sample_rate):
    """
    Function design to generate a Bokeh figure containing the evolution of RIP signal, when
    respiration was suspended for a long period, the rectangular signal that defines the
    stages of inhalation and exhalation and the first derivative of the RIP signal.

    Applied in the Notebook "Particularities of Inductive Respiration (RIP) Sensor ".

    ----------
    Parameters
    ----------
    signal : list
        List with the acquired RIP signal.

    rect_signal : list
        Data samples of the rectangular signal that identifies inhalation and exhalation
        segments.

    sample_rate : int
        Sampling rate of acquisition.
    """

    signal = numpy.array(signal) - numpy.average(signal)
    rect_signal = numpy.array(rect_signal)
    time = numpy.linspace(0, len(signal) / sample_rate, len(signal))
    signal_diff = numpy.diff(signal)

    # Inhalation and Exhalation time segments.
    # [Signal Binarization]
    rect_signal_rev = rect_signal - numpy.average(rect_signal)
    inhal_segments = numpy.where(rect_signal_rev >= 0)[0]
    exhal_segments = numpy.where(rect_signal_rev < 0)[0]
    rect_signal_rev[inhal_segments] = numpy.max(rect_signal_rev)
    rect_signal_rev[exhal_segments] = numpy.min(rect_signal_rev)

    # Normalized Data.
    norm_signal = signal / numpy.max(signal)
    norm_rect_signal = rect_signal_rev / numpy.max(rect_signal_rev)
    norm_signal_diff = signal_diff / numpy.max(signal_diff)

    # Smoothed Data.
    smooth_diff = smooth(signal_diff, int(sample_rate / 10))
    smooth_norm_diff = smooth(norm_signal_diff, int(sample_rate / 10))

    # Scaled Rectangular Signal.
    scaled_rect_signal = (rect_signal_rev * numpy.max(smooth_diff)) / numpy.max(rect_signal_rev)

    # [Signal Differentiation]
    diff_rect_signal = numpy.diff(rect_signal_rev)
    inhal_begin = numpy.where(diff_rect_signal > 0)[0]
    inhal_end = numpy.where(diff_rect_signal < 0)[0]
    exhal_begin = inhal_end
    exhal_end = inhal_begin[1:]

    # Generation of a Bokeh figure where data will be plotted.
    figure_list = plot([list([0]), list([0]), list([0])],
                                    [list([0]), list([0]), list([0])], gridPlot=True, gridLines=3,
                                    gridColumns=1, showPlot=False)

    # Edition of Bokeh figure (title, axes labels...)
    # [Top Figure]
    title = Title()
    title.text = "RIP Signal and Respiration Cycles"
    figure_list[0].title = title

    figure_list[0].line(time, signal, **opensignals_kwargs("line"))

    # [Plot of inhalation and exhalation segments]
    _inhal_exhal_segments(figure_list[0], list(time), list(rect_signal_rev), inhal_begin, inhal_end,
                          exhal_begin, exhal_end)
    figure_list[0].yaxis.axis_label = "Raw Data (without DC component)"

    # [Middle Figure]
    title = Title()
    title.text = "1st Derivative of RIP Signal and Respiration Cycles"
    figure_list[1].title = title

    figure_list[1].line(time[1:], smooth_diff, **opensignals_kwargs("line"))

    # [Plot of inhalation and exhalation segments]
    _inhal_exhal_segments(figure_list[1], list(time), list(scaled_rect_signal), inhal_begin,
                          inhal_end, exhal_begin, exhal_end)
    figure_list[1].yaxis.axis_label = "Raw Differential Data"

    # [Bottom Figure]
    title = Title()
    title.text = "RIP Signal and 1st Derivative (Normalized)"
    figure_list[2].title = title

    figure_list[2].line(time, norm_signal, **opensignals_kwargs("line"))
    figure_list[2].line(time[1:], smooth_norm_diff, legend_label="RIP 1st Derivative", **opensignals_kwargs("line"))

    # [Plot of inhalation and exhalation segments]
    _inhal_exhal_segments(figure_list[2], list(time), list(norm_rect_signal), inhal_begin,
                          inhal_end, exhal_begin, exhal_end)
    figure_list[2].yaxis.axis_label = "Normalized Data"
    figure_list[2].xaxis.axis_label = "Time (s)"

    grid_plot_ref = gridplot([[figure_list[0]], [figure_list[1]], [figure_list[2]]],
                             **opensignals_kwargs("gridplot"))

    show(grid_plot_ref)


# =================================================================================================
# ====================================== Other Category ===========================================
# =================================================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% emg_overview.ipynb %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def plot_simple_threshold_algorithm(time, signal_smooth, binary_signal, sr, thresh_1, thresh_2):
    """
    -----
    Brief
    -----
    Figure intended to represent a muscular activation envelope and the two thresholds of a double-threshold algorithm
    used to detect the onset and offset of the muscular activation.

    -----------
    Description
    -----------
    Function design to generate a Bokeh figure containing the graphical explanation of the double-threshold muscular
    activation detection algorithm, presenting the smooth version of a muscular activation and the two thresholds of the
    detection algorithm.

    The intesection points between the smoothed signal and the thresholds will define the onset and offset of the
    muscular activation period.

    Applied in the Notebook "EMG - Overview".

    ----------
    Parameters
    ----------
    time : list
        List with the time axis values of the smoothed signal.

    signal_smooth : list
        List with the smooth version of the acquired EMG signal.

    binary_signal : list
        Binary signal data samples which graphically illustrates the delimiting intervals of a muscular activation
        period.

    sr : int
        Data acquisition sampling rate in Hz.

    thresh_1 : int
        Threshold 1 intended to detect the onset of the muscular activation periods.

    thresh_2 : int
        Threshold 2 intended to detect the offset of the muscular activation periods.
    """
    # create list for thresholds to add them in the legend of the next plot
    thresh1 = []
    thresh2 = []

    for n in range(len(time)):
        thresh1.append(thresh_1)
        thresh2.append(thresh_2)

    # find intersection of onset and offset signal with thresholds
    intersect_on = []
    intersect_index_on = []
    intersect_off = []
    intersect_index_off = []
    for index, i in enumerate(signal_smooth):
        # return thres_1 value if signal meets thresh_1 for onset
        if i >= thresh_1 and signal_smooth[index - 1] < thresh_1:
            intersect_on.append(thresh_1)
            intersect_index_on.append(index)
        # return thres_2 value if signal meets thresh_2 for offset
        elif i <= thresh_2 and signal_smooth[index - 1] > thresh_2:
            intersect_off.append(thresh_2)
            intersect_index_off.append(index)

    # plot of binary and smooth signal to visualize the activation and inactivation periods
    fig_list = plot([list(time), list(time), list(time), list(time)],
                     [list(numpy.array(binary_signal) * max(signal_smooth)), list(signal_smooth), list(thresh1),
                      list(thresh2)], legend_label=["Activation Signal", "Smoothed Signal", "Threshold 1", "Threshold 2"],
                      grid_plot=False, opensignals_style=True, x_axis_label="Time (s)", y_axis_label="RAW Data Samples",
                      x_range=(11, 13), get_fig_list=True, show_plot=False)
    fig_list[0].circle(numpy.array(intersect_index_on) / sr, intersect_on, size=10, color="yellowgreen",
                       legend_label="Onset")
    fig_list[0].circle(numpy.array(intersect_index_off) / sr, intersect_off, size=10, color="darkorange",
                       legend_label="Offset")
    show(fig_list[0])


def download(link, out):
    """
    Downloading data from websites, such as previously acquired physiological signals, is an extremely relevant task,
    taking into consideration that, without data, processing cannot take place.

    With the current function a file can be easily downloaded through the "link" input.

    ----------
    Parameters
    ----------
    link : str
        String with the url that contains the file to be downloaded.

    out : str
        Name of the downloaded file (with extension). A destination path can also be included.

    """

    # [Source: https://stackoverflow.com/questions/7243750/download-file-from-web-in-python-3]
    r = requests.get(link)
    with open(out, 'wb') as outfile:
        outfile.write(r.content)

def _inhal_exhal_segments(fig, time, signal, inhal_begin, inhal_end, exhal_begin, exhal_end):
    """
    Auxiliary function used to plot each inhalation/exhalation segment.

    ----------
    Parameters
    ----------
    fig : Bokeh figure
        Figure where inhalation/exhalation segments will be plotted.

    time : list
        Time axis.

    signal : list
        Data samples of the acquired/processed signal.

    inhal_begin : list
        List with the indexes where inhalation segments begin.

    inhal_end : list
        List with the indexes where inhalation segments end.

    exhal_begin : list
        List with the indexes where exhalation segments begin.

    exhal_end : list
        List with the indexes where exhalation segments end.
    """

    inhal_color = opensignals_color_pallet()
    exhal_color = opensignals_color_pallet()
    for inhal_exhal in range(0, len(inhal_begin)):
        if inhal_exhal == 0:
            legend_label = ["Respiration Suspension", "Normal Breath"]
        else:
            legend_label = [None, None]

        fig.line(time[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]],
                 signal[inhal_begin[inhal_exhal]:inhal_end[inhal_exhal]], line_width=2,
                 line_color=inhal_color, legend_label=legend_label[0])

        if inhal_exhal != len(inhal_begin) - 1:
            fig.line(time[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]],
                     signal[exhal_begin[inhal_exhal]:exhal_end[inhal_exhal]], line_width=2,
                     line_color=exhal_color, legend_label=legend_label[1])
            if inhal_exhal == 0:
                fig.line(time[:inhal_begin[inhal_exhal]], signal[:inhal_begin[inhal_exhal]],
                         line_width=2, line_color=exhal_color, legend_label=legend_label[1])
        else:
            fig.line(time[exhal_begin[inhal_exhal]:], signal[exhal_begin[inhal_exhal]:],
                     line_width=2, line_color=exhal_color, legend_label=legend_label[1])


# 07/11/2018  00h02m :)
