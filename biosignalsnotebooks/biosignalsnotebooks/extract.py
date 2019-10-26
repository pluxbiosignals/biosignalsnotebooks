
"""
Ensures to the user that he can extract multiple parameters from a specific electrophysiological
signal at once.

Available Functions
-------------------
[Public]

hrv_parameters
    Function for extracting HRV parameters from time and frequency domains.
remove_ectopy
    Application of a clinical criterion used for detecting and removing ectopic beats in ECG signal.
psd
    Determination of the Power Spectral Density Function (Fourier Domain)
emg_paramaters
    Function for extracting EMG parameters from time and frequency domains.
fatigue_eval_med_freq
    Returns the evolution time series of EMG median frequency along the acquisition, based on
    a sliding window mechanism.

Observations/Comments
---------------------
None

/\
"""

import numpy
import scipy.signal as scisignal
import scipy.interpolate as interpol
import scipy.integrate as integr
import pandas
from bokeh.models import BoxAnnotation
from bokeh.plotting import show
from bokeh.layouts import gridplot
from .detect import tachogram, detect_emg_activations
from .conversion import raw_to_phy
from .visualise import plot, opensignals_kwargs, opensignals_color_pallet


def hrv_parameters(data, sample_rate, signal=False, in_seconds=False):
    """
    -----
    Brief
    -----
    Function for extracting HRV parameters from time and frequency domains.

    -----------
    Description
    -----------
    ECG signals require specific processing due to their cyclic nature. For example, it is expected that in similar
    conditions the RR peak interval to be similar, which would mean that the heart rate variability (HRV) would be
    constant.

    In this function, it is calculated the tachogram of the input ECG signal, that allows to understand the variability
    of the heart rate by the calculus of the time difference between consecutive RR peaks. Thus, different features
    may be extracted from the tachogram, such as, maximum, minimum and average RR peak interval.

    This function extracts a wide range of features related to the HRV and returns them as a dictionary.

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

    Returns
    -------
    out : dict
        Dictionary with HRV parameters values, with keys:
            MaxRR : Maximum RR interval
            MinRR : Minimum RR interval
            AvgRR : Average RR interval
            MaxBPM : Maximum RR interval in BPM
            MinBPM : Minimum RR interval in BPM
            AvgBPM : Average RR interval in BPM
            SDNN : Standard deviation of the tachogram
            SD1 : Square root of half of the sqaured standard deviation of the differentiated tachogram
            SD2 : Square root of double of the squared SD1 minus the SD2 squared
            SD1/SD2 : quotient between SD1 and SD2
            NN20 : Number of consecutive heartbeats with a difference larger than 20 ms
            pNN20 : Relative number of consecutive heartbeats with a difference larger than 20 ms
            NN50 : Number of consecutive heartbeats with a difference larger than 50 ms
            pNN50 : Relative number of consecutive heartbeats with a difference larger than 50 ms
            ULF_Power : Power of the spectrum between 0 and 0.003 Hz
            VLF_Power : Power of the spectrum between 0.003 and 0.04 Hz
            LF_Power : Power of the spectrum between 0.04 and 0.15 Hz
            HF_Power : Power of the spectrum between 0.15 and 0.40 Hz
            LF_HF_Ratio : Quotient between the values of LF_Power and HF_Power
            Total_Power : Power of the whole spectrum
    """

    out_dict = {}

    # Generation of tachogram.
    tachogram_data, tachogram_time = tachogram(data, sample_rate, signal=signal,
                                               in_seconds=in_seconds, out_seconds=True)

    # Ectopy Removal.
    tachogram_data_nn = remove_ectopy(tachogram_data, tachogram_time)[0]

    # Determination of heart rate in BPM.
    # bpm_data = (1 / numpy.array(tachogram_data_nn)) * 60

    # ================================== Time Parameters ==========================================
    # Maximum, Minimum and Average RR Interval.
    out_dict["MaxRR"] = numpy.max(tachogram_data_nn)
    out_dict["MinRR"] = numpy.min(tachogram_data_nn)
    out_dict["AvgRR"] = numpy.average(tachogram_data_nn)

    # Maximum, Minimum and Average Heart Rate.
    max_hr = 1 / out_dict["MinRR"]  # Cycles per second.
    out_dict["MaxBPM"] = max_hr * 60  # BPM

    min_hr = 1 / out_dict["MaxRR"]  # Cycles per second.
    out_dict["MinBPM"] = min_hr * 60  # BPM

    avg_hr = 1 / out_dict["AvgRR"]  # Cyles per second.
    out_dict["AvgBPM"] = avg_hr * 60  # BPM

    # SDNN.
    out_dict["SDNN"] = numpy.std(tachogram_data_nn)

    # ================================ Poincaré Parameters ========================================
    # Auxiliary Structures.
    tachogram_diff = numpy.diff(tachogram_data)
    sdsd = numpy.std(tachogram_diff)

    # Poincaré Parameters.
    out_dict["SD1"] = numpy.sqrt(0.5 * numpy.power(sdsd, 2))
    out_dict["SD2"] = numpy.sqrt(2 * numpy.power(out_dict["SDNN"], 2) -
                                 numpy.power(out_dict["SD1"], 2))
    out_dict["SD1/SD2"] = out_dict["SD1"] / out_dict["SD2"]

    # ============================= Additional Parameters =========================================
    tachogram_diff_abs = numpy.fabs(tachogram_diff)

    # Number of RR intervals that have a difference in duration, from the previous one, of at least
    # 20 ms.
    out_dict["NN20"] = sum(1 for i in tachogram_diff_abs if i > 0.02)
    out_dict["pNN20"] = int(float(out_dict["NN20"]) / len(tachogram_diff_abs) * 100)  # % value.

    # Number of RR intervals that have a difference in duration, from the previous one, of at least
    # 50 ms.
    out_dict["NN50"] = sum(1 for i in tachogram_diff_abs if i > 0.05)
    out_dict["pNN50"] = int(float(out_dict["NN50"]) / len(tachogram_diff_abs) * 100)  # % value.

    # =============================== Frequency Parameters ========================================
    # Auxiliary Structures.
    freqs, power_spect = psd(tachogram_time, tachogram_data)  # Power spectrum.

    # Frequency Parameters.
    freq_bands = {"ulf_band": [0.00, 0.003], "vlf_band": [0.003, 0.04], "lf_band": [0.04, 0.15],
                  "hf_band": [0.15, 0.40]}
    power_band = {}
    total_power = 0

    band_keys = freq_bands.keys()
    for band in band_keys:
        freq_band = freq_bands[band]
        freq_samples_inside_band = [freq for freq in freqs if freq_band[0] <= freq <= freq_band[1]]
        power_samples_inside_band = [power_val for power_val, freq in zip(power_spect, freqs) if
                                     freq_band[0] <= freq <= freq_band[1]]
        power = numpy.round(integr.simps(power_samples_inside_band, freq_samples_inside_band), 5)

        # Storage of power inside band.
        power_band[band] = {}
        power_band[band]["Power Band"] = power
        power_band[band]["Freqs"] = freq_samples_inside_band
        power_band[band]["Power"] = power_samples_inside_band

        # Total power update.
        total_power = total_power + power

    out_dict["ULF_Power"] = power_band["ulf_band"]["Power Band"]
    out_dict["VLF_Power"] = power_band["vlf_band"]["Power Band"]
    out_dict["LF_Power"] = power_band["lf_band"]["Power Band"]
    out_dict["HF_Power"] = power_band["hf_band"]["Power Band"]
    out_dict["LF_HF_Ratio"] = power_band["lf_band"]["Power Band"] / power_band["hf_band"]["Power Band"]
    out_dict["Total_Power"] = total_power

    return out_dict


def remove_ectopy(tachogram_data, tachogram_time):
    """
    -----
    Brief
    -----
    Function for removing ectopic beats.

    -----------
    Description
    -----------
    Ectopic beats are beats that are originated in cells that do not correspond to the expected pacemaker cells. These
    beats are identifiable in ECG signals by abnormal rhythms.

    This function allows to remove the ectopic beats by defining time thresholds that consecutive heartbeats should
    comply with.

    ----------
    Parameters
    ----------
    tachogram_data : list
        Y Axis of tachogram.

    tachogram_time : list
        X Axis of tachogram.

    Returns
    -------
    out : list, list
        List of tachogram samples. List of instants where each cardiac cycle ends.

    Source
    ------
    "Comparison of methods for removal of ectopy in measurement of heart rate variability" by
    N. Lippman, K. M. Stein and B. B. Lerman.
    """

    # If the i RR interval differs from i-1 by more than 20 % then it will be removed from analysis.
    remove_margin = 0.20
    finish_ectopy_remove = False

    signal = list(tachogram_data)
    time = list(tachogram_time)

    # Sample by sample analysis.
    beat = 1
    while finish_ectopy_remove is False:
        max_thresh = signal[beat - 1] + remove_margin * signal[beat - 1]
        min_thresh = signal[beat - 1] - remove_margin * signal[beat - 1]
        if signal[beat] > max_thresh or signal[beat] < min_thresh:
            if beat <= len(signal) - 2:
                signal.pop(beat)
                signal.pop(beat)
                time.pop(beat)
                time.pop(beat)
            # To remove the influence of the ectopic beat we need to exclude the RR
            # intervals "before" and "after" the ectopic beat.
            # [NB <RRi> NB <RRi+1> EB <RRi+2> NB <RRi+3> NB...] -->
            # --> [NB <RRi> NB cut NB <RRi+3> NB...]

            # Advance "Pointer".
            beat += 1
        else:
            # Advance "Pointer".
            beat += 1

        # Verification if the cycle should or not end.
        if beat >= len(signal):
            finish_ectopy_remove = True

    return signal, time


def psd(tachogram_time, tachogram_data):
    """
    -----
    Brief
    -----
    Determination of the Power Spectral Density Function (Fourier Domain)

    -----------
    Description
    -----------
    The Power Spectral Density Function allows to perceive the behavior of a given signal in terms of its frequency.
    This procedure costs the time resolution of the signal but may be important to extract features in a different
    domain appart from the time domain.

    This function constructs the Power Spectral Density Function in the frequency domain.

    ----------
    Parameters
    ----------
    tachogram_time : list
        X Axis of tachogram.
    tachogram_data : list
        Y Axis of tachogram.

    Returns
    -------
    out : list, list
        Frequency and power axis.
    """

    init_time = tachogram_time[0]
    fin_time = tachogram_time[-1]
    tck = interpol.splrep(tachogram_time, tachogram_data)
    interpolation_rate = 4

    nn_time_even = numpy.linspace(init_time, fin_time, (fin_time - init_time) * interpolation_rate)
    nn_tachogram_even = interpol.splev(nn_time_even, tck)

    freq_axis, power_axis = scisignal.welch(nn_tachogram_even, interpolation_rate,
                                            window=scisignal.get_window("hanning",
                                                                        min(len(nn_tachogram_even),
                                                                            1000)),
                                            nperseg=min(len(nn_tachogram_even), 1000))

    freqs = [round(val, 3) for val in freq_axis if val < 0.5]
    power = [round(val, 4) for val, freq in zip(power_axis, freq_axis) if freq < 0.5]

    return freqs, power


def emg_parameters(data, sample_rate, raw_to_mv=True, device="biosignalsplux", resolution=16):
    """
    -----
    Brief
    -----
    Function for extracting EMG parameters from time and frequency domains.

    -----------
    Description
    -----------
    EMG signals have specific properties that are different from other biosignals. For example, it is not periodic,
    contrary to ECG signals.
    This type of biosignals are composed of activation and inactivation periods that are different from one another.
    Specifically, there differences in the amplitude domain, in which the activation periods are characterised by an
    increase of amplitude.

    This function allows the extraction of a wide range of features specific of EMG signals.

    ----------
    Parameters
    ----------
    data : list
        EMG signal.

    sample_rate : int
        Sampling frequency.

    raw_to_mv : boolean
        If True then it is assumed that the input samples are in a raw format and the output
        results will be in mV.
        When True "device" and "resolution" inputs became mandatory.

    device : str
        PLUX device label:
        - "bioplux"
        - "bioplux_exp"
        - "biosignalsplux"
        - "rachimeter"
        - "channeller"
        - "swifter"
        - "ddme_openbanplux"

    resolution : int
        Resolution selected during acquisition.

    Returns
    -------
    out : dict
        Dictionary with EMG parameters values, with keys:
            Maximum Muscular Activation Duration : Duration of the longest activation in the EMG signal
            Minimum Muscular Activation Duration : Duration of the shortest activation in the EMG signal
            Average Muscular Activation Duration : Average duration of the activations in the EMG signal
            Standard Deviation of Burst Duration : Standard Deviation duration of the activations in the EMG signal
            Maximum Sample Value : Maximum value of the EMG signal
            Minimum Sample Value : Minimum value of the EMG signal
            Average Sample Value : Average value of the EMG signal
            Standard Deviation Sample Value : Standard deviation value of the EMG signal
            RMS : Root mean square of the EMG signal
            Area : Area under the curve of the EMG signal
            Total Power Spect : Total power of the power spectrum of the EMG signal
            Median Frequency : Median frequency of the EMG signal calculated using the power spectrum of the EMG signal
            Maximum Power Frequency : Frequency correspondent to the maximum amplitude in the power spectrum of the EMG
                                      signal
    """

    out_dict = {}

    # Conversion of data samples to mV if requested by raw_to_mv input.
    if raw_to_mv is True:
        data = raw_to_phy("EMG", device, data, resolution, option="mV")

    # Detection of muscular activation periods.
    burst_begin, burst_end = detect_emg_activations(data, sample_rate, smooth_level=20,
                                                    threshold_level=10, time_units=True)[:2]

    # --------------------------- Number of activation periods. -----------------------------------
    out_dict["Number of Muscular Activations"] = len(burst_begin)

    # ----------- Maximum, Minimum and Average duration of muscular activations. ------------------
    # Bursts Duration.
    bursts_time = burst_end - burst_begin

    # Parameter extraction.
    out_dict["Maximum Muscular Activation Duration"] = numpy.max(bursts_time)
    out_dict["Minimum Muscular Activation Duration"] = numpy.min(bursts_time)
    out_dict["Average Muscular Activation Duration"] = numpy.average(bursts_time)
    out_dict["Standard Deviation of Muscular Activation Duration"] = numpy.std(bursts_time)

    # --------- Maximum, Minimum, Average and Standard Deviation of EMG sample values -------------
    # Maximum.
    out_dict["Maximum Sample Value"] = numpy.max(data)

    # Minimum.
    out_dict["Minimum Sample Value"] = numpy.min(data)

    # Average and Standard Deviation.
    out_dict["Average Sample Value"] = numpy.average(data)
    out_dict["Standard Deviation Sample Value"] = numpy.std(data)

    # ---------- Root Mean Square and Area under the curve (Signal Intensity Estimators) ----------
    # Root Mean Square.
    out_dict["RMS"] = numpy.sqrt(numpy.sum(numpy.array(data) * numpy.array(data)) / len(data))

    # Area under the curve.
    out_dict["Area"] = integr.cumtrapz(data)[-1]

    # -------------------- Total power and frequency reference points -----------------------------
    # Signal Power Spectrum.
    freq_axis, power_axis = scisignal.welch(data, fs=sample_rate, window='hanning', noverlap=0,
                                            nfft=int(256.))

    # Total Power and Median Frequency (Frequency that divides the spectrum into two regions with
    # equal power).
    area_power_spect = integr.cumtrapz(power_axis, freq_axis, initial=0)
    out_dict["Total Power Spect"] = area_power_spect[-1]
    out_dict["Median Frequency"] = freq_axis[numpy.where(area_power_spect >=
                                                         out_dict["Total Power Spect"] / 2)[0][0]]
    out_dict["Maximum Power Frequency"] = freq_axis[numpy.argmax(power_axis)]

    return out_dict


def fatigue_eval_med_freq(data, sample_rate, time_units=True, raw_to_mv=True,
                          device="biosignalsplux", resolution=16, show_plot=False):
    """
    -----
    Brief
    -----
    Returns the evolution time series of EMG median frequency along the acquisition, based on a sliding window
    mechanism.

    -----------
    Description
    -----------
    The median frequency of activation events in EMG signal is particularly important in fatigue evaluation methods.

    This function calculates the median frequency of each activation period and allows to plot those values in order to
    see the temporal evolution of this particular feature.

    ----------
    Parameters
    ----------
    data : list
        EMG signal.

    sample_rate : int
        Sampling frequency.

    time_units : boolean
        If True this function will return the x axis samples in seconds.

    raw_to_mv : boolean
        If True then it is assumed that the input samples are in a raw format and the output
        results will be in mV. When True "device" and "resolution" inputs became mandatory.

    device : str
        PLUX device label:
        - "bioplux"
        - "bioplux_exp"
        - "biosignalsplux"
        - "rachimeter"
        - "channeller"
        - "swifter"
        - "ddme_openbanplux"

    resolution : int
        Resolution selected during acquisition.

    show_plot : boolean
        If True, then a figure with the median frequency evolution will be shown.

    Returns
    -------
    out : pandas.DataFrame
        DataFrame with the time and the sequence of median frequency evolution.
    """

    # Conversion of data samples to mV if requested by raw_to_mv input.
    if raw_to_mv is True:
        data = raw_to_phy("EMG", device, data, resolution, option="mV")

    # Definition of the time axis.
    if time_units is True:
        time = numpy.linspace(0, len(data) / sample_rate, len(data))
    else:
        time = numpy.linspace(0, len(data) - 1, len(data))

    # Detection of muscular activation periods.
    burst_begin, burst_end = detect_emg_activations(data, sample_rate, smooth_level=20,
                                                    threshold_level=10, time_units=False,
                                                    volts=True, resolution=resolution,
                                                    device=device, plot_result=False)[:2]

    # Iteration along bursts.
    median_freq_data = []
    median_freq_time = []
    for burst in range(0, len(burst_begin)):
        processing_window = data[burst_begin[burst]:burst_end[burst]]
        central_point = (burst_begin[burst] + burst_end[burst]) / 2
        median_freq_time.append(central_point / sample_rate)

        # Generation of the processing window power spectrum.
        freqs, power = scisignal.welch(processing_window, fs=sample_rate, window='hanning',
                                       noverlap=0, nfft=int(256.))

        # Determination of median power frequency.
        area_freq = integr.cumtrapz(power, freqs, initial=0)
        total_power = area_freq[-1]
        median_freq_data.append(freqs[numpy.where(area_freq >= total_power / 2)[0][0]])

    # Graphical Representation step.
    if show_plot is True:
        list_figures_1 = plot([list(time), list(median_freq_time)],
                              [list(data), list(median_freq_data)],
                              title=["EMG Acquisition highlighting bursts",
                                     "Median Frequency Evolution"], gridPlot=True,
                              gridLines=2, gridColumns=1, openSignalsStyle=True,
                              x_axis_label="Time (s)",
                              yAxisLabel=["Raw Data", "Median Frequency (Hz)"],
                              x_range=[0, 125], show_plot=False)

        # Highlighting processing window.
        for burst in range(0, len(burst_begin)):
            color = opensignals_color_pallet()
            box_annotation = BoxAnnotation(left=burst_begin[burst] / sample_rate,
                                           right=burst_end[burst] / sample_rate, fill_color=color,
                                           fill_alpha=0.1)
            box_annotation_copy = BoxAnnotation(left=burst_begin[burst] / sample_rate,
                                                right=burst_end[burst] / sample_rate,
                                                fill_color=color, fill_alpha=0.1)
            list_figures_1[0].add_layout(box_annotation)
            list_figures_1[1].add_layout(box_annotation_copy)

        gridplot_1 = gridplot([[list_figures_1[0]], [list_figures_1[1]]],
                              **opensignals_kwargs("gridplot"))
        show(gridplot_1)

    # pandas.DataFrame(a, columns=a.keys())
    # pandas.DataFrame([a], columns=a.keys())
    return pandas.DataFrame({"Time (s)": median_freq_time,
                             "Median Frequency (Hz)": median_freq_data},
                            columns=["Time (s)", "Median Frequency (Hz)"])

# 25/09/2018 18h58m :)
