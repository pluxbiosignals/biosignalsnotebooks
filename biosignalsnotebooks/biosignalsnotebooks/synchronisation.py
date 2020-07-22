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
    function in order to creating a new header for a synchronized android sensor file

pad_android_data
    function in order to pad multiple android signals to the correct same start and end values

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

Observations/Comments
---------------------
None

/\
"""
import json
import biosignalsnotebooks as bsnb
import numpy as np
from h5py import File


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

    mean_1, std_1, mean_2, std_2 = [np.mean(in_signal_1), np.std(in_signal_1), np.mean(in_signal_2),
                                    np.std(in_signal_2)]
    signal_1 = in_signal_1 - mean_1
    signal_1 /= std_1
    signal_2 = in_signal_2 - mean_2
    signal_2 /= std_2

    # Calculate the full cross-correlation between the two signals.
    correlation = np.correlate(signal_1, signal_2, 'full')

    # Finding the edge of the correct correlation signal
    center = len(correlation) - len(signal_1) if len(signal_1) < len(signal_2) else len(correlation) - len(signal_2)

    # Finding the position of the maximum value of the correlation signal
    max_position = correlation.argmax()
    # Calculating the difference between the center and the position of the maximum value
    phase_straight = center - max_position

    # Finding the position of the maximum value of the reversed signal (corr[::-1])
    max_position_reversed = correlation[::-1].argmax()
    # Calculating the difference between the center and the position of the maximum value in the reversed correlation
    # signal
    phase_reversed = center - max_position_reversed

    # Calculate the dephasing between the signals. Maximum value of both results guarantees that we find the true
    # dephasing of the signals
    phases_aux = [phase_straight, phase_reversed]
    phase = np.abs(phases_aux).argmax()
    true_phase = np.abs(phases_aux[phase])

    if phases_aux[0] < phases_aux[1]:
        signal_1 = signal_1[true_phase:]
    else:
        signal_2 = signal_2[true_phase:]

    result_signal_1 = signal_1 * std_1 + mean_1
    result_signal_2 = signal_2 * std_2 + mean_2

    return true_phase, result_signal_1, result_signal_2


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


def create_android_sync_header(in_path):

    '''
    function in order to creating a new header for a synchronized android sensor file
    (i.e. multiple android sensor files into one single file)
    Parameters
    ----------
    in_path (list of strings or string): list containing the paths to the files that are supposed to be synchronized

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

                # add the fields from the header of the current file
                header['internal sensors']['sensor'].extend(curr_header['internal sensors']['sensor'])  # sensor field
                header['internal sensors']['column'].extend(
                    curr_header['internal sensors']['column'][1:])  # column field

                # get the last channel from the channel field
                num_channels = header['internal sensors']['channels'][-1]

                # get the channels from the current sensor
                new_channels = curr_header['internal sensors']['channels']

                # adjust the channel number
                new_channels = [ch + (num_channels + 1) for ch in new_channels]

                header['internal sensors']['channels'].extend(new_channels)  # channels field
                header['internal sensors']['label'].extend(
                    curr_header['internal sensors']['label'])  # label field
                header['internal sensors']['resolution'].extend(
                    curr_header['internal sensors']['resolution'])  # resolution field
                header['internal sensors']['special'].extend(
                    curr_header['internal sensors']['special'])  # special field
                header['internal sensors']['sleeve color'].extend(
                    curr_header['internal sensors']['sleeve color'])  # sleeve color field

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
    let's assume an acquistion was made with the following sensors Acc, GPS, Light, and Proximity.
    The sensors start acquiring data in the following order: ['Proximity', 'Light', 'Acc', 'GPS']
    The sensor stop acquiring data in the following order: ['Proximity', 'Light', 'GPS', 'Acc']

    Then the user can specify where to start and end the synchronization by for example setting:
    start_with='Proximity', and
    stop_with='GPS'
    In this case the signals are synchronized when the Proximity sensor starts recording until the GPS sensor stops
    recording data. The other sensors are padded / cropped to the corresponding starting / stopping points.
    At the beginning:The 'Light', 'Acc', and 'GPS' sensors are padded to the staring point of the Proximity sensor
    At the end: The 'Proximity' and 'Light' sensors are padded until the stopping point of the 'GPS' sensor and the
                'Acc' sensor is cropped to the stopping point of the GPS sensor.

    Parameters
    ----------
    sensor_data (list): A list containing the data of the sensors to be synchronized.

    report (dict): The report returned by the 'load_android_data' function.

    start_with (string, optional): The sensor that indicates that indicates when the synchronization should be started.
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
                    'The configuration you chose led to elimination of the {} sensor. Please choose another sensor for paremeter \'end\'.'.format(
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

            # concatenate the channel to the padded data
            padded_data = np.vstack((padded_data, sig_channel))

        # append the data to the padded_sensor_data list
        # the data is transposed in order to have the correct shape (samples x number of channels)
        padded_sensor_data.append(padded_data.T)

    return padded_sensor_data


    # TODO: android synchronization function that does basically everything, the user only has to give the file_list
# ==================================================================================================
# ================================= Private Functions ==============================================
# ==================================================================================================


def _shape_array(array1, array2):
    """
    Function that equalises the input arrays by zero-padding the shortest one.

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
    if len(array1) > len(array2):
        new_array = array2
        old_array = array1
    else:
        new_array = array1
        old_array = array2

    length = len(old_array) - len(new_array)

    for i in range(length):
        n = new_array[-1].copy()
        n[0::3] += 1
        n[2::3] = 0
        new_array = np.vstack([new_array, [n]])

    arrays = np.hstack([old_array, new_array])
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
    for file in files:
        for i, device in enumerate(file.keys()):
            nr_channels.append(len(list(file[device])))
            data.append(file[device][channels[i]])

    dephase, s1, s2 = synchronise_signals(data[0], data[1])

    new_header = [h.replace("\n", "") for h in header]
    sync_file = open(new_path, 'w')
    sync_file.write(' \n'.join(new_header) + '\n')

    old_columns = np.loadtxt(in_path)
    if np.array_equal(s1, data[0]):
        # Change the second device
        aux = 3 * nr_channels[0]
        columns = old_columns[dephase:, aux:]
        new_file = _shape_array(old_columns[:, :aux], columns)
    elif np.array_equal(s2, data[1]):
        # Change the first device
        aux = 3 * nr_channels[1]
        columns = old_columns[dephase:, :aux]
        new_file = _shape_array(columns, old_columns[:, aux:])
    else:
        print("The devices are synchronised.")
        return
    for line in new_file:
        sync_file.write('\t'.join(str(int(i)) for i in line) + '\t\n')
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
            header.append(opened_p.readlines()[1][:-2] + ', ' + opened_p_1.readlines()[1][3:])
    header.append("# EndOfHeader")

    data = []
    nr_channels = []
    for i, file in enumerate(files):
        nr_channels.append(len(list(file)))
        data.append(file[channels[i]])

    dephase, s1, s2 = synchronise_signals(data[0], data[1])

    new_header = [h.replace("\n", "") for h in header]
    sync_file = open(new_path, 'w')
    sync_file.write('\n'.join(new_header) + '\n')

    if np.array_equal(s1, data[0]):
        # Change the second device
        old_columns = np.loadtxt(in_path[1])
        columns = old_columns[dephase:]
        new_file = _shape_array(columns, np.loadtxt(in_path[0]))
    elif np.array_equal(s2, data[1]):
        # Change the first device
        old_columns = np.loadtxt(in_path[0])
        columns = old_columns[dephase:]
        new_file = _shape_array(columns, np.loadtxt(in_path[1]))
    else:
        print("The devices are synchronised.")
        return
    for line in new_file:
        sync_file.write('\t'.join(str(int(i)) for i in line) + '\t\n')
    sync_file.close()
