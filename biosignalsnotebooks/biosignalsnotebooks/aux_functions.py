"""
Includes a set of auxiliary functions that are invoked in other biosignalsnotebooks modules.

Like the module name suggests, these functions have a supporting role and their use is not
restricted to a single module or category of biosignalsnotebooks Jupyter Notebooks.

Considering this generic nature, the great majority of the functions contained inside
"aux_functions" module are classified as private and his inclusion in the package is only intended
for the use inside biosignalsnotebooks project, though they are completely functional for other
applications.

Available Functions
-------------------
[Private]

_is_instance
    Function responsible for checking when the type of 'all' or 'any' list (input) elements is equal
    to a specific data type (input).
_butter_bandpass_filter
    Generation of a Butterworth bandpass filter and application of a signal to it.
_moving_average
    Function dedicated to the application of a moving average filter, intended to smooth the EMG
    signal.
_filter_keywords
    Function for filtering kwargs, ensuring that invalid keywords are not passed as arguments when
    certain function is called.
_inv_key
    It is invoked by _filter_keywords and used for identification when a list of keywords contain
    invalid keywords.
_calc_time_precision
    Calculates the precision needed for generating the time axis
_truncate
    truncates a number to the given decimal places


Observations/Comments
---------------------
None

/\
"""

import numpy
import scipy.signal as scisign
from inspect import signature
from warnings import warn
from scipy.interpolate import interp1d
import time as time_package
import os
from bokeh.plotting import output_file
import math


def _is_instance(type_to_check, element, condition="any", deep=False):
    """
    -----
    Brief
    -----
    Function that verifies when "all" or "any" elements of the list "element" have the type
    specified in "type_to_check" input.

    -----------
    Description
    -----------
    In some biosignalsnotebooks functions their implementation is extremely dependent on a specific
    criterion, i.e., 'all' list entries should be of a specific data type.

    In order to ensure this functionality _is_instance function was implemented.

    For example, when plotting data through 'plot' function of 'visualise' module, 'all' entries
    of time axis and data samples lists need to be 'Numeric'.
    In order to this condition be checked _is_instance should be called with the following input
    values:

    _is_instance(Number, [1, 2, 3, True, ...], 'all')

    Sometimes is also relevant to check if at least one of list entries belongs to a data type, for
    cases like this, the argument "condition" should have value equal to "any".

    --------
    Examples
    --------
    >>> _is_instance(Number, [1, 2, 3, True], 'all')
    False
    >>> _is_instance(Number, [1, 1.2, 3, 5], 'all')
    True

    ----------
    Parameters
    ----------
    type_to_check : type element
        Data type (all or any elements of 'element' list must be of the type specified in the
        current input).

    element : list
        List where condition specified in "condition" will be checked.

    condition : str
        String with values "any" or "all" verifying when "any" or "all" element entries have the
        specified type.

    deep : bool
        Flag that identifies when element is in a matrix format and each of its elements should be
        verified iteratively.

    Returns
    -------
    out : boolean
        Returns True when the "condition" is verified for the entries of "element" list.
    """

    out = None

    # Direct check of "condition" in "element".
    if deep is False:
        if condition == "any":
            out = any(isinstance(el, type_to_check) for el in element)
        elif condition == "all":
            out = all(isinstance(el, type_to_check) for el in element)

    # Since "element" is in a matrix format, then it will be necessary to check each dimension.
    else:
        for row in range(0, len(element)):
            for column in range(0, len(element[row])):
                flag = _is_instance(type_to_check, element[column][row], "all", deep=False)
                if flag is False:
                    out = flag
                else:
                    out = True
    return out


def _butter_bandpass_filter(signal, low_cutoff, high_cutoff, sample_rate, order=6):
    """
    -----
    Brief
    -----
    Function with the purpose of applying a digital bandpass filter on signal, in order to attenuate
    the signal content outside the frequency band [low_cutoff, high_cutoff].

    -----------
    Description
    -----------
    In signal processing, knowledge can be extracted from different domains, the most common is the
    time-domain, where statistical parameters are taken by analysing the acquired samples of
    a time series.

    Another common domain of signal analysis is the frequency domain, also known as
    "Fourier Domain" due to the fact that for converting data from time to frequency domain it is
    necessary to apply the Fourier Transform.

    The basic principle behind the Fourier Analysis is related with the mathematical decomposition
    of a time-series.

    As demonstrated by Joseph Fourier in his book "Théorie analytique de la chaleur":
    "some functions could be written as an infinite sum of harmonics".

    Each "harmonic" is characterized by a specific frequency, so, after decomposing a time series
    into their harmonics/elementary components, the "frequency content" of the signal is revealed.

    If the frequency content is manipulated, for example, by decreasing the weight of some
    harmonics, after the reconstruction ("sum of harmonics") then the resultant signal in time
    domain will be slightly different comparing with the original one.

    With the current function an input "signal" is applied to a butterworth bandpass filter, in
    order to decrease the weight of elementary components with frequencies smaller than "low_cutoff"
    or bigger than "high_cutoff".

    Filter order can also be specified (the bigger the order more quickly the response of the filter
    will be, near the cutoff frequencies). Higher orders could cause a less stable behavior of the
    system.

    ----------
    Parameters
    ----------
    signal : ndarray
        Array that contains the acquired samples of the signal under analysis.
    low_cutoff : int
        Low cutoff frequency of the bandpass filter.
    high_cutoff : int
        High cutoff frequency of the bandpass filter.
    sample_rate : int
        Sampling rate at which the acquisition took place.
    order : int
        Filter order.

    Returns
    -------
    out : list
        Filtered signal samples.
    """

    order = order
    nyquist_freq = 0.5 * sample_rate

    # Transfer Function.
    b_coeff, a_coeff = scisign.butter(order, [low_cutoff / nyquist_freq,
                                              high_cutoff / nyquist_freq], btype='band')[:2]

    # Application of the signal to the designed filter.
    sign = scisign.lfilter(b_coeff, a_coeff, signal)

    return sign


def _moving_average(data, wind_size=3):
    """
    -----
    Brief
    -----
    Application of a moving average filter for signal smoothing.

    -----------
    Description
    -----------
    In certain situations it will be interesting to simplify a signal, particularly in cases where
    some events with a random nature take place (the random nature of EMG activation periods is
    a good example).

    One possible simplification procedure consists in smoothing the signal in order to obtain
    only an "envelope". With this methodology the analysis is mainly centered on seeing patterns
    in data and excluding noise or rapid events [1].

    The simplification can be achieved by segmenting the time series in multiple windows and
    from each window an average value of all the samples that it contains will be determined
    (dividing the sum of all sample values by the window size).

    A quick and efficient implementation (chosen in biosignalsnotebooks package) of the moving window
    methodology is through a cumulative sum array.

    [1] https://en.wikipedia.org/wiki/Smoothing

    ---------
    Parameters
    ----------
    data : list
        List of signal samples.
    wind_size : int
        Number of samples inside the moving average window (a bigger value implies a smoother
        output signal).

    Returns
    -------
    out : numpy array
        Array that contains the samples of the smoothed signal.
    """

    wind_size = int(wind_size)
    ret = numpy.cumsum(data, dtype=float)
    ret[wind_size:] = ret[wind_size:] - ret[:-wind_size]
    return numpy.concatenate((numpy.zeros(wind_size - 1), ret[wind_size - 1:] / wind_size))


def _filter_keywords(function, kwargs_dict, is_class=False, warn_print=True):
    """
    -----
    Brief
    -----
    Function for filtering kwargs, ensuring that invalid keywords are not passed as arguments.

    -----------
    Description
    -----------
    Many Python functions included in the major packages, include in their definition some
    keyword arguments (kwargs), i.e., a dictionary having as keys non-formal parameters.

    In spite of not being formally defined, only certain keywords are accepted.

    In order to avoid that the biosignalsnotebooks user gets some errors due to an invalid keyword
    argument, when invoking functions such as 'plot' ('visualise' module), _filter_keywords receives
    the keywords entered by the user, checks if these keywords are valid and only returns a
    dictionary with the valid ones.

    ----------
    Parameters
    ----------
    function : function name
        Function where the **kwargs dictionary must be applied.

    kwargs_dict : dict
        Variable keyword arguments.

    is_class : bool
        Flag to specify if the function input is in fact a Class.

    warn_print : bool
        Flag to specify if a warning should be printed in case a key argunment is invalid.

    Returns
    -------
    kwargs_final : dict
        A filtered dictionary of valid kwargs for using in the specified function.
    """

    # %%%%%%%%%%%%%%%%%%%%%%%%%% List of keywords of our input function %%%%%%%%%%%%%%%%%%%%%%%%%%%
    if is_class is False:
        list_of_keywords = list(signature(function).parameters.keys())
    else:
        list_of_keywords = list(function.__dict__.keys())

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # %% List of keywords passed in **kwargs that match the valid keywords of the input function %%
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    available_keywords = set(kwargs_dict.keys())
    valid_keywords = list(available_keywords.intersection(list_of_keywords))

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Final kwargs %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    bool_val, inv_keys = _inv_key(list(available_keywords), list_of_keywords)
    if not bool_val:
        str_inval_keys = ""
        for inval_key in inv_keys:
            str_inval_keys += " " + str(inval_key) + ";"
            if warn_print is True:
                warn(RuntimeWarning("At least one of the specified kwargs is not applied "
                                    "in numpy.loadtxt function" + str_inval_keys),
                     stacklevel=2)
                break

    kwargs_final = dict((your_key, kwargs_dict[your_key]) for your_key in valid_keywords)

    return kwargs_final


def _inv_key(list_keys, valid_keys):
    """
    -----
    Brief
    -----
    A sub-function of _filter_keywords function.

    -----------
    Description
    -----------
    Function used for identification when a list of keywords contains invalid keywords not present
    in the valid list.

    ----------
    Parameters
    ----------
    list_keys : list
        List of keywords that must be verified, i.e., all the inputs needs to be inside valid_keys
        in order to a True boolean be returned.

    valid_keys : list
        List of valid keywords.

    Returns
    -------
    out : boolean, list
        Boolean indicating if all the inserted keywords are valid. If true a list with invalid
        keywords will be returned.
    """

    inv_keys = []
    bool_out = True
    for i in list_keys:
        if i not in valid_keys:
            bool_out = False
            inv_keys.append(i)

    return bool_out, inv_keys


def _generate_bokeh_file(file_name):
    """
    -----
    Brief
    -----
    Auxiliary function responsible for the creation of a directory where Bokeh figures will be
    stored.
    The "active" output file for Bokeh will also be updated for the new one.

    -----------
    Description
    -----------
    To ensure that Bokeh plots are correctly observed in the HTML version of the Notebooks, it is
    necessary to embed the plots inside Iframes.

    Taking this into consideration, the source file of the plot is mandatory to use an Iframe, and
    this function ensures the generation of a Bokeh file for each plot, storing it in an adequate
    place.

    ----------
    Parameters
    ----------
    file_name : str
        Name given to the file.

    Returns
    -------
    out : str
        String containing the file name.
    """
    # Creation of our output file instance.
    if file_name is None:
        file_name = "plot_" + time_package.strftime("%Y_%m_%d_%H_%M_%S.html")
    else:
        file_name += ".html"

    if not os.path.exists("generated_plots"):
        os.makedirs("generated_plots")

    output_file(os.getcwd().replace("\\", "/") + "/generated_plots/" + file_name)

    return file_name


def _is_a_url(input_element):
    """
    -----
    Brief
    -----
    Auxiliary function responsible for checking if the input is a string that contains an url.

    -----------
    Description
    -----------
    Some biosignalsnotebooks functions support a remote access to files. In this situation it is
    important to understand if the input is an url, which can be easily achieved by checking if some
    key-markers are present.

    The key-markers that will be searched are "http://", "https://", "www.", ".pt", ".com", ".org",
    ".net".

    ----------
    Parameters
    ----------
    input_element : unknown
        The data structure that will be checked.

    Returns
    -------
    out : bool
        If the input_element is a string and if it contains any key-marker, then True flag will be returned.
    """
    if type(input_element) is str:
        # Check if signal_handler is a url.
        # [Statements to be executed if signal_handler is a url]
        if any(mark in input_element for mark in ["http://", "https://", "www.", ".pt", ".com",
                                                  ".org", ".net"]):
            return True
        else:
            return False
    else:
        return False


def _generate_download_google_link(link):
    """
    -----
    Brief
    -----
    Function that returns a direct download link of a file stored inside a Google Drive
    Repository.

    -----------
    Description
    -----------
    Generally a link from a Google Drive file is only for viewing purposes.

    If the user wants to download the file it can be done with Google Drive graphical user
    interface.

    However if we try to programmatically download the file it cannot be done with the normal url.

    So, the current function converts the "read-only" link to a downloadable format.

    ----------
    Parameters
    ----------
    link : str
        Sharable Google Drive link.

    Returns
    -------
    out : str
        Manipulated link, that ensures a direct download with wget function.
    """

    # Get file id.
    if "id=" not in link:
        # Split link into segments (split character --> /)
        split_link = link.split("/")

        file_id = split_link[-2]
    else:
        # Split link into segments (split string --> "id=")
        split_link = link.split("id=")
        file_id = split_link[-1]

    return "https://drive.google.com/uc?export=download&id=" + file_id


def _interpolate(segment, segment1, kind='linear'):
    """
    -----
    Brief
    -----
    Given two input signals, interpolates the shortest to the length of the longest.

    -----------
    Description
    -----------
    Interpolation is a technique that allows to fill in missing values of a signal in order to extend it. In this case,
    interpolation is intended to equalize the length of the input signals/segments to the length of the longest one.
    The method of interpolation may be of any kind accepted by scipy.interpolate.interp1d.

    This function allows to interpolate the input segments to the length of the longest one.

    ----------
    Parameters
    ----------
    segment: array-like
        first segment
    segment1: array-like
        second segment
    kind: string
        kind of interpolation to be applied to the set of segments. Default: 'linear'.

    Returns
    -------
    new_array, original_array: array-like
        interpolated segments/signals
    """

    if len(segment) > len(segment1):
        new_array = segment1
        original_array = segment
    elif len(segment) < len(segment1):
        new_array = segment
        original_array = segment1
    else:
        return segment, segment1

    x = range(len(new_array))
    y = new_array
    xnew = numpy.linspace(0, x[-1], num=len(original_array), endpoint=True)
    new_array = interp1d(x, y, kind=kind)(xnew)

    return new_array, original_array


def _interpolated_segments(segments, kind='linear'):
    """
    -----
    Brief
    -----
    Given a set of segments, interpolates all to the length of the longest segment.

    -----------
    Description
    -----------
    Interpolation is a technique that allows to fill in missing values of a signal in order to extend its length. In
    this case, interpolation is intended to equalize the length of the input signals/segments to the length of the
    longest one. The method of interpolation may be of any kind accepted by scipy.interpolate.interp1d.

    This function allows to interpolate the input segments to the length of the longest one.

    ----------
    Parameters
    ----------
    segments: array-like
        set of segments
    kind: string
        kind of interpolation to be applied to the set of segments. Default: 'linear'.

    Returns
    -------
    interpolated_segments: array-like
        interpolated segments/signals
    """
    
    index = numpy.array([len(i) for i in segments]).argmax()
    interpolated_segments = segments.copy()
    for i, seg in enumerate(segments):
        interpolated_segments[i] = _interpolate(seg, segments[index].copy(), kind)[0]

    interpolated_segments = numpy.vstack(interpolated_segments)

    return interpolated_segments


def _calc_time_precision(sampling_rate):
    """
    Calculates the number of needed digits after the decimal point based on the given sampling rate.
    This is done by finding the periodicity within the fraction. The precision is the number of digits of a non-repeated
    sequence AFTER the decimal point + 1.
    Parameters
    ----------
    sampling_rate: integer
        Sampling frequency of acquisition.

    Returns
    -------
    the precision needed for the given sqmpling rate

    """

    # convert sampling rate to int
    sampling_rate = int(sampling_rate)

    # calculate the first remainder
    remainder = 1 % sampling_rate

    # list for holding all remainders that have been calculated
    seen_remainders = []

    # calculate all other remainders until the modulo operation yields either zero or the remainder has already appeared
    # before (this is when the periodicity starts)
    while (remainder != 0) and (remainder not in seen_remainders):

        # append the current remainder to the seen remainder list
        seen_remainders.append(remainder)

        # multiply the remainder by ten (this is basically the process of converting a fraction to a decimal number
        # using long division
        remainder = remainder * 10

        # calculate the next remainder
        remainder = remainder % sampling_rate

    return len(seen_remainders) + 1


def _truncate_time(number, decimals=0):
    """
    Truncates a time to the specified decimal places. This function is needed when a time axis is generated for PLUX
    devices, because otherwise there will be approximation "errors" that come from the binary internal representation
    of fractions with floats. See: https://docs.python.org/3/tutorial/floatingpoint.html
    Parameters
    ----------
    number: float
            The float number that is supposed to be truncated
    decimals: int
            The number of decimal places that are supposed to stay preserved after the truncation

    Returns
    -------
    A truncated float number

    """

    # check for validity of inputs
    if not isinstance(decimals, int):
        raise TypeError("The parameter \'decimal\' must be an integer value.")
    elif decimals < 0:
        raise ValueError("The parameter \'decimal\' has to be >= 0.")
    elif decimals == 0:
        return math.trunc(number)

    # calculate the shift factor for truncation
    shift_factor = 10 ** decimals

    # calculate the truncated number (shift --> truncate --> shift back)
    return math.trunc(number * shift_factor) / shift_factor


def _calc_value_precision(device, resolution):
    """
    Function to calculate the precision needed for a PLUX device based on the resolution of the device.
    This function calculates the least significant bit / the smallest step size achievable, finds the first non-zero
    digit after the decimal point and returns the position of that digit as the precision needed
    Parameters
    ----------
    device: String
        The name of the deivce as string
    resolution:
        The resolution of the device

    Returns
    -------
    The precision needed for the device as integer

    """

    # lists for checking device type
    biosignalsplux_devices = ["bioplux", "bioplux_exp", "biosignalsplux", "rachimeter", "channeller", "swifter",
                              "biosignalspluxsolo"]

    bitalino_devices = ["bitalino_rev", "bitalino_riot", "bitalino"]

    # check for the device
    if device not in biosignalsplux_devices or device not in bitalino_devices:

        # set standard precision of 5 digits
        precision = 4

        return precision

    # get the full-scale volatge
    vcc = 3.0 if device in biosignalsplux_devices else 3.3  # assuming all other devices are bitalino devices

    # calculate the least significant bit /  the smallest step size achievable
    lsb = vcc / (2 ** resolution)

    # convert lsb to string and make sure that the number is not in scientifc exponential notation
    # using 10 digits after the decimal point
    lsb = '{:.10f}'.format(lsb)

    # get the position of the first non-zero value on the fractional part (the part after the decimal point)
    precision = _get_pos_first_nonzero_at_start(lsb.split('.')[1])

    return precision - 1


def _get_pos_first_nonzero_at_start(fractional):
    """
    function that returns all zeros at the beginning of the fractional part (the part that comes after the decimal point)
    of a number and returns the position of the first non-zero number.

    example: 00000056789999 the first 6 zeroes are ignored and the function returns 6
             (the position of the 5 in that sequence)

    Parameters
    ----------
    fractional: String
            The fractional part of a float number converted to a string

    Returns
    -------
    The position of the first non-zero number in the input string

    """

    # bolean for checking if a digit of the fractional part is zero
    is_zero = True

    # start from postion 1 in the array
    pos = 0

    # ignore all zeros at the beginning
    while is_zero:

        # check if the digit is not zero
        if fractional[pos] != '0':

            # set isZero to false
            is_zero = False

        else:  # current digit is zero

            # update position
            pos += 1

    return pos


def _truncate_value(value, repeat=4):
    """
    Truncates a the fractional part of a number (part after the decimal point) based on the number of repeats given
    (i.e. 8.284657919999999 is truncated to 8.284657919 if repeats = 3).
    This function is needed when PLUX RAW sensor values are converted to their physical values. Otherwise there will be
    approximation "errors" that come from the binary internal representation of fractions with floats.
    See: https://docs.python.org/3/tutorial/floatingpoint.html

    Parameters
    ----------
    value: float
        The converted sensor value.
    repeat: int, optional
        The

    Returns
    -------
    A truncated float

    """
    # check for validity of inputs
    if not isinstance(repeat, int):
        raise TypeError("The parameter \'repeat\' places must be an integer value.")
    elif repeat <= 0:
        raise ValueError("The parameter \'repeat\' has to be > 0")

    # check if sensor value is 0.0
    if str(value) == '0.0':
        return value

    # make sure that the string is not in scientific exponential notation
    # 25 decimal places after the decimal point should be more than enough...
    value = '{:.25f}'.format(value)

    # split the string at the decimal point
    split = value.split('.')

    # get the fractional part
    frac = split[1]

    # check if the integer part (part before the decimal point) is zero
    if split[0] == '0' or split[0] =='-0':
        # ignore zeroes at the beginning of the fractional part
        start_pos = _get_pos_first_nonzero_at_start(frac)

    else:
        # set start position to 1 (second digit after the decimal point)
        start_pos = 1

    # get the digit before the start position
    check_digit = frac[start_pos - 1]

    # counter for counting the occurence of the digit
    counter = 0
    precision = 0

    for pos in range(start_pos, len(frac)):

        # get the next digit
        digit = frac[pos]

        # check if digit is equal to the last seen digit
        if digit == check_digit:

            # update the counter
            counter += 1
        else:

            # update the current digit
            check_digit = digit

            # reset the counter
            counter = 0

        if counter == repeat:
            precision = pos - (repeat - 1)
            break

    # check if there is a repeating sequence of min length 'repeat' in the fractional part
    if precision != 0:
        # truncate the fractional part
        split[1] = frac[:precision]

    # join both the the number again
    return float('.'.join(split))

# 01/10/2018 19h19m :)
