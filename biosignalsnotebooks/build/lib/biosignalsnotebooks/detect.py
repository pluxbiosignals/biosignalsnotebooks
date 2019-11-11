
"""
List of functions intended to detect events in the acquired data.

Available Functions
-------------------
[Public]

detect_r_peaks
    Function that applies the Pan-Tompkins algorithm for detection of R peaks.
tachogram
    From ECG signal or from the list of samples where R peaks are located, this function generates
    a tachogram, i.e., a time-series with the evolution of RR interval (in seconds) along the
    acquisition.
detect_emg_activations
    In this function a single threshold algorithm is used for identifying the begin and end of each
    muscular activation period.
    EMG signal was simplified before the "sample by sample" threshold check, through smoothing and
    application of Teager Kaiser Energy Operator (TKEO).

Available Functions
-------------------
[Private]

<Pan-Tompkins Algorithm>
_ecg_band_pass_filter
    Step 1 of ECG simplification presented on Pan-Tompkins algorithm.
_differentiate
    Step 2 of ECG simplification presented on Pan-Tompkins algorithm.
_squaring
    Step 3 of ECG simplification presented on Pan-Tompkins algorithm.
_integration
    Step 4 of ECG simplification presented on Pan-Tompkins algorithm.
_buffer_ini
    Initialisation of the buffer that stores eight RR intervals (R peak detection algorithm consists
    in a sequential verification of each signal samples and rr_buffer will store the most recent
    eight RR intervals).
_buffer_update
    Update of buffer content (used in the R peak detection algorithm).
_detects_peaks
    Function where a first sequence of conditions, defined by Pan and Tompkins, are checked in order
    to obtain a temporary list of possible R peaks.
_checkup
    Checkup of a second sequence of conditions, defined by Pan and Tompkins, in order to our
    temporary list with possible R peaks be reduced to the set of definitive R peaks.
_acceptpeak
    In this function the Pan-Tompkins algorithm parameter SPK1 is updated.
_noisepeak
    In this function the Pan-Tompkins algorithm parameter NPK1 is updated.
</Pan-Tompkins Algorithm>

<Muscular Activation Detection Algorithm>
_thres_norm_reg
    Inside this function a relative value (percentage) of the muscular activation threshold is
    converted to an absolute format.

Observations/Comments
---------------------
None

/\
"""

from .conversion import raw_to_phy
from .visualise import plot, opensignals_kwargs, opensignals_style, opensignals_color_pallet
from .aux_functions import _butter_bandpass_filter, _moving_average

import numpy
from scipy.stats import linregress
from scipy.signal import filtfilt, butter

# Base packages used in OpenSignals Tools Notebooks for plotting data
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
output_notebook(hide_banner=True)


def detect_r_peaks(ecg_signal, sample_rate, time_units=False, volts=False, resolution=None,
                   device="biosignalsplux", plot_result=False):
    """
    -----
    Brief
    -----
    Python implementation of R peak detection algorithm (proposed by Raja Selvaraj).

    -----------
    Description
    -----------
    Pan-Tompkins algorithm is one of the gold-standard algorithms in R-peak detection on ECG due to its low
    computational complexity, which allows for real-time applications, preserving high accuracy values.

    This function allows the detection of these events in ECG signals using the Pan-Tompkins.

    ----------
    Parameters
    ----------
    ecg_signal : list
        List of ECG acquired samples.

    sample_rate : int
        Sampling frequency.

    time_units : boolean
        If True this function will return the R peak position in seconds.

    volts : boolean
        If True, then the conversion of raw units to mV will be done. Resolution needs to be
        specified.

    resolution : int or None
        Selected resolution for data acquisition.

    device : str
        Specification of the device category.

    plot_result : boolean
        If True it will be presented a graphical representation of the R peak position in the ECG
        signal.

    Returns
    -------
    out : R peak position (ndarray), R peak amplitude (ndarray)
        R peak position (sample number or time instant in seconds) and amplitude (raw or mV).

    """

    if volts is True:
        if resolution is not None:
            # ecg_signal = ((ecg_signal / 2 ** resolution) - 0.5) * 3
            ecg_signal = raw_to_phy("ECG", device, ecg_signal, resolution, option="mV")
        else:
            raise RuntimeError("For converting raw units to mV is mandatory the specification of "
                               "acquisition resolution.")

    if time_units is True:
        time = numpy.linspace(0, len(ecg_signal) / sample_rate, len(ecg_signal))
    else:
        time = numpy.linspace(0, len(ecg_signal) - 1, len(ecg_signal))

    # Filtering Step of Pan-Tompkins Algorithm.
    filtered = _ecg_band_pass_filter(ecg_signal, sample_rate)

    # Differentiation Step of Pan-Tompkins Algorithm.
    differentiated = _differentiate(filtered)

    # Rectification Step of Pan-Tompkins Algorithm.
    squared = _squaring(differentiated)

    # Integration Step of Pan-Tompkins Algorithm.
    integrated = _integration(squared, sample_rate)

    rr_buffer, spk1, npk1, threshold = _buffer_ini(integrated, sample_rate)
    probable_peaks, possible_peaks = _detects_peaks(integrated, sample_rate)
    definitive_peaks = _checkup(probable_peaks, integrated, sample_rate, rr_buffer, spk1, npk1,
                                threshold)
    definitive_peaks = list(map(int, definitive_peaks))

    # Rephasing step.
    definitive_peaks_rephase = numpy.array(definitive_peaks) - 30 * (sample_rate / 1000)
    definitive_peaks_rephase = list(map(int, definitive_peaks_rephase))

    if time_units is True:
        peaks = numpy.array(time)[definitive_peaks_rephase]
    else:
        peaks = definitive_peaks_rephase

    amplitudes = numpy.array(ecg_signal)[definitive_peaks_rephase]

    # If plot is invoked by plot_result flag, then a graphical representation of the R peaks is
    # presented to the user.
    if plot_result is True:
        time_int = numpy.array(time[1:])
        integrated = numpy.array(integrated)

        fig = figure(x_axis_label='Time (s)', y_axis_label='Raw Data',
                     **opensignals_kwargs("figure"))
        fig.line(time_int, integrated, **opensignals_kwargs("line"))
        fig.circle(time_int[definitive_peaks], integrated[definitive_peaks], size=30,
                   color="#00893E", legend_label="Definitive Peaks")
        fig.circle(time_int[probable_peaks], integrated[probable_peaks], size=20, color="#009EE3",
                   legend_label="Probable Peaks")
        fig.circle(time_int[possible_peaks], integrated[possible_peaks], size=10, color="#302683",
                   legend_label="Possible Peaks")

        fig2 = figure(x_axis_label='Time (s)', y_axis_label='Raw Data',
                      **opensignals_kwargs("figure"))
        fig2.line(time, ecg_signal, **opensignals_kwargs("line"))
        fig2.circle(time[definitive_peaks_rephase],
                    numpy.array(ecg_signal)[definitive_peaks_rephase],
                    size=30, color=opensignals_color_pallet(), legend_label="Definitive Peaks")

        opensignals_style([fig, fig2])

        grid_plot = gridplot([[fig], [fig2]], **opensignals_kwargs("gridplot"))
        show(grid_plot)

    return peaks, amplitudes


def detect_emg_activations(emg_signal, sample_rate, smooth_level=20, threshold_level=10,
                           time_units=False, volts=False, resolution=None, device="biosignalsplux",
                           plot_result=False):
    """
    -----
    Brief
    -----
    Python implementation of Burst detection algorithm using Teager Kaiser Energy Operator.

    -----------
    Description
    -----------
    Activation events in EMG readings correspond to an increase of muscular activity, namely, from inaction to action.
    These events are characterised by an increase in electric potential that returns to the initial values when the
    muscle returns to a state of inaction.

    This function detects activation events using the Teager Kaiser Energy Operator.

    ----------
    Parameters
    ----------
    emg_signal : list
        List of EMG acquired samples.

    sample_rate : int
        Sampling frequency.

    smooth_level : number
        Defines a percentage proportional to the smoothing level, i.e. the bigger this value is,
        the more smoothed is the signal.

    threshold_level : number
        Specification of the single threshold position, used for distinguishing between activation
        (above) and inactivation samples (below).

    time_units : boolean
        If True this function will return the Burst begin and end positions in seconds.

    volts : boolean
        If True, then the conversion of raw units to mV will be done. Resolution need to be
        specified.

    resolution : int
        Selected resolution for data acquisition.

    device : str
        Specification of the device category.

    plot_result : boolean
        If True it will be presented a graphical representation of the detected burst in the EMG
        signal.

    Returns
    -------
    out : bursts begin (ndarray), bursts end (ndarray)
        Begin and end of bursts (sample number or time instant in seconds).

    smooth_signal: list
        It is returned the smoothed EMG signal (after the processing steps intended to simplify the
        signal).

    threshold_level: float
        The value of the detection threshold used to locate the begin and end of each muscular
        activation period.
    """

    if volts is True:
        if resolution is not None:
            emg_signal = raw_to_phy("EMG", device, emg_signal, resolution, option="mV")
            units = "mV"
        else:
            raise RuntimeError(
                "For converting raw units to mV is mandatory the specification of acquisition "
                "resolution.")
    else:
        units = "Input Units"

    if time_units is True:
        time_units_str = "Time (s)"
        time = numpy.linspace(0, len(emg_signal) / sample_rate, len(emg_signal))
    else:
        time = numpy.linspace(0, len(emg_signal) - 1, len(emg_signal))
        time_units_str = "Sample Number"

    # ----------------------------------- Baseline Removal -----------------------------------------
    pre_pro_signal = numpy.array(emg_signal) - numpy.average(emg_signal)

    # ------------------------------------ Signal Filtering ----------------------------------------
    low_cutoff = 10  # Hz
    high_cutoff = 300  # Hz

    # Application of the signal to the filter.
    pre_pro_signal = _butter_bandpass_filter(pre_pro_signal, low_cutoff, high_cutoff, sample_rate)

    # ------------------------------ Application of TKEO Operator ----------------------------------
    tkeo = []
    for i, signal_sample in enumerate(pre_pro_signal):
        if i in (0, len(pre_pro_signal) - 1):
            tkeo.append(signal_sample)
        else:
            tkeo.append(numpy.power(signal_sample, 2) - (pre_pro_signal[i + 1] *
                                                         pre_pro_signal[i - 1]))

    # Smoothing level - Size of sliding window used during the moving average process (a function
    # of sampling frequency)
    smoothing_level = int((smooth_level / 100) * sample_rate)

    # --------------------------------- Signal Rectification ---------------------------------------
    rect_signal = numpy.absolute(tkeo)

    # ------------------------------ First Moving Average Filter -----------------------------------
    rect_signal = _moving_average(rect_signal, sample_rate / 10)

    # -------------------------------- Second Smoothing Phase --------------------------------------
    smooth_signal = []
    for i in range(0, len(rect_signal)):
        if smoothing_level < i < len(rect_signal) - smoothing_level:
            smooth_signal.append(numpy.mean(rect_signal[i - smoothing_level:i + smoothing_level]))
        else:
            smooth_signal.append(0)

    # ----------------------------------- Threshold -----------------------------------------------
    avg_pre_pro_signal = numpy.average(pre_pro_signal)
    std_pre_pro_signal = numpy.std(pre_pro_signal)

    threshold_level = avg_pre_pro_signal + _thres_norm_reg(threshold_level, smooth_signal,
                                                           pre_pro_signal) * std_pre_pro_signal

    # Generation of a square wave reflecting the activation and inactivation periods.
    binary_signal = []
    for i in range(0, len(time)):
        if smooth_signal[i] >= threshold_level:
            binary_signal.append(1)
        else:
            binary_signal.append(0)

    # ------------------------------ Begin and End of Bursts --------------------------------------
    diff_signal = numpy.diff(binary_signal)
    act_begin = numpy.where(diff_signal == 1)[0]
    act_end = numpy.where(diff_signal == -1)[0]

    if time_units is True:
        time_begin = numpy.array(time)[act_begin]
        time_end = numpy.array(time)[act_end]
    else:
        time_begin = act_begin
        time_end = act_end

    # If plot is invoked by plot_result flag, then a graphical representation of the R peaks is
    # presented to the user.
    if plot_result is True:
        plot([list(time), list(time)], [list(emg_signal), list(numpy.array(binary_signal) *
                                                               numpy.max(emg_signal))],
             yAxisLabel=["Data Samples (" + units + ")"] * 2,
             x_axis_label=time_units_str, legend_label=["EMG Signal", "Activation Signal"])

    return time_begin, time_end, smooth_signal, threshold_level


# ==================================================================================================
# ================================= Private Functions ==============================================
# ==================================================================================================

# [Pan-Tompkins R peak detection algorithm]
def _ecg_band_pass_filter(data, sample_rate):
    """
    Bandpass filter with a bandpass setting of 5 to 15 Hz

    ----------
    Parameters
    ----------
    data : list
        List with the ECG signal samples.
    sample_rate : int
        Sampling rate at which the acquisition took place.

    Returns
    -------
    out : list
        Filtered signal.
    """
    nyquist_sample_rate = sample_rate / 2.
    normalized_cut_offs = [5/nyquist_sample_rate, 15/nyquist_sample_rate]
    b_coeff, a_coeff = butter(2, normalized_cut_offs, btype='bandpass')[:2]
    return filtfilt(b_coeff, a_coeff, data, padlen=150)


def _differentiate(data):
    """
    Derivative nearly linear between dc and 30 Hz

    ----------
    Parameters
    ----------
    data : list
        Data samples of the signal where the first derivative estimate is done.

    Returns
    -------
    out : list
        List with the differences between consecutive samples (the length of this list is equal to
        len(data) - 1).

    """
    return numpy.diff(data)


def _squaring(data):
    """
    Squaring data point by point. Nonlinear amplification, emphasizing the higher
    frequencies

    ----------
    Parameters
    ----------
    data : ndarry
        Array that contains signal samples. Each sample value will be squared.

    Returns
    -------
    out : ndarray
        Squared signal.

    """
    return data * data


def _integration(data, sample_rate):
    """
    Moving window integration. N is the number of samples in the width of the integration
    window

    ----------
    Parameters
    ----------
    data : ndarray
        Samples of the signal where a moving window integration will be applied.
    sample_rate : int
        Sampling rate at which the acquisition took place.

    Returns
    -------
    out : ndarray
        Integrated signal samples.
    """
    wind_size = int(0.080 * sample_rate)
    int_ecg = numpy.zeros_like(data)
    cum_sum = data.cumsum()
    int_ecg[wind_size:] = (cum_sum[wind_size:] - cum_sum[:-wind_size]) / wind_size
    int_ecg[:wind_size] = cum_sum[:wind_size] / numpy.arange(1, wind_size + 1)

    return int_ecg


def _buffer_ini(data, sample_rate):
    """
    Initializes the buffer with eight 1s intervals

    ----------
    Parameters
    ----------
    data : ndarray
        Pre-processed ECG signal samples.
    sample_rate : int
        Sampling rate at which the acquisition took place.

    Returns
    -------
    rr_buffer : list
        Data structure that stores eight samples (in the future this buffer will store the duration
        of eight RR intervals instead of the 1 second values defined in initialisation).
    spk1 : float
        Initial value of SPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named signal peak).
    npk1 : int
        Initial value of NPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named noise peak).
    threshold : float
        Initial value of the adaptive threshold level (relevant parameter for the application of
        specific criteria during the identification of R peaks).

    Sources
    -------
    https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf


    """
    rr_buffer = [1] * 8
    spk1 = max(data[sample_rate:2*sample_rate])
    npk1 = 0
    threshold = _buffer_update(npk1, spk1)

    return rr_buffer, spk1, npk1, threshold


def _buffer_update(npk1, spk1):
    """
    Computes threshold based on signal and noise values

    ----------
    Parameters
    ----------
    npk1 : int
        Actual value of NPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named noise peak).
    spk1 : float
        Actual value of SPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named signal peak).

    Returns
    -------
    out : float
        The updated threshold level.

    """
    threshold = npk1 + 0.25 * (spk1 - npk1)

    return threshold


def _detects_peaks(ecg_integrated, sample_rate):
    """
    Detects peaks from local maximum

    ----------
    Parameters
    ----------
    ecg_integrated : ndarray
        Array that contains the samples of the integrated signal.
    sample_rate : int
        Sampling rate at which the acquisition took place.

    Returns
    -------
    choosen_peaks : list
        List of local maximums that pass the first stage of conditions needed to be considered as
        a R peak.
    possible_peaks : list
        List with all the local maximums in the signal.

    """

    # Minimum RR interval = 200 ms
    min_rr = (sample_rate / 1000) * 200

    # Computes all possible peaks and their amplitudes
    possible_peaks = [i for i in range(0, len(ecg_integrated)-1)
                      if ecg_integrated[i-1] < ecg_integrated[i] and
                      ecg_integrated[i] > ecg_integrated[i+1]]

    possible_amplitudes = [ecg_integrated[k] for k in possible_peaks]
    chosen_peaks = []

    # Starts with first peak
    if not possible_peaks:
        raise Exception("No Peaks Detected.")
    peak_candidate_i = possible_peaks[0]
    peak_candidate_amp = possible_amplitudes[0]
    for peak_i, peak_amp in zip(possible_peaks, possible_amplitudes):
        if peak_i - peak_candidate_i <= min_rr and peak_amp > peak_candidate_amp:
            peak_candidate_i = peak_i
            peak_candidate_amp = peak_amp
        elif peak_i - peak_candidate_i > min_rr:
            chosen_peaks += [peak_candidate_i - 6]  # Delay of 6 samples
            peak_candidate_i = peak_i
            peak_candidate_amp = peak_amp
        else:
            pass

    return chosen_peaks, possible_peaks


def _checkup(peaks, ecg_integrated, sample_rate, rr_buffer, spk1, npk1, threshold):
    """
    Check each peak according to thresholds

    ----------
    Parameters
    ----------
    peaks : list
        List of local maximums that pass the first stage of conditions needed to be considered as
        an R peak.
    ecg_integrated : ndarray
        Array that contains the samples of the integrated signal.
    sample_rate : int
        Sampling rate at which the acquisition took place.
    rr_buffer : list
        Data structure that stores the duration of the last eight RR intervals.
    spk1 : float
        Actual value of SPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named signal peak).
    npk1 : int
        Actual value of NPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named noise peak).
    threshold : float
        Initial value of the adaptive threshold level (relevant parameter for the application of
        specific criteria during the identification of R peaks).

    Returns
    -------
    out : list
        List with the position of the peaks considered as R peak by the algorithm.

    """
    peaks_amp = [ecg_integrated[peak] for peak in peaks]
    definitive_peaks = []
    for i, peak in enumerate(peaks):
        amp = peaks_amp[i]

        # accept if larger than threshold and slope in raw signal
        # is +-30% of previous slopes
        if amp > threshold:
            definitive_peaks, spk1, rr_buffer = _acceptpeak(peak, amp, definitive_peaks, spk1,
                                                            rr_buffer)

        # accept as qrs if higher than half threshold,
        # but is 360 ms after last qrs and next peak
        # is more than 1.5 rr intervals away
        # just abandon it if there is no peak before
        # or after
        elif amp > threshold / 2 and list(definitive_peaks) and len(peaks) > i + 1:
            mean_rr = numpy.mean(rr_buffer)
            last_qrs_ms = (peak - definitive_peaks[-1]) * (1000 / sample_rate)
            last_qrs_to_next_peak = peaks[i+1] - definitive_peaks[-1]

            if last_qrs_ms > 360 and last_qrs_to_next_peak > 1.5 * mean_rr:
                definitive_peaks, spk1, rr_buffer = _acceptpeak(peak, amp, definitive_peaks, spk1,
                                                                rr_buffer)
            else:
                npk1 = _noisepeak(amp, npk1)
        # if not either of these it is noise
        else:
            npk1 = _noisepeak(amp, npk1)
        threshold = _buffer_update(npk1, spk1)

    definitive_peaks = numpy.array(definitive_peaks)

    return definitive_peaks


def _acceptpeak(peak, amp, definitive_peaks, spk1, rr_buffer):
    """
    Private function intended to insert a new RR interval in the buffer.

    ----------
    Parameters
    ----------
    peak : int
        Sample where the peak under analysis is located.
    amp : int
        Amplitude of the peak under analysis.
    definitive_peaks : list
        List with the definitive_peaks stored until the present instant.
    spk1 : float
        Actual value of SPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named signal peak).
    rr_buffer : list
        Data structure that stores the duration of the last eight RR intervals.

    Returns
    -------
    definitive_peaks_out : list
        Definitive peaks list.
    spk1 : float
        Updated value of SPK1 parameter.
    rr_buffer : list
        Buffer after appending a new RR interval and excluding the oldest one.

    """

    definitive_peaks_out = definitive_peaks
    definitive_peaks_out = numpy.append(definitive_peaks_out, peak)
    spk1 = 0.125 * amp + 0.875 * spk1  # spk1 is the running estimate of the signal peak
    if len(definitive_peaks_out) > 1:
        rr_buffer.pop(0)
        rr_buffer += [definitive_peaks_out[-1] - definitive_peaks_out[-2]]

    return numpy.array(definitive_peaks_out), spk1, rr_buffer


def _noisepeak(amp, npk1):
    """
    Private function intended to insert a new RR interval in the buffer.

    ----------
    Parameters
    ----------
    amp : int
        Amplitude of the peak under analysis.
    npk1 : int
        Actual value of NPK1 parameter defined in Pan-Tompkins real-time R peak detection algorithm
        (named noise peak).

    Returns
    -------
    npk1 : float
        Updated value of NPK1 parameter.
    """
    npk1 = 0.125 * amp + 0.875 * npk1  # npk1 is the running estimate of the noise peak

    return npk1


def tachogram(data, sample_rate, signal=False, in_seconds=False, out_seconds=False):
    """
    Function for generation of ECG Tachogram.

    ----------
    Parameters
    ----------
    data : list
        ECG signal or R peak list. When the input is a raw signal the input flag signal should be
        True.

    sample_rate : int
        Sampling frequency.

    signal : boolean
        If True, then the data argument contains the set of the ECG acquired samples.

    in_seconds : boolean
        If the R peaks list defined as the input argument "data" contains the sample numbers where
        the R peaks occur, then in_seconds needs to be False.

    out_seconds : boolean
        If True then each sample of the returned time axis is expressed in seconds.

    Returns
    -------
    out : list, list
        List of tachogram samples. List of instants where each cardiac cycle ends.

    """

    if signal is False:  # data is a list of R peaks position.
        data_copy = data
        time_axis = numpy.array(data)#.cumsum()
        if out_seconds is True and in_seconds is False:
            time_axis = time_axis / sample_rate
    else:  # data is a ECG signal.
        # Detection of R peaks.
        data_copy = detect_r_peaks(data, sample_rate, time_units=out_seconds, volts=False,
                                   resolution=None, plot_result=False)[0]
        time_axis = data_copy

    # Generation of Tachogram.
    tachogram_data = numpy.diff(time_axis)
    tachogram_time = time_axis[1:]

    return tachogram_data, tachogram_time


# [Muscular Activation Detection Algorithm]

def _thres_norm_reg(threshold_level, signal, pre_smooth_signal):
    """
    Regression function that with a percent input gives an absolute value of the threshold
    level (used in the muscular activation detection algorithm).
    Converts a relative threshold level to an absolute value.

    ----------
    Parameters
    ----------
    threshold_level : int
        Percentage value that defines the absolute threshold level relatively to the maximum value
        of signal.
    signal : list
        List of EMG smoothed signal samples.
    pre_smooth_signal : list
        Original EMG samples.

    Returns
    -------
    out : float
        Threshold level in absolute format.

     """
    avg_signal = numpy.average(pre_smooth_signal)
    std_signal = numpy.std(pre_smooth_signal)

    threshold_0_perc_level = (-avg_signal) / float(std_signal)
    threshold_100_perc_level = (numpy.max(signal) - avg_signal) / float(std_signal)

    slope, b_coeff = linregress([0, 100], [threshold_0_perc_level, threshold_100_perc_level])[:2]
    return slope * threshold_level + b_coeff

# 01/10/2018 19h19m :)
