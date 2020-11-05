# coding=utf-8
"""
Functions intended to synchronise two signals and generate a new file containing the new synchronised signals.

Available Functions
-------------------
[Public]

synchronise_signals
    This function synchronises the input signals using the full cross correlation function between the signals.

generate_sync_txt_file
    This function allows to generate a text file with synchronised signals from the input file(s).

generate_sync_h5_file
    This function allows to generate a h5 file with synchronised signals from the input file(s).

create_synchronised_files
    This function creates .txt and .h5 files with synchronised signals.

create_android_sync_header
    function in order to creating a new header for a synchronised android sensor file

pad_android_data
    function in order to pad multiple android signals to the correct same start and end values

save_synchronised_android_data
    Function used for saving synchronised android data into a single file

sync_android_files
    Function to synchronise multiple android files into one. The function has two modes.

Available Functions
-------------------
[Private]

_shape_array
    Function that equalises the input arrays by zero-padding the shortest one.

_create_h5_file_old
    Function to create a new .h5 file that contains the copy of the contents of the input file(s).

_create_h5_file
    Function to create a new .h5 file that contains the copy of the contents of the input file(s).

_create_txt_from_str
    This function allows to generate a text file with synchronised signals from the input file.

_create_txt_from_list
    This function allows to generate a text file with synchronised signals from the input files.

_pad_data:
    Function to pad data with either padding type 'same' or 'zero'

Observations/Comments
---------------------
None

/\
"""
import json
import biosignalsnotebooks as bsnb
import numpy as np
from h5py import File
import os
from .android import re_sample_data, _round_sampling_rate
from .load import load_android_data


def synchronise_signals(in_signal_1, in_signal_2):
    """
    -----
    Brief
    -----
    This function synchronises the input signals using the full cross correlation function between the signals.

    -----------
    Description
    -----------
    Signals acquired with two devices may be dephased. It is possible to synchronise the two signals by multiple
    methods. Here, it is implemented a method that uses the calculus of the cross-correlation between those signals and
    identifies the correct instant of synchrony.

    This function synchronises the two input signals and returns the dephasing between them, and the resulting
    synchronised signals.

    ----------
    Parameters
    ----------
    in_signal_1 : list or numpy.array
        One of the input signals.
    in_signal_2 : list or numpy.array
        The other input signal.

    Returns
    -------
    phase : int
        The dephasing between signals in data points.
    result_signal_1: list or numpy.array
        The first signal synchronised.
    result_signal_2: list or numpy.array
        The second signal synchronised.
    """

    # signal normalisation
    mean_1, std_1, mean_2, std_2 = [np.mean(in_signal_1), np.std(in_signal_1), np.mean(in_signal_2),
                                    np.std(in_signal_2)]
    signal_1 = in_signal_1 - mean_1
    signal_1 /= std_1
    signal_2 = in_signal_2 - mean_2
    signal_2 /= std_2

    # zero padding signals so that they are of same length, this facilitates the calculation because
    # then the delay between both signals can be directly calculated
    # zero padding only if needed
    if (len(signal_1) != len(signal_2)):

        # check which signal has to be zero padded
        if (len(signal_1) < len(signal_2)):

            # pad first signal
            signal_1 = np.append(signal_1, np.zeros(len(signal_2) - len(signal_1)))

        else:

            # pad second signal
            signal_2 = np.append(signal_2, np.zeros(len(signal_1) - len(signal_2)))

    # Calculate the full cross-correlation between the two signals.
    correlation = np.correlate(signal_1, signal_2, 'full')

    # crop signals to original length (removing zero padding)
    signal_1 = signal_1[:len(in_signal_1)]
    signal_2 = signal_2[:len(in_signal_2)]

    # calculate tau / shift between both signals
    tau = int(np.argmax(correlation) - (len(correlation)) / 2)

    # check which signal has to be sliced
    if (tau < 0):
        # tau negative --> second signal lags
        signal_2 = signal_2[np.abs(tau):]

    elif (tau > 0):
        # tau positive ---> firs signal lags
        signal_1 = signal_1[np.abs(tau):]

    # revert signals to orignal scale
    result_signal_1 = signal_1 * std_1 + mean_1
    result_signal_2 = signal_2 * std_2 + mean_2

    return tau, result_signal_1, result_signal_2


def generate_sync_txt_file(in_path, channels=("CH1", "CH1"), new_path='sync_file.txt'):
    """
    -----
    Brief
    -----
    This function allows to generate a text file with synchronised signals from the input file(s).

    -----------
    Description
    -----------
    OpenSignals files follow a specific structure that allows to analyse all files in the same way. Furthermore, it
    allows those files to be opened and analysed in the OpenSignals software without the need of programming.

    This functions takes one or two files, synchronises the signals in channels and generates a new file in the new
    path.

    ----------
    Parameters
    ----------
    in_path : str or list
        If the input is a string, it is assumed that the two signals are in the same file, else, if the input is a list,
        it is assumed that the two signals are in different file (the list should contain the paths to the two files).
    channels : list
        List with the strings identifying the channels of each signal. (default: ("CH1", "CH1"))
    new_path : str
        The path to create the new file. (default: 'sync_file.txt')
    """
    if type(in_path) is str:
        _create_txt_from_str(in_path, channels, new_path)
    elif type(in_path) is list:
        _create_txt_from_list(in_path, channels, new_path)
    else:
        raise TypeError('The path should be a list of str or a str.')


def generate_sync_h5_file(in_paths, channels=('channel_1', 'channel_1'), new_path='sync_file.h5'):
    """
    -----
    Brief
    -----
    This function allows to generate a h5 file with synchronised signals from the input file(s).

    -----------
    Description
    -----------
    OpenSignals files follow a specific structure that allows to analyse all files in the same way. Furthermore, it
    allows those files to be opened and analysed in the OpenSignals software without the need of programming.

    This functions takes one or two files, synchronises the signals in channels and generates a new file in the new
    path.

    ----------
    Parameters
    ----------
    in_paths : str or list
        If the input is a string, it is assumed that the two signals are in the same file, else, if the input is a list,
        it is assumed that the two signals are in different file (the list should contain the paths to the two files).
    channels : list
        List with the strings identifying the channels of each signal. (default: ("channel_1", "channel_1"))
    new_path : str
        The path to create the new file. (default: 'sync_file.h5')
    """

    if type(in_paths) == list or type(in_paths) == str:
        new_file = _create_h5_file(in_paths, new_path)
    else:
        raise TypeError('The path should be a list of str or a str.')

    data, devices = [[], []]
    for j, i in enumerate(list(new_file.keys())):
        devices.append(i)
        data.append(np.concatenate(new_file[i].get('raw').get(channels[j]))[:])
    phase, s1, s2 = synchronise_signals(data[0], data[1])

    if np.array_equal(s1, data[0]):
        # Change the second device
        new_device = new_file[devices[1]]
    elif np.array_equal(s2, data[1]):
        # Change the first device
        new_device = new_file[devices[0]]
    raw_digital = ['raw', 'digital', 'support']
    for r_d in raw_digital:
        raw_di = new_device[r_d]
        for key in list(raw_di.keys()):
            if r_d != 'support':
                signal = list(raw_di[key])[phase:]
                attribute = list(raw_di[key].attrs.items())
                del raw_di[key]
                raw_di.create_dataset(name=key, data=np.array(signal, dtype=np.int32))
                for a in attribute:
                    raw_di[key].attrs.__setitem__(name=a[0], value=a[1])
            else:
                for other_key in list(raw_di[key].keys()):
                    channel = raw_di[key][other_key]
                    level = int(key.split('_')[-1])
                    for yak in list(channel.keys()):
                        if yak is not 't':
                            data_aux = list(channel[yak])[int(np.ceil(phase/level)):]
                        else:
                            data_aux = list(channel[yak])[:len(channel[yak][:])-int(np.ceil(phase / level))]
                        del channel[yak]
                        channel.create_dataset(name=yak, data=np.array(data_aux))

    length = abs(len(new_file[devices[0]]['raw']['channel_1']) - len(new_file[devices[1]]['raw']['channel_1']))

    if len(new_file[devices[0]]['raw']['channel_1']) > len(new_file[devices[1]]['raw']['channel_1']):
        index = 1
    else:
        index = 0

    for r_d in raw_digital:
        raw_di = new_file[devices[index]][r_d]
        for key in list(raw_di.keys()):
            if r_d != 'support':
                if 'channel' in key or 'digital' in key:
                    signal = np.concatenate([list(raw_di[key]), np.zeros([length, 1])])
                elif 'nSeq' in key:
                    signal = np.arange(len(raw_di[key]) + length)
                attribute = list(raw_di[key].attrs.items())
                del raw_di[key]
                raw_di.create_dataset(name=key, data=np.array(signal, dtype=np.int32))
                for a in attribute:
                    raw_di[key].attrs.__setitem__(name=a[0], value=a[1])
            else:
                for other_key in list(raw_di[key].keys()):
                    channel = raw_di[key][other_key]
                    level = int(key.split('_')[-1])
                    for yak in list(channel.keys()):
                        if yak is not 't':
                            data_aux = np.vstack([list(channel[yak]),
                                                  np.zeros(int(length / level)).reshape(-1, 1)])
                        else:
                            data_aux = np.arange(0, len(channel[yak][:])+length//level).reshape(-1, 1)*level

                        del channel[yak]
                        channel.create_dataset(name=yak, data=np.array(data_aux, dtype=int))

    final_length = len(np.ravel(signal))
    for i in list(new_file.keys()):
        new_file[i].attrs['duration'] = str(int(final_length // new_file[i].attrs['sampling rate'])) + ' s'
        new_file[i].attrs.modify(name='nsamples', value=int(final_length))
    new_file.close()


def create_synchronised_files(in_path=(('file1.txt', 'file2.txt'), ('file1.h5', 'file2.h5')), channels=(1, 1),
                      file_name='sync_file'):
    """
    -----
    Brief
    -----
    This function creates .txt and .h5 files with synchronised signals.

    -----------
    Description
    -----------
    OpenSignals software generates 3 types of files structured in specific ways. The formats are .txt, .h5 and .edf.
    Those files follow specific structures in order to normalise their analysis and to be able to be opened by the
    OpenSignals software.

    This functions allows to generate .txt and .h5 files with synchronised signals structured the same way as the files
    generated by OpenSignals software.

    ----------
    Parameters
    ----------
    in_path : list
        List containing the paths to the two file formats. If the signals are in separate files, each entry should be a
        list of strings, else, the list should contain two strings.
        (default: (('file1.txt', 'file2.txt'), ('file1.h5', 'file2.h5') - case in which the two signals are in separate
        files)
        (example in which the signals are in the same file: ('file.txt', 'file.h5')
    channels : list
        List with the ints identifying the channels of each signal. (default: (1, 1))
    file_name : str
        The name of the new files without the extension. (default: 'sync_file')
    """
    h5_channels = ['channel_'+str(i) for i in channels]
    txt_channels = ['CH' + str(i) for i in channels]
    generate_sync_h5_file(in_path[1], channels=h5_channels, new_path=file_name+'.h5')
    generate_sync_txt_file(in_path[0], channels=txt_channels, new_path=file_name + '.txt')


def create_android_sync_header(in_path, sampling_rate):

    '''
    function in order to creating a new header for a synchronised android sensor file
    (i.e. multiple android sensor files into one single file)
    Parameters
    ----------
    in_path (list of strings): list containing the paths to the files that are supposed to be synchronised
    sampling_rate(int): The sampling rate to which the signals are going to be synchronised

    Returns
    -------
    header (string): the new header as a string
    '''

    # variable for the header
    header = None

    # cycle through the file list
    for i, file in enumerate(in_path):

        # check if it is the first file entry
        if (i == 0):

            # open the file
            with open(file, encoding='latin-1') as opened_file:
                # read the information from the header lines (omitting the begin and end tags of the header)
                header_string = opened_file.readlines()[1][2:]  # omit "# " at the beginning of the sensor infromation

                # convert the header into a dict
                header = json.loads(header_string)

        else:

            # open the file
            with open(file, encoding='latin-1') as opened_file:
                header_string = opened_file.readlines()[1][2:]

                # convert header into a dict
                curr_header = json.loads(header_string)

                # get the key 'internal sensor' or 'sensores internos'
                dict_key = list(header.keys())[0]

                # add the fields from the header of the current file
                header[dict_key]['sensor'].extend(curr_header[dict_key]['sensor'])  # sensor field
                header[dict_key]['column'].extend(
                    curr_header[dict_key]['column'][1:])  # column field

                # get the last channel from the channel field
                num_channels = header[dict_key]['channels'][-1]

                # get the channels from the current sensor
                new_channels = curr_header[dict_key]['channels']

                # adjust the channel number
                new_channels = [ch + (num_channels + 1) for ch in new_channels]

                header[dict_key]['channels'].extend(new_channels)  # channels field
                header[dict_key]['label'].extend(
                    curr_header[dict_key]['label'])  # label field
                header[dict_key]['resolution'].extend(
                    curr_header[dict_key]['resolution'])  # resolution field
                header[dict_key]['special'].extend(
                    curr_header[dict_key]['special'])  # special field
                header[dict_key]['sleeve color'].extend(
                    curr_header[dict_key]['sleeve color'])  # sleeve color field
                header[dict_key]['sampling rate'] = sampling_rate # changing sampling rate to the one specified by the
                                                                  # user

    # create new header string
    header_string = "# OpenSignals Text File Format\n# " + json.dumps(header) + '\n# EndOfHeader\n'

    return header_string


def pad_android_data(sensor_data, report, start_with=None, end_with=None, padding_type='same'):

    """
    function in order to pad multiple android signals to the correct same start and end values. This function is
    needed in order to perform a synchronization of android sensors.
    Instead of passing a sample number or a time to indicate where to start or end the synchronization the user passes
    the sensor name instead.

    example:
    let's assume an acquisition was made with the following sensors Acc, GPS, Light, and Proximity.
    The sensors start acquiring data in the following order: ['Proximity', 'Light', 'Acc', 'GPS']
    The sensor stop acquiring data in the following order: ['Proximity', 'Light', 'GPS', 'Acc']

    Then the user can specify where to start and end the synchronization by for example setting:
    start_with='Proximity', and
    stop_with='GPS'
    In this case the signals are synchronised when the Proximity sensor starts recording until the GPS sensor stops
    recording data. The other sensors are padded / cropped to the corresponding starting / stopping points.
    At the beginning:The 'Light', 'Acc', and 'GPS' sensors are padded to the staring point of the Proximity sensor
    At the end: The 'Proximity' and 'Light' sensors are padded until the stopping point of the 'GPS' sensor and the
                'Acc' sensor is cropped to the stopping point of the GPS sensor.

    Parameters
    ----------
    sensor_data (list): A list containing the data of the sensors to be synchronised.

    report (dict): The report returned by the 'load_android_data' function.

    start_with (string, optional): The sensor that indicates when the synchronization should be started.
                              If not specified the sensor that started latest is chosen.

    end_with (string, optional): The sensor that indicates when the synchronizing should be stopped.
                            If not specified the sensor that stopped earliest is chosen

    padding_type (string, optional): The padding type used for padding the signal. Options are either 'same' or 'zero'.
                                     If not specified, 'same' is used.

    Returns
    -------

    padded_sensor_data: the padded sensor data for each sensor in the sensor_data list
    """

    # list for holding the padded data
    padded_sensor_data = []

    # get the index of the sensor used for padding in the start (ssi = start sensor index)
    # if none is provided (start == None) then the latest starting sensor is used
    if (start_with == None):
        ssi = report['starting times'].index(max(report['starting times']))

    else:
        ssi = report['names'].index(start_with)

    # get the index of the sensor used for padding in the end (esi = end sensor index)
    # if none is provided (end == None) then the sensor that stopped earliest is used
    if (end_with == None):
        esi = report['stopping times'].index(min(report['stopping times']))

    else:
        esi = report['names'].index(end_with)

    # check if the starting and stopping times are equal (this can be the case when a significant motion sensor is used
    # and only one significant motion was detected by the sensor)
    # in that case we use the next sensor that stopped recording the earliest
    if (report['starting times'][esi] == report['stopping times'][ssi]):
        print('Warning: Start and end at same time...using next sensor that stopped earliest instead')
        esi = report['stopping times'].index(np.sort(report['stopping times'])[1])

    # get the starting value
    start_time = report['starting times'][ssi]

    # get the stopping value
    end_time = report['stopping times'][esi]

    # get time axis of the starting sensor and check for dimensionality of the data
    time_axis_start = sensor_data[ssi][:1] if (sensor_data[ssi].ndim == 1) else sensor_data[ssi][:, 0]

    # get the time axis of th ending sensor and check for dimensionality of the data
    time_axis_end = sensor_data[esi][:1] if (sensor_data[esi].ndim == 1) else sensor_data[esi][:, 0]

    # start padding: for loop over names (enumerated)
    for i, name in enumerate(report['names']):

        # get the data of the current signal
        data = sensor_data[i]

        # check for the dimensionality of the signal data (handling for significant motion sensor)
        if (data.ndim == 1):  # 1D array

            # get the time axis
            time_axis = data[:1]

            # get the signal data
            signals = data[1:]

            # expand the dimensionality of the data (in order to have the same dimensionality as all other data)
            signals = np.expand_dims(signals, axis=1)

        else:  # mutlidimensional array

            # get the time_axis
            time_axis = data[:, 0]

            # get the signal data
            signals = data[:, 1:]

        # --- 1.) padding at the beginnging ---
        if (start_time > time_axis[0]):  # start_time after current signal start (cropping of the signal needed)

            # get the time_axis size before cropping
            orig_size = time_axis.size

            # crop the time axis
            time_axis = time_axis[time_axis >= start_time]

            # crop the signal data
            signals = signals[(orig_size - time_axis.size):, :]

        # get the values that need to be padded to the current time axis
        start_pad = time_axis_start[time_axis_start < time_axis[0]]

        # --- 2.) padding at the end ---
        if (end_time < time_axis[-1]):  # end_time before current signal end (cropping of the signal needed

            # crop the time axis
            time_axis = time_axis[time_axis <= end_time]

            # check if cropping leads to elimination of signal
            if (time_axis.size == 0):
                raise IOError(
                    'The configuration you chose led to elimination of the {} sensor. Please choose another sensor for paremeter \'end_with\'.'.format(
                        name))

            # crop the signal data
            signals = signals[:time_axis.size, :]

        # get the values that need to be padded to the current time axis
        end_pad = time_axis_end[time_axis_end > time_axis[-1]]

        # pad the time axis
        time_axis = np.concatenate((start_pad, time_axis, end_pad))

        # for holing the new padded data
        padded_data = time_axis

        # cycle over the signal channels
        for channel in np.arange(signals.shape[1]):

            # get the signal channel
            sig_channel = signals[:, channel]

            # check for the sensor
            if (name == 'GPS'):  # gps sensor (always use padding type 'same' to indicate that the phone has not moved)

                # pad the channel
                sig_channel = np.pad(sig_channel, (start_pad.size, end_pad.size), 'edge')

            elif (name == 'SigMotion'):  # significant motion sensor (always pad zeros)

                # pad the channel
                sig_channel = np.pad(sig_channel, (start_pad.size, end_pad.size), 'constant', constant_values=(0, 0))

            else:  # all other sensors

                # check for setting of the user
                if (padding_type == 'same'):

                    # pad the channel
                    sig_channel = np.pad(sig_channel, (start_pad.size, end_pad.size), 'edge')

                elif (padding_type == 'zeros'):

                    # pad the channel
                    sig_channel = np.pad(sig_channel, (start_pad.size, end_pad.size), 'constant',
                                         constant_values=(0, 0))

                else:  # undefined input

                    raise IOError('Invalid padding type. Please choose between padding types \'same\' or \'zero\'.')

            # concatenate the channel to the padded data
            padded_data = np.vstack((padded_data, sig_channel))

        # append the data to the padded_sensor_data list
        # the data is transposed in order to have the correct shape (samples x number of channels)
        padded_sensor_data.append(padded_data.T)

    return padded_sensor_data


def save_synchronised_android_data(time_axis, data, header, path, file_name='android_synchronised'):
    """
    Function used for saving synchronised android data into a single file

    Parameters
    ----------
    time_axis (N,  array_like): The time axis after the padding and re-sampling the sensor data.

    data (list): List containing the padded and re-sampled sensor signals. The length of data along the 0-axis has to be
                 the same size as time_axis

   header (string): A string containing the header that is supposed to be added to the file.

    path (string): A string with the location where the file should be saved.

    file_name (string, optional): The name of the file. If not specified, the file is named
                             'android_synchronised.txt'.

    """
    # add .txt suffix to the file name
    file_name = file_name + '.txt'
    # create final save path
    save_path = os.path.join(path, file_name)

    # add the time axis for the final data array
    # make the time axis a column vector
    final_data_array = np.expand_dims(time_axis, 1)

    # write all the data into a single array
    for signals in data:
        final_data_array = np.append(final_data_array, signals, axis=1)

    # open a new file at the path location
    sync_file = open(save_path, 'w')

    # write the header to the file
    sync_file.write(header)

    # write the data to the file
    for row in final_data_array:
        sync_file.write('\t'.join(str(value) for value in row) + '\t\n')

    # close the file
    sync_file.close()

    return save_path


def sync_android_files(in_path, out_path, sync_file_name='android_synchroinzed', automatic_sync=True):
    """
    Function to synchronise multiple android files into one. The function has two modes.

    1.) automatic_sync = True:
        In this mode, the function will do a full automatic syncrhonization of the files. The synchronization will only
        take place in the time window in which all sensors are runinng simultaneously. The rest of the data will be cut.
        Furthermore, the sampling rate for re-sampling the signals will be set to the highest sampling rate present.
        This sampling rate is rounded to the next tens digit (i.e 43 Hz -> 40 Hz | 98 Hz -> 100 Hz). Sampling rates below
        5 Hz are set to 1 Hz.
        In this mode, the function will give feedback on what it is doing and how it is setting the values.

    2.) automatic_sync = False
        In this mode, the function will prompt the user for specific inputs that are needed to set certain parameters.
        The function will prompt the user with appropriate prompts and also handles when the user inputs something invalid.

    Parameters
    ----------
    in_path (list): list of paths that point to the files that are supposed to be synchronised
    out_path (string): The path where the synchronised file is supposed to be saved
    sync_file_name (String, optional): The name of the new file. If not provided then the name will be set to
                                       'android_synchronised.txt'
    automatic_sync (boolean, optional): boolean for setting the mode of the function.
                                        If not provided it will be set to True

    Returns
    -------

    """

    # load the data
    sensor_data, report = load_android_data(in_path, print_report=True)

    # ---- data padding ---- #
    print('\n---- DATA PADDING ----\n')
    # check for synchroization option
    if (not automatic_sync):

        # flags for checking user input
        check_input1 = False  # for start_with and end_with
        check_input2 = False  # for padding_type

        # prompt user for start_with and end_with
        while (not check_input1):

            # get the input from the user
            start_with = input('Type in the sensor for specifying where to START the synchronization:')
            end_with = input('Type in the sensor name for specifiying where to END the synchronization:')

            # check the input for validity
            if (start_with not in report['names'] or end_with not in report['names']):

                # wrong input: prompt user again
                print(
                    '\nOne of the sensors you chose is not listed in the report. \nPlease choose from the following sensors {}.\n'.format(
                        report['names']))

            else:  # input correct

                check_input1 = True

        # prompt user for padding_type
        while (not check_input2):

            # get input from the user
            padding_type = input('Choose a PADDING TYPE (same or zeros):')

            # check for validity
            if (padding_type not in ['same', 'zeros']):

                # wrong input: prompt user again
                print('\nThe padding type you chose does not exist. \nPlease input either same or zeros.\n')

            else:  # input correct

                check_input2 = True

        # pad the data
        padded_sensor_data = pad_android_data(sensor_data, report, start_with=start_with, end_with=end_with,
                                              padding_type=padding_type)

    else:  # automatic sync

        # inform the user
        print('Synchronizing from start of {} sensor until end of {} sensor.'.format(report['starting order'][-1],
                                                                                     report['stopping order'][0]))
        print('Using padding type: \'same\'.')

        padded_sensor_data = pad_android_data(sensor_data, report)

    # ---- data re-sampling ---- #
    print('\n---- DATA RE-SAMPLING ----\n')

    # list for holding the re-sampled data
    re_sampled_data = []

    # list for holding the time axes of each sensor
    re_sampled_time = []

    # check for synchroization option
    if (not automatic_sync):

        # set the flag for checking input to false
        check_input1 = False  # for shift_time_axis
        check_input2 = False  # for sampling_rate
        check_input3 = False  # for kind_interp

        # prompt for shift_time_axis
        while (not check_input1):

            # get the input of the user
            # shift_time_axis=False, sampling_rate=None, kind_interp='linear'
            shift_request = input(
                'Do you want to shift the time axis in order to start at zero and convert it to seconds (yes/no)?:')

            # convert to lowercase in case user types 'Yes, YES' or 'No, NO'
            shift_request = shift_request.lower()

            # check for validity
            if (shift_request not in ['yes', 'no']):

                # wrong input: prompt user again
                print('\nInvalid input. \nPlease input either yes or no.\n')

            else:  # correct input

                # check which kind of input the user provided (Yes or No) and set the shift_time_axis accordingly
                if (shift_request == 'yes'):

                    shift_time_axis = True

                else:  # user chose 'no'

                    shift_time_axis = False

                check_input1 = True

        # prompt input for sampling rate
        while (not check_input2):

            # get the input from the user
            sampling_request = input(
                'Please provide a sampling rate (in Hz). The value will be converted to an Integer:')

            # check if input is really a number
            try:

                sampling_rate = int(sampling_request)

                # check if the user decied to input zero
                if (sampling_rate <= 0):

                    print('\nThe sampling rate you chose is invalid.\nPlease input a sampling rate > 0.\n')

                else:  # correct input

                    check_input2 = True

            except ValueError:

                print('\nThe input you provided is not a number.\n')

        # prompt for interpolation type
        interp_types = ['linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next']
        while (not check_input3):

            # get input from the user

            kind_interp = input(
                'Type in the kind of interpolation you want to use. \nYou can choose the folloiwng {}:'.format(
                    interp_types))

            # check the input for validity
            if (kind_interp not in interp_types):

                # wrong input: prompt user again
                print(
                    '\nThe interpolation type you choose is not valid. \nPlease choose from the following types {}.\n'.format(
                        interp_types))

            else:  # input correct

                check_input3 = True

        # cycle over the data and re-sample it
        for data in padded_sensor_data:
            # resample the data ('_' suppreses the output for the sampling rate)
            re_time, re_data, _ = re_sample_data(data[:, 0], data[:, 1:], shift_time_axis=shift_time_axis,
                                                 sampling_rate=sampling_rate, kind_interp=kind_interp)

            # add the the time and data to the lists
            re_sampled_time.append(re_time)
            re_sampled_data.append(re_data)

    else:  # automatic sync

        # get the highest sampling rate and round it accordingly
        sampling_rate = _round_sampling_rate(report['max. sampling rate'])

        # inform the user
        print('The signals will be re-sampled to:  {} Hz.'.format(sampling_rate))
        print('Shifting the time axis to start at zero and converting to seconds.')
        print('Using interpolation type: \'previous\'.')

        # cycle over the sig
        for data in padded_sensor_data:
            # resample the data ('_' suppreses the output for the sampling rate)
            re_time, re_data, _ = re_sample_data(data[:, 0], data[:, 1:], shift_time_axis=True,
                                                 sampling_rate=sampling_rate, kind_interp='previous')

            # add the the time and data to the lists
            re_sampled_time.append(re_time)
            re_sampled_data.append(re_data)

    # ---- Saving data to file ---- #
    print('\n---- Saving Data to file ----\n')

    # create new file header
    new_header = create_android_sync_header(in_path, sampling_rate)

    # save the data to the file
    save_path = save_synchronised_android_data(re_sampled_time[0], re_sampled_data, new_header, out_path,
                                               file_name=sync_file_name)

    # inform the user where the file has been saved
    print('The file has been saved to: {}'.format(save_path))


# ==================================================================================================
# ================================= Private Functions ==============================================
# ==================================================================================================


def _shape_array(array1, array2):
    """
    Function that equalises the input arrays by padding the shortest one using padding type 'same', i.e. replicating
    the last row.

    ----------
    Parameters
    ----------
    array1: list or numpy.array
        Array
    array2: list or numpy.array
        Array

    Return
    ------
    arrays: numpy.array
        Array containing the equal-length arrays.
    """

    # check if the data arrays are of different size
    if (len(array1) != len(array2)):

        # check which array needs to be padded
        if (len(array1) < len(array2)):

            # get the length of the padding
            pad_length = len(array2) - len(array1)

            # pad the first array
            array1 = _pad_data(array1, pad_length)

        else:

            # get the length of the padding
            pad_length = len(array1) - len(array2)

            # pad the second array
            array2 = _pad_data(array2, pad_length)

    # hstack both arrays / concatenate both array horizontally
    arrays = np.hstack([array1, array2])

    return arrays


def _create_h5_file_old(in_paths, new_path):
    """
    Function to create a new .h5 file that contains the copy of the contents of the input file(s).

    in_paths : str or list
        If the input is a string, it is assumed that the two signals are in the same file, else, if the input is a list,
        it is assumed that the two signals are in different file (the list should contain the paths to the two files).
    new_path : str
        The path to create the new file. (default: 'sync_file.h5')

    Returns
    -------
    new_file : h5py Object
        Object of the h5py package containing the new file containing the copy of the contents of the input file(s).
    """
    if type(in_paths) == str:
        in_paths = [in_paths]
    new_file = File(new_path, 'w')
    for in_path in in_paths:
        with File(in_path) as file:
            for attribute in (list(file.attrs.items())):
                new_file.attrs.__setitem__(name=attribute[0], value=attribute[1])
            for key in list(file.keys()):
                new_file.create_group(key)
                for attribute in list(file[key].attrs.items()):
                    new_file[key].attrs.__setitem__(name=attribute[0], value=attribute[1])
                for other_key in list(file[key].keys()):
                    new_file.create_group(key + '/' + other_key)
                    for attribute in list(file[key + '/' + other_key].attrs.items()):
                        new_file[key + '/' + other_key].attrs.__setitem__(name=attribute[0], value=attribute[1])
                    for another_key in list(file[key][other_key]):
                        try:
                            for yet_another_key in list(file[key][other_key][another_key].keys()):
                                try:
                                    for y in list(file[key][other_key][another_key][yet_another_key].keys()):
                                        new_file.create_dataset(name=key + '/' + other_key + '/' + another_key + '/'
                                                                     + yet_another_key + '/' + y,
                                                                data=file[key][other_key][another_key][yet_another_key][
                                                                    y])
                                        for attribute in list(
                                                file[key][other_key][another_key][yet_another_key].attrs.items()):
                                            new_file[key + '/' + other_key + '/' + another_key + '/'
                                                     + yet_another_key + '/' + y].attrs.__setitem__(
                                                name=attribute[0],
                                                value=attribute[1])
                                except:
                                    new_file.create_dataset(
                                        name=key + '/' + other_key + '/' + another_key + '/' + yet_another_key,
                                        data=file[key][other_key][another_key][yet_another_key])
                                    for attribute in list(
                                            file[
                                                key + '/' + other_key + '/' + another_key + '/' + yet_another_key].attrs.items()):
                                        new_file[
                                            key + '/' + other_key + '/' + another_key + '/' + yet_another_key].attrs.__setitem__(
                                            name=attribute[0],
                                            value=attribute[1])
                        except:
                            new_file.create_dataset(name=key + '/' + other_key + '/' + another_key,
                                                    data=list(file[key][other_key][another_key]))
                            for attribute in list(file[key + '/' + other_key + '/' + another_key].attrs.items()):
                                new_file[key + '/' + other_key + '/' + another_key].attrs.__setitem__(name=attribute[0],
                                                                                                      value=attribute[
                                                                                                          1])

    return new_file


def _create_h5_file(in_paths, new_path):
    """
    Function to create a new .h5 file that contains the copy of the contents of the input file(s).

    in_paths : str or list
        If the input is a string, it is assumed that the two signals are in the same file, else, if the input is a list,
        it is assumed that the two signals are in different file (the list should contain the paths to the two files).
    new_path : str
        The path to create the new file. (default: 'sync_file.h5')

    Returns
    -------
    new_file : h5py Object
        Object of the h5py package containing the new file containing the copy of the contents of the input file(s).
    """
    if type(in_paths) == str:
        in_paths = [in_paths]
    new_file = File(new_path, 'w')
    for i, in_path in enumerate(in_paths):
        with File(in_path, 'r') as file:
            for key in list(file.keys()):
                file.copy(source=file[key], dest=new_file, name=key)

    return new_file


def _create_txt_from_str(in_path, channels, new_path):
    """
    This function allows to generate a text file with synchronised signals from the input file.

    ----------
    Parameters
    ----------
    in_path : str
        Path to the file containing the two signals that will be synchronised.
    channels : list
        List with the strings identifying the channels of each signal.
    new_path : str
        The path to create the new file.
    """
    header = ["# OpenSignals Text File Format"]
    files = [bsnb.load(in_path)]
    with open(in_path, encoding="latin-1") as opened_p:
        header.append(opened_p.readlines()[1])
    header.append("# EndOfHeader")

    data = []
    nr_channels = []
    is_integer_data = True
    for file in files:
        for i, device in enumerate(file.keys()):
            nr_channels.append(len(list(file[device])))
            data.append(file[device][channels[i]])

    dephase, s1, s2 = synchronise_signals(data[0], data[1])

    if data[0] is not int or data[1] is not int:
        is_integer_data = False

    # Avoid change in float precision if we are working with float numbers.
    if not is_integer_data:
        round_data_0 = [float('%.2f' % (value)) for value in data[0]]
        round_data_1 = [float('%.2f' % (value)) for value in data[1]]
        round_s_1 = [float('%.2f' % (value)) for value in s1]
        round_s_2 = [float('%.2f' % (value)) for value in s2]
    else:
        round_data_0 = data[0]
        round_data_1 = data[1]
        round_s_1 = s1
        round_s_2 = s2

    # Check which array is aligned.
    old_columns = np.loadtxt(in_path)
    if np.array_equal(round_s_1, round_data_0):
        # Change the second device
        aux = 3 * nr_channels[0]
        columns = old_columns[dephase:, aux:]
        new_file = _shape_array(old_columns[:, :aux], columns)
    elif np.array_equal(round_s_2, round_data_1):
        # Change the first device
        aux = 3 * nr_channels[1]
        columns = old_columns[dephase:, :aux]
        new_file = _shape_array(columns, old_columns[:, aux:])
    else:
        print("The devices are synchronised.")
        return

    # write header to file
    new_header = [h.replace("\n", "") for h in header]
    sync_file = open(new_path, 'w')
    sync_file.write(' \n'.join(new_header) + '\n')

    # write data to file
    for line in new_file:
        if is_integer_data:
            sync_file.write('\t'.join(str(int(i)) for i in line) + '\t\n')
        else:
            sync_file.write('\t'.join(str(i) for i in line) + '\t\n')
    sync_file.close()


def _create_txt_from_list(in_path, channels, new_path):
    """
    This function allows to generate a text file with synchronised signals from the input files.

    ----------
    Parameters
    ----------
    in_path : list
        Paths to the files containing the two signals that will be synchronised.
    channels : list
        List with the strings identifying the channels of each signal.
    new_path : str
        Path to create the new file.
    """

    header = ["# OpenSignals Text File Format"]
    files = [bsnb.load(p) for p in in_path]
    with open(in_path[0], encoding="latin-1") as opened_p:
        with open(in_path[1], encoding="latin-1") as opened_p_1:
            # append both headers
            header.append(opened_p.readlines()[1][:-2] + ', ' + opened_p_1.readlines()[1][3:])

    header.append("# EndOfHeader")

    # lists for holding the read data
    data = []
    nr_channels = []

    # read the data
    for i, file in enumerate(files):
        nr_channels.append(len(list(file)))
        data.append(file[channels[i]])

    # calculate the delay between both signals
    dephase, _, _ = synchronise_signals(data[0], data[1])

    # load original data
    data_1 = np.loadtxt(in_path[0])
    data_2 = np.loadtxt(in_path[1])

    # Check which device lags
    if dephase < 0:

        # second device lags
        # slice the data
        data_2 = data_2[np.abs(dephase):]

    elif dephase > 0:

        # first device lags
        # slice the data
        data_1 = data_1[np.abs(dephase):]

    else:
        # dephase == 0 ---> devices were already syncronised
        print("The devices were already synchronised.")

    # pad data so that both devices are of the same length
    # in case that phase = 0 the data will only be concatenated horizontally
    new_file = _shape_array(data_1, data_2)

    # write header to file
    new_header = [h.replace("\n", "") for h in header]
    sync_file = open(new_path, 'w')
    sync_file.write('\n'.join(new_header) + '\n')

    # writing synchronised data to file
    for line in new_file:
        sync_file.write('\t'.join(str(i) for i in line) + '\t\n')

    # close the file
    sync_file.close()


def _pad_data(data, pad_length, padding_type='same'):
    """
    Function for padding data. The function uses padding type 'same', i.e. it replicates the last row of the data, as default

    ----------
    Parameters
    ----------
    data (numpy.array): the data that is supposed to be padded

    pad_length (int): the length of the padding that is supposed to be applied to data

    padding_type (string, optional): The type of padding applied, either: 'same' or 'zero'. Default: 'same'

    Return
    ------
    padded_data (numpy.array): The data with the padding
    """

    # get the sampling period (or distance between sampling points, for PLUX devices this is always 1)
    # it is assumed that the signals are equidistantly sampled therefore only the distance between to sampling points
    # is needed to calculate the sampling period
    T = data[:, 0][1] - data[:, 0][0]

    if padding_type == 'same':

        # create the 'same' padding array
        padding = np.tile(data[-1, 1:], (pad_length, 1))

    elif padding_type == 'zero':

        # get the number of columns for the zero padding
        num_cols = data.shape[1] - 1  # ignoring the time/sample column

        # create the zero padding array
        padding = np.zeros((pad_length, num_cols))

    else:

        IOError('The padding type you chose is not defined. Use either \'same\ or \'zero\'.')

    # create the time / sample axis that needs to be padded
    start = data[:, 0][-1] + T
    stop = start + (T * pad_length)
    time_pad = np.arange(start, stop, T)
    time_pad = time_pad[:pad_length]  # crop the array if there are to many values

    # expand dimension for hstack operation
    time_pad = np.expand_dims(time_pad, axis=1)

    # hstack the time_pad and the zero_pad to get the final padding array
    pad_array = np.hstack((time_pad, padding))

    # vstack the pad_array and the new_array
    padded_data = np.vstack([data, pad_array])

    return padded_data


