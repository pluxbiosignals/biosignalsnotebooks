from h5py import File
import json
from os.path import splitext, join
from datetime import datetime

HOUR = 3600
MIN = 60
SEC = 1

def read_h5(path):
    """
    Function to read a .h5 file with a structure provided by OpenSignals and construct a dictionary with the more
    relevant information about each signal.
    
    ----------
    Parameters
    ----------
    path : str
        Absolute or relative path to the .h5 file to be read.
    
    Returns
    -------
    dic : dict
        Dictionary with the relevant information of the .h5 file. Keys:
        Sample Rate
        Number of Channels
        Signal Type
        Acquisition Time
        Resolutions
    """
    file = File(path)
    dic = {"Sample Rate": [], "Acquisition Time": [], "Resolutions": [], "Signal Type": [], "Number of Channels": []}
    for mac in list(file.keys()):
        device = file[mac]
        char_to_remove = {ord(i):None for i in '[]\''}
        sampling_rate = device.attrs["sampling rate"]
        dic["Sample Rate"].append(str(sampling_rate))
        samples = device.attrs["nsamples"]
        time_sec = samples / sampling_rate
        time = datetime.fromtimestamp(time_sec).strftime("%H:%M:%S.") + str(datetime.fromtimestamp(time_sec).microsecond//1000)[:1]
        dic["Acquisition Time"].append(time)
        ch_counter = 0
        dic["Resolutions"].append(str([str(res) + " bits" for res in device.attrs["resolution"]]).translate(char_to_remove))
        for channel in list(device["raw"].keys()):
            if "channel" in channel:
                sensor = device["raw"][channel].attrs["sensor"].decode("utf-8")
                if sensor == "RAW":
                    print("The type of signal is set to RAW. You need to specify the type of signal (sensor): ")
                    sensor = input()
                dic["Signal Type"].append(sensor)
                ch_counter += 1
        dic["Number of Channels"].append(str(ch_counter))
    
    for key in dic.keys():
        dic[key] = str(dic[key]).translate(char_to_remove)
	
    return dic

def write_json_info(path, observations=""):
    """
    Function to write a JSON file from a dictionary. It is intended to be used to
	construct the file with the most relevant information from a given .h5 file.
    
    ----------
	Parameters
    ----------
    path : str
        Absolute or relative path to the .h5 file to be read.
    observations : str
        Observations of the signal(s) from the input .h5 file.
    """
    dic = read_h5(path)
    dic["Observations"] = observations
    with open(splitext(path)[0]+'_info.json', 'w') as file:
        json.dump(dic, file)

# path = "C:/Users/gui_s/Documents/biosignalsnotebooks_org/biosignalsnotebooks_notebooks/signal_samples/bvp_rest.h5"
path = "../biosignalsnotebooks_notebooks/signal_samples/"  # Don't need to change this line
file = "GON.h5"
write_json_info(join(path, file), "A conventional goniometer signal acquisition with limb movement over time") # Only need to change the observations of the file