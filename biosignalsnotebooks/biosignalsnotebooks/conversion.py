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
from .aux_functions import _is_a_url, _generate_download_google_link, _calc_time_precision, _truncate_time, \
    _truncate_value, _calc_value_precision
from .load import load
import math
from scipy.constants import g


def raw_to_phy(sensor, device, raw_signal, resolution, option, truncate=True):
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
        - "EEG"
        - "EDA"

    device : str
        PLUX device label:
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
        - "g"
        - "m/s^2"
        (When is not applicable a warning message is raised).

    truncate: boolean (optional)
        indicates whether the resulting

    Returns
    -------
    out : list
        Signal in the new scale.
    """

    raw_signal = numpy.array(raw_signal)

    # Check if resolution has the correct data format.
    if not isinstance(resolution, int) and not isinstance(resolution, numpy.int32):
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
                                                        resolution, option="Ohm", truncate=False)) + a_2 *
                       ((numpy.log(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                              option="Ohm", truncate=False))) ** 3))
        elif option == "C":
            if device in available_dev_1:
                out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                             option="K", truncate=False)) - 273.15
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
            if device in available_dev_1:
                vcc = 3.0
                offset = 0.5
                gain = 1
            elif device in available_dev_2:
                vcc = 3.3
                offset = 0.5
                gain = 1.008
            elif device in available_dev_3:
                vcc = 3.3
                offset = 0.5
                gain = 1.009
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
            out = (raw_signal * vcc / (2 ** resolution) - vcc * offset) / gain

        elif option == "V":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="mV", truncate=False)) / 1000

        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

    elif sensor == "ECG":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller",
                           "swifter", "ddme_openbanplux"]
        available_dev_2 = ["bitalino", "bitalino_rev", "bitalino_riot"]
        if option == "mV":
            if device in available_dev_1:
                vcc = 3.0
                offset = 0.5
                gain = 1.019
            elif device in available_dev_2:
                vcc = 3.3
                offset = 0.5
                gain = 1.1
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
            out = (raw_signal * vcc / (2 ** resolution) - vcc * offset) / gain

        elif option == "V":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="mV", truncate=False)) / 1000

        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

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
                                         option="uA", truncate=False)) * 1e-6

        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

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
                                         option="uA", truncate=False)) * 1e-6

        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

    elif sensor == "ACC":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller",
                           "swifter", "ddme_openbanplux"]

        available_dev_2 = ["bitalino_rev", "bitalino_riot"]
        if option == "g":
            if device in available_dev_1:
                Cm = 28000.0
                CM = 38000.0

                out = 2.0 * ((2 ** (16.0 - resolution) * raw_signal - Cm) / (CM - Cm)) - 1.0

            elif device in available_dev_2:

                # for bitalino the default calibration values are
                # for 6bit channel:
                # Cmax = 38
                # Cmin = 25
                # for 10bit channel:
                # Cmax = 608
                # Cmin = 400
                Cm = 400.0 / math.pow(2.0, 10 - resolution)
                CM = 608.0 / math.pow(2.0, 10 - resolution)

                out = 2.0 * ((raw_signal - Cm) / (CM - Cm)) - 1.0

            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
        elif option == "m/s^2":

            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,option="g", truncate=False)) * g
        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

    elif sensor == "EEG":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller", "swifter",
                           "ddme_openbanplux"]
        available_dev_2 = ["bitalino_rev", "bitalino_riot"]
        if option == "uV":
            if device in available_dev_1:
                vcc = 3.0
                offset = 0.5
                gain = 0.041990
            elif device in available_dev_2:
                vcc = 3.3
                offset = 0.5
                gain = 0.040000
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
            out = ((raw_signal * vcc / (2 ** resolution)) - vcc * offset) / gain

        elif option == "V":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="uV", truncate=False)) * 1e6

        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

    elif sensor == "EDA":
        available_dev_1 = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller", "swifter",
                           "biosignalspluxsolo"]
        available_dev_2 = ["bitalino"]
        available_dev_3 = ["bitalino_rev", "bitalino_riot"]
        if option == "uS":
            if device in available_dev_1:
                vcc = 3.0
                offset = 0
                gain = 0.12
            elif device in available_dev_2:
                # out = 1.0 / (1.0 - (raw_signal / (2 ** resolution)))

                return 1.0 / (1.0 - (raw_signal / (2 ** resolution)))  # [_truncate_value(value) for value in out]
            elif device in available_dev_3:
                vcc = 3.3
                offset = 0
                gain = 0.132
            else:
                raise RuntimeError("The output specified unit does not have a defined transfer "
                                   "function for the used device.")
            out = ((raw_signal * vcc / (2 ** resolution)) - vcc * offset) / gain

        elif option == "S":
            out = numpy.array(raw_to_phy(sensor, device, list(raw_signal), resolution,
                                         option="uS", truncate=False)) * 1e6

        else:
            raise RuntimeError("The selected output unit is invalid for the sensor under analysis.")

    else:
        raise RuntimeError("The specified sensor is not valid or for now is not available for unit "
                           "conversion.")

    # truncate the sensor data
    # i.e. truncate 1.2081179279999996 to 1.2081179279
    if truncate:

        # get the precision needed (by calculating the least significant bit / the smallest step size achievable)
        precision = _calc_value_precision(device, resolution)

        out = numpy.array([_truncate_value(value, precision) for value in out])

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

    # calculate the precision needed
    precision = _calc_time_precision(sample_rate)

    # ================================= Generation of the Time Axis ===============================
    time_axis = numpy.linspace(0, end_of_time, nbr_of_samples)

    time_axis = [_truncate_time(value, precision) for value in time_axis]

    return list(time_axis)


# 25/09/2018 18h58m :)
