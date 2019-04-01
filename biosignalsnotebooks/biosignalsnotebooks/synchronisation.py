import biosignalsnotebooks as bsnb
import numpy as np
from h5py import File


def synchronise_signals(in_signal_1, in_signal_2):
    """
    -----
    Brief
    -----
    This function synchronises the input signals.

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
    This functions creates .txt and .h5 files with synchronised signals.

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
