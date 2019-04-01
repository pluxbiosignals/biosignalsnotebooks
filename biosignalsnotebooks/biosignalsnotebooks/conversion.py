# coding=utf-8
"""
Module responsible for the definition of functions that convert Raw units (available in the
acquisition files returned by OpenSignals) and sample units to physical units like mV, A, ºC,
s,..., accordingly to the sensor under analysis.

Available Functions
-------------------
[Public]

raw_to_phy
    Function that converts each sample value in raw units to a physical unit taking into account
    the respective transfer function for the sensor and device specified as an input.
generate_time
    Considering the acquisition sampling rate and the number of samples that compose
    the signal, this function will return a time axis in seconds.

Observations/Comments
---------------------
None

/\
"""

import numpy
from .aux_functions import _is_a_url, _generate_download_google_link
from .load import load


def raw_to_phy(sensor, device, raw_signal, resolution, option):
    """
    -----
    Brief
    -----
    Function for converting raw units to physical units.

    -----------
    Description
    -----------
    Each sensor and device has a specific transfer function that models the inputs to outputs. This transfer function
    is, thus, used in order to convert the raw units that are measured to physical units that originated the data.

    This functions makes the conversion of raw units to physical units, using the information of sensor and device.

    ----------
    Parameters
    ----------
    sensor : str
        Sensor label:
        - "ECG"
        - "EMG"
        - "TEMP"
        - "BVP"
        - "SpO2.HEAD"
        - "SpO2.FING"
        - "SpO2.ARM"

    device : str
        Plux device label:
        - "bioplux"
        - "bioplux_exp"
        - "biosignalsplux"
        - "rachimeter"
        - "channeller"
        - "swifter"
        - "ddme_openbanplux"

    raw_signal : list
        Raw signal samples.

    resolution : int
        Resolution selected during acquisition.

    option : str (optional)
        Output units (only available in certain sensors):
        - "mV"
        - "V"
        - "C" (Celsius)
        - "K" (Kelvin)
        - "Ohm"
        - "A"
        - "uA"
        (When is not applicable a warning message is raised).

    Returns
    -------
    out : list
        Signal in the new scale.
    """
    raw_signal = numpy.array(raw_signal)

    # Check if resolution has the correct data format.
    if not isinstance(resolution, int):
        raise RuntimeError("The specified resolution needs to be an integer.")

    out = None
    if sensor == "TEMP":
        vcc = 3.0
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller",
                           "swifter", "ddme_openbanplux"]
        available_dev_2 = ["bitalino", "bitalino_rev", "bitalino_riot"]
        if option == "Ohm":
            if device in available_dev_1:
                out = (1e4 * raw_signal) / (2**resolution - raw_signal)
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
        elif option == "K":
            a_0 = 1.12764514e-3
            a_1 = 2.34282709e-4
            a_2 = 8.77303013e-8
            out = 1 / (a_0 + a_1 * numpy.log(raw_to_phy(sensor, device, list(raw_signal),
                                                        resolution, option="Ohm")) + a_2 *
                       ((numpy.log(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                              option="Ohm"))) ** 3))
        elif option == "C":
            if device in available_dev_1:
                out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                             option="K")) - 273.15
            elif device in available_dev_2:
                out = ((raw_signal / (2 ** resolution)) * vcc - 0.5) * 100
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

    elif sensor == "EMG":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller",
                           "swifter", "ddme_openbanplux"]
        available_dev_2 = ["bitalino"]
        available_dev_3 = ["bitalino_rev", "bitalino_riot"]
        if option == "mV":
            vcc = 3.0
            if device in available_dev_1:
                offset = 0.5
                gain = 1
            elif device in available_dev_2:
                offset = 0.5
                gain = 1.008
            elif device in available_dev_3:
                offset = 0.5
                gain = 1.009
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
            out = (raw_signal * vcc / (2 ** resolution) - vcc * offset) / gain

        elif option == "V":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="mV")) / 1000

    elif sensor == "ECG":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller",
                           "swifter", "ddme_openbanplux"]
        available_dev_2 = ["bitalino", "bitalino_rev", "bitalino_riot"]
        if option == "mV":
            vcc = 3.0
            if device in available_dev_1:
                offset = 0.5
                gain = 1.019
            elif device in available_dev_2:
                offset = 0.5
                gain = 1.1
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
            out = (raw_signal * vcc / (2 ** resolution) - vcc * offset) / gain

        elif option == "V":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="mV")) / 1000

    elif sensor == "BVP":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller",
                           "swifter", "ddme_openbanplux"]
        if option == "uA":
            vcc = 3.0
            if device in available_dev_1:
                offset = 0
                gain = 0.190060606
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
            out = (raw_signal * vcc / (2 ** resolution) - vcc * offset) / gain

        elif option == "A":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="uA")) * 1e-6

    elif sensor in ["SpO2.ARM", "SpO2.HEAD", "SpO2.FING"]:
        available_dev_1 = ["channeller", "biosignalsplux", "swifter"]

        scale_factor = None
        if "ARM" in sensor or "FING" in sensor:
            scale_factor = 1.2
        elif "HEAD" in sensor:
            scale_factor = 0.15

        if option == "uA":
            if device in available_dev_1:
                out = scale_factor * (raw_signal / (2 ** resolution))
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")

        elif option == "A":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="uA")) * 1e-6

    elif sensor == "ACC":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller",
                           "swifter", "ddme_openbanplux"]
        if option == "g":
            if device in available_dev_1:
                Cm = 28000.0
                CM = 38000.0
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")

            out = 2.0*((2**(16.0 - resolution) * raw_signal - Cm) / (CM - Cm)) - 1.0

    else:
        raise RuntimeError("The specified sensor is not valid or for now is not available for unit "
                           "conversion.")

    return out


def generate_time(signal, sample_rate=1000):
    """
    -----
    Brief
    -----
    Function intended to generate a time axis of the input signal.

    -----------
    Description
    -----------
    The time axis generated by the acquisition process originates a set of consecutive values that represents the
    advancement of time, but does not have specific units.

    Once the acquisitions are made with specific sampling frequencies, it is possible to calculate the time instant
    of each sample by multiplying that value by the sampling frequency.

    The current function maps the values in the file produced by Opensignals to their real temporal values.

    ----------
    Parameters
    ----------
    signal : list
        List with the signal samples.

    sample_rate : int
        Sampling frequency of acquisition.

    Returns
    -------
    out : list
        Time axis with each list entry in seconds.
    """

    # Download of signal if the input is a url.
    if _is_a_url(signal):
        # Check if it is a Google Drive sharable link.
        if "drive.google" in signal:
            signal = _generate_download_google_link(signal)
        data = load(signal, remote=True)
        key_level_1 = list(data.keys())[0]
        if "00:" in key_level_1:
            mac = key_level_1
            chn = list(data[mac].keys())[0]
            signal = data[mac][chn]
        else:
            chn = key_level_1
            signal = data[chn]


    nbr_of_samples = len(signal)
    end_of_time = nbr_of_samples / sample_rate

    # ================================= Generation of the Time Axis ===============================
    time_axis = numpy.linspace(0, end_of_time, nbr_of_samples)

    return list(time_axis)

# 25/09/2018 18h58m :)
