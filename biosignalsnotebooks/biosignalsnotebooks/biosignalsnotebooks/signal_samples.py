"""
biosignalsnotebooks module responsible for loading data from the available signal samples (used on
biosignalsnotebooks Notebooks).

Available Functions
-------------------
[Public]

load_signal
    Function that returns a dictionary with the data contained inside a signal sample file
    (stored in the biosignalsnotebooks signal samples directory).

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

SIGNAL_PATH = os.path.abspath(__file__).split(os.path.basename(__file__))[0] + \
              "notebook_files\\osf_files\\signal_samples\\"
FILE_EXTENSION = ".h5"


def load_signal(signal_name, get_header=False):
    """
    Function that returns a dictionary with the data contained inside 'signal_name' file (stored in
    the biosignalsnotebooks signal samples directory.

    ----------
    Parameters
    ----------
    signal_name : file name
        Name that identifies the signal sample to be loaded.

        Possible values:
        [ecg_4000_hz]
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

    get_header : boolean
        If true the file header will be returned as one of the function outputs.

    Returns
    -------
    out : dict
        A dictionary with the data stored inside the file specified in the input 'signal_name'.

    header : dict
        Metadata of the acquisition file (includes sampling rate, resolution, used device...
    """

    available_signals = ["ecg_4000_hz", "ecg_5_min", "ecg_sample", "ecg_20_sec_10_Hz",
                         "ecg_20_sec_100_Hz", "ecg_20_sec_1000_Hz", "emg_bursts", "emg_fatigue",
                         "temp_res_8_16", "bvp_sample"]

    if signal_name in available_signals:
        out, header = load(SIGNAL_PATH + signal_name + FILE_EXTENSION, get_header=True)
    else:
        raise RuntimeError("The signal name defined as input does not correspond to any of the "
                           "signal samples contained in the package.")

    if get_header is True:
        return out, header
    else:
        return out

# 11/10/2018 16h45m :)
