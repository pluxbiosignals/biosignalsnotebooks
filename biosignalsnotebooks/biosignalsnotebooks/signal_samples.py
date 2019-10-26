"""
biosignalsnotebooks module responsible for loading data from the available signal samples (used on
biosignalsnotebooks Notebooks).

Available Functions
-------------------
[Public]

load_signal
    Function that returns a dictionary with the data contained inside a signal sample file
    (stored in the biosignalsnotebooks signal samples directory).

[Private]

_generate_download_google_link
    Google Drive sharable links do not allow a direct download with wget function, so, this private
    function manipulates the input link to ensure the desired download.

Observations/Comments
---------------------
None

/\
"""

# =================================================================================================
# ====================================== Import Statements ========================================
# =================================================================================================
import os
from .load import load
from .aux_functions import _generate_download_google_link

SIGNAL_PATH = (os.path.abspath(__file__).split(os.path.basename(__file__))[0] + \
              "notebook_files\\osf_files\\signal_samples\\").replace("\\", "/")
# TODO Substitute \\ by os.sep to work on all operative systems
FILE_EXTENSION = ".h5"


def load_signal(signal_handler, get_header=False):
    """
    -----
    Brief
    -----
    Function that returns a dictionary with the data contained inside 'signal_name' file (stored in
    the biosignalsnotebooks signal samples directory).

    -----------
    Description
    -----------
    Biosignalsnotebooks library provides data samples in order to the users that are new to biosignals data handling to
    have a place to start without the need to acquire new data. This sample files are stored in the folder
    _signal_samples inside the library.

    This function returns the data from the selected sample.

    ----------
    Parameters
    ----------
    signal_name : file name or url
        Name that identifies the signal sample to be loaded or a url.

        Possible values:
        [ecg_4000_Hz]
        =================   ==============
        Signal Type                    ECG
        Acquisition Time           00:12.4
        Sample Rate                4000 Hz
        Number of Channels               1
        Conditions                 At Rest
        =================   ==============

        [ecg_5_min]
        =================   ==============
        Signal Type                    ECG
        Acquisition Time           05:00.0
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions                 At Rest
        =================   ==============

        [ecg_sample]
        =================   ==============
        Signal Type                    ECG
        Acquisition Time           00:11.9
        Sample Rate                 200 Hz
        Number of Channels               1
        Conditions                 At Rest
        =================   ==============

        [ecg_20_sec_10_Hz]
        =================   ==============
        Signal Type                    ECG
        Acquisition Time           00:20.0
        Sample Rate                  10 Hz
        Number of Channels               1
        Conditions                 At Rest
                             using Lead II
        =================   ==============

        [ecg_20_sec_100_Hz]
        =================   ==============
        Signal Type                    ECG
        Acquisition Time           00:19.7
        Sample Rate                 100 Hz
        Number of Channels               1
        Conditions                 At Rest
                             using Lead II
        =================   ==============

        [ecg_20_sec_1000_Hz]
        =================   ==============
        Signal Type                    ECG
        Acquisition Time           00:20.4
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions                 At Rest
                             using Lead II
        =================   ==============

        [emg_bursts]
        =================   ==============
        Signal Type                    EMG
        Muscle              Biceps Brachii
        Acquisition Time           00:28.5
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions             Cyclic
                               Contraction
        =================   ==============

        [emg_fatigue]
        =================   ==============
        Signal Type                    EMG
        Muscle              Biceps Brachii
        Acquisition Time           02:06.9
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions          Cyclic Flexion
                            and Extension
                            for fatigue
                            induction
        =================   ==============

        [temp_res_8_16]
        =================   ==============
        Signal Type            Temperature
        Acquisition Time           03:53.1
        Sample Rate                1000 Hz
        Number of Channels               2
        Resolutions          8 and 16 bits
        Conditions           Temperature
                             increase and
                             decrease
        =================   ==============

        [bvp_sample]
        =================   ==============
        Signal Type                    BVP
        Acquisition Time           00:27.3
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions                 At Rest
        =================   ==============

        [eeg_sample_closed_open_eyes]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           04:02.0
        Sample Rate                1000 Hz
        Number of Channels               2
        Conditions           Detection of
                             neuronal alpha
                             waves while
                             eyes are
                             opened or
                             closed
        =================   ==============

        [eeg_sample_artefacts_seg1]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           02:08.5
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           An EEG acqui-
                             sition which
                             contains
                             movement
                             artefacts
                             [Segment 1]
        =================   ==============

        [eeg_sample_artefacts_seg2]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           01:49.2
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           An EEG acqui-
                             sition which
                             contains
                             movement
                             artefacts
                             [Segment 2]
        =================   ==============

        [eeg_sample_artefacts_seg3]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           01:30.6
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           An EEG acqui-
                             sition which
                             contains
                             noisy data
                             with electro-
                             magnetic origin
                             Segment 3]
        =================   ==============

        [eeg_sample_0cm_h]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           03:59.7
        Sample Rate                1000 Hz
        Number of Channels               2
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed at the
                             Occipital line
                             connecting O1
                             and O2 positions
                             [Space between
                             electrodes = 0 cm]
        =================   ==============

        [eeg_sample_1cm_h]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           04:02.6
        Sample Rate                1000 Hz
        Number of Channels               2
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed at the
                             Occipital line
                             connecting O1
                             and O2 positions
                             [Space between
                             electrodes = 1 cm]
        =================   ==============

        [eeg_sample_2cm_h]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           04:17.9
        Sample Rate                1000 Hz
        Number of Channels               2
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed at the
                             Occipital line
                             connecting O1
                             and O2 positions
                             [Space between
                             electrodes = 2 cm]
        =================   ==============

        [eeg_sample_0cm_v]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           04:03.4
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed perpen-
                             dicularly to
                             the Occipital
                             line connecting
                             O1 and O2
                             positions
                             [Space between
                             electrodes = 0 cm]
        =================   ==============

        [eeg_sample_1cm_v]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           04:01.8
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed perpen-
                             dicularly to
                             the Occipital
                             line connecting
                             O1 and O2
                             positions
                             [Space between
                             electrodes = 1 cm]
        =================   ==============

        [eeg_sample_2cm_v]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           05:02.5
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed perpen-
                             dicularly to
                             the Occipital
                             line connecting
                             O1 and O2
                             positions
                             [Space between
                             electrodes = 2 cm]
        =================   ==============

        [eeg_sample_o]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           03:59.3
        Sample Rate                1000 Hz
        Number of Channels               2
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed at O1
                             and O2 positions
        =================   ==============

        [eeg_sample_p]
        =================   ==============
        Signal Type                    EEG
        Acquisition Time           04:02.3
        Sample Rate                1000 Hz
        Number of Channels               2
        Conditions           An EEG acquis-
                             ition with the
                             exploratory
                             electrodes
                             placed at P3
                             and P4 positions
        =================   ==============

        [emg_1000_hz_16_bits_solo]
        =================   ==============
        Signal Type                    EMG
        Acquisition Time           01:27.6
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           EMG acquisition
                             from Adductor
                             pollicis muscle
                             (1000 Hz and
                             16 bits)
        =================   ==============

        [emg_1000_hz_16_bits_solo]
        =================   ==============
        Signal Type                    EMG
        Acquisition Time           01:27.6
        Sample Rate                1000 Hz
        Number of Channels               1
        Conditions           EMG acquisition
                             from Adductor
                             pollicis muscle
                             (1000 Hz and
                             16 bits)
        =================   ==============

    get_header : boolean
        If True the file header will be returned as one of the function outputs.

    Returns
    -------
    out : dict
        A dictionary with the data stored inside the file specified in the input 'signal_name'.

    header : dict
        Metadata of the acquisition file (includes sampling rate, resolution, used device...)
    """

    primordial_list_signals = ["ecg_4000_Hz", "ecg_5_min", "ecg_sample", "ecg_20_sec_10_Hz",
                               "ecg_20_sec_100_Hz", "ecg_20_sec_1000_Hz", "emg_bursts", "emg_fatigue",
                               "temp_res_8_16", "bvp_sample", "eeg_sample_closed_open_eyes",
                               "eeg_sample_artefacts_seg1", "eeg_sample_artefacts_seg2", "eeg_sample_artefacts_seg3",
                               "eeg_sample_0cm_h", "eeg_sample_1cm_h", "eeg_sample_2cm_h", "eeg_sample_0cm_v",
                               "eeg_sample_1cm_v", "eeg_sample_2cm_v", "eeg_sample_o", "eeg_sample_p"]

    # Check if signal_handler is a url.
    # [Statements to be executed if signal_handler is a url]
    if any(mark in signal_handler for mark in ["http://", "https://", "www.", ".pt", ".com", ".org",
                                               ".net"]):
        # Check if it is a Google Drive sharable link.
        if "drive.google" in signal_handler:
            signal_handler = _generate_download_google_link(signal_handler)

        # Load file.
        out, header = load(signal_handler, remote=True, get_header=True, signal_sample=True)

    # [Statements to be executed if signal_handler is an identifier of the signal]
    else:
        list_files = list_signal_samples()
        if signal_handler in primordial_list_signals or signal_handler in list_files:
            out, header = load(SIGNAL_PATH + signal_handler + FILE_EXTENSION, get_header=True, signal_sample=True)
        else:
            raise RuntimeError("The signal name defined as input does not correspond to any of the "
                           "signal samples contained in the package.")

    if get_header is True:
        return out, header
    else:
        return out

def list_signal_samples():
    """
    -----
    Brief
    -----
    A "getter" that returns all signal samples filenames.

    -----------
    Description
    -----------
    The current function is a simpler "getter" returning the list of files inside SIGNALS_PATH with .h5 extension, i.e.,
    the files containing physiological data.

    Returns
    -------
    out : list
        A list containing all valid .h5 files.
    """

    # Get the complete list of files inside SIGNALS_PATH.
    list_files = os.listdir(SIGNAL_PATH)
    valid_files = []
    for file in list_files:
        if ".h5" in file:
            valid_files.append(file.split('.h5')[0])

    return valid_files

# 11/10/2018 16h45m :)
