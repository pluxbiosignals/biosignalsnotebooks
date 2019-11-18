
<img src="https://i.ibb.co/rbtv3dW/OS-logo-title-slim.png">

[![Python](https://img.shields.io/badge/python-3.6-blue.svg)]()
[![html5](https://img.shields.io/badge/html-5-green.svg)]()
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/biosignalsplux/biosignalsnotebooks/mybinder_complete?filepath=biosignalsnotebooks_environment%2Fcategories%2FMainFiles%2Fbiosignalsnotebooks.ipynb)

## Description

**<span style="color:#009EE3">biosignalsnotebooks</span>** is a set of documents and a **<span style="color: #62C3EE">Python</span>** library to provide programming examples in the form of **<span style="color:#72BE94">Jupyter Notebooks</span>**, as companion to the **<span style="color:#009EE3">OpenSignals</span>** biosignals acquisition tools.

This collection of code samples has the purpose to help users of PLUX Wireless Biosignals systems, such as **bitalino** or **biosignalsplux**, and to the researcher or student interested on recording processing and classifying biosignals. The examples are set on a level of complexity to inspire the users and programmers on how easy some tasks are and that more complex ones can also be achieved, by reusing and recreating some of the examples presented here.

A **<span style="color: #62C3EE">Python</span>** library (entitled **<span style="color:#009EE3">biosignalsnotebooks</span>** ) is the base toolbox to support the notebooks and to provide some useful functionalities. It can be installed through pip command, like demonstrated in a [PyPI <img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline">](https://pypi.org/project/biosignalsnotebooks/) dedicated page.

In many cases we also point and illustrate with code the usage of other python toolboxes dedicated to biosignal processing.

The notebooks will cover the full topics pipeline of working with biosignals, such as: **<span style="color: #62C3EE">Load</span>** a file; **<span style="color:#AFE1F6">Visualise</span>** the data online and offline, **<span style="color:#00893E">Pre-Process</span>** a one channel signal or a multi-channel acquisition, **<span style="color:#72BE94">Detect</span>** relevant events in the signals, **<span style="#A8D7BD">Extract</span>** features from many different type of sensors and domains, **<span style="#CF0272">Train and Classify</span>** among a set of classes with several machine learning approaches, **<span style="#F0B2D4">Understand</span>** the obtained results with metrics and validations techniques.

These examples are carried in a multitude of biosignals , from ECG, EDA, EMG, Accelerometer, Respiration among many others.
The notebooks have a set of labels to help navigate among topics <a href="http://biosignalsplux.com/notebooks/Categories/MainFiles/by_tag_rev.php"><img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline"></a>, types of signals <a href="http://biosignalsplux.com/notebooks/Categories/MainFiles/by_signal_type_rev.php"><img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline"></a>, application area <a href="http://biosignalsplux.com/notebooks/Categories/MainFiles/biosignalsnotebooks_rev.php"><img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline"></a> and complexity <a href="http://biosignalsplux.com/notebooks/Categories/MainFiles/by_diff_rev.php"><img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline"></a> level to support the search for particular solutions.

We encourage you to share new example ideas, to pose questions info@plux.info, and to make improvements or suggestion to this set of notebooks.

**Be inspired on how to make the most of your biosignals!**


## Available Notebooks

<table width="100%">
    <tr>
        <td width="20%" align="center"><strong> Category <strong></td>
        <td width="80%"></td>
    </tr>
	<tr>
		<td rowspan='2'><p align='center'><img src='https://i.ibb.co/LgrhTz9/Install.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Install/prepare_anaconda_rev.php' target='_blank'> Download, Install and Execute Anaconda </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Install/prepare_jupyter_rev.php'> Download, Install and Execute Jupyter Notebook Environment </a> </td>
	</tr>
	<tr>
		<td rowspan='1'><p align='center'><img src='https://i.ibb.co/8cNpQFM/Connect.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Connect/pairing_device_rev.php' target='_blank'> Pairing a Device at Windows 10 [biosignalsplux] </a> </td>
	</tr>
	<tr>
		<td rowspan='5'><p align='center'><img src='https://i.ibb.co/d2jZH1s/Record.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Record/eeg_electrode_placement_rev.php' target='_blank'>EEG - Electrode Placement </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Record/record_data_rev.php'> Signal Acquisition [OpenSignals] </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Record/resolution_rev.php'> Resolution - The difference between smooth and abrupt variations </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Record/sampling_rate_and_aliasing_rev.php'>Problems of low sampling rate (aliasing)</a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Record/store_signals_after_acquisition_rev.php'> Store Files after Acquisition [OpenSignals] </a> </td>
	</tr>
	<tr>
		<td rowspan='5'><p align='center'><img src='https://i.ibb.co/YPbCnzD/Load.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Load/dataload_eeg_physionet_rev.php' target='_blank'> EEG - Loading Data from PhysioNet</a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Load/open_h5_rev.php'>Load acquired data from .h5 file</a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Load/open_signals_after_acquisition_rev.php'> Load Signals after Acquisition [OpenSignals] </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Load/open_txt_rev.php'>Load acquired data from .txt file</a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Load/signal_loading_preparatory_steps_rev.php'>Signal Loading - Working with File Header </a> </td>
	</tr>
	<tr>
		<td rowspan='10'><p align='center'><img src='https://i.ibb.co/1rKWccX/Pre-Process.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/digital_filtering_rev.php' target='_blank'> Digital Filtering - A Fundamental Pre-Processing Step </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/digital_filtering_eeg_rev.php'> Digital Filtering - EEG </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/emg_fatigue_evaluation_median_freq_rev.php'>Fatigue Evaluation - Evolution of Median Power Frequency</a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/generation_of_time_axis_rev.php'> Generation of a time axis (conversion of samples into seconds) </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/synchronisation_rev.php'> Device Synchronisation - Cable, Light and Sound Approaches </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/unit_conversion_ACC_rev.php'>ACC Sensor - Unit Conversion </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/unit_conversion_ecg_rev.php'>ECG Sensor - Unit Conversion </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/unit_conversion_eeg_rev.php'>EEG Sensor - Unit Conversion </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/unit_conversion_emg_rev.php'>EMG Sensor - Unit Conversion </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Pre-Process/unit_conversion_fNIRS_rev.php'>fNIRS Sensor - Unit Conversion </a> </td>
	</tr>
	<tr>
		<td rowspan='2'><p align='center'><img src='https://i.ibb.co/rymrvFL/Detect.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Detect/detect_bursts_rev.php' target='_blank'> Event Detection - Muscular Activations (EMG) </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Detect/r_peaks_rev.php'> Event Detection - R Peaks (ECG) </a> </td>
	</tr>
	<tr>
		<td rowspan='2'><p align='center'><img src='https://i.ibb.co/tchq7Cc/Extract.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Extract/eeg_extract_alphaband_rev.php' target='_blank'> EEG - Alpha Band Extraction </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Extract/emg_parameters_rev.php'> EMG Analysis - Time and Frequency Parameters </a> </td>
	</tr>
	<tr>
		<td rowspan='5'><p align='center'><img src='https://i.ibb.co/CQ4cyGb/Train-and-Classify.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Train_And_Classify/biosignal_classification_rev.php' target='_blank'> Signal Classifier - Distinguish between EMG and ECG </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Train_And_Classify/classification_game_orange_rev.php'> Rock, Paper or Scissor Game - Train and Classify [Orange] </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Train_And_Classify/classification_game_volume_1_rev.php'> Rock, Paper or Scissor Game - Train and Classify [Volume 1] </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Train_And_Classify/classification_game_volume_2_rev.php'> Rock, Paper or Scissor Game - Train and Classify [Volume 2] </a> </td>
	</tr>
	<tr>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Train_And_Classify/classification_game_volume_3_rev.php'> Rock, Paper or Scissor Game - Train and Classify [Volume 3] </a> </td>
	</tr>
	<tr>
		<td rowspan='1'><p align='center'><img src='https://i.ibb.co/yfwcy2M/Evaluate.png' width='50%' align='center'></p></td>
		<td align='center'> <a href='http://www.biosignalsplux.com/notebooks/Categories/Evaluate/classification_game_volume_4_rev.php' target='_blank'> Rock, Paper or Scissor Game - Train and Classify [Volume 4] </a> </td>
	</tr>
</table>

## What is **PLUX**

PLUX wireless biosignals is devoted to the creation innovative products for advanced biosignals monitoring platforms
that integrate wearable body sensors combined with wireless connectivity, algorithms and software applications.

We have been perusing the mission of making biosignals as accessible as possible to researchers and students in many areas of application, ranging from biomedical engineering, computer science, human computer interaction, sport sciences, psychology, clinical research among other fields.

## Plux's Software and Hardware Environment

[**OpenSignals**](http://biosignalsplux.com/en/software/opensignals) is the companion application to *Plux* devices ([**bitalino**](http://bitalino.com/en/) or [**biosignalsplux**](http://biosignalsplux.com/en/)) where the users collect visualize an process biosignals in a intuitive user interface. Opensignals is free and can be used also with signals collected form other devices.

In some cases **OpenSignals** provides [*plugins*](http://biosignalsplux.com/en/software/add-ons) for advanced signals processing operations that automate some of the research process. Some of the plugins are curated and advanced versions of the base notebooks explained in here.

The list of plugins can be found here: http://biosignalsplux.com/en/software/add-ons

## Access to biosignalsnotebooks Notebooks

<a href="http://biosignalsplux.com/notebooks/Categories/MainFiles/biosignalsnotebooks_rev.php">
    <p align="center">
      <img src="https://image.ibb.co/ingFWV/bsnb-logo-animation.gif" width="40%">
    </p>
</a>

*For viewing biosignalsnotebooks .ipynb files correctly formatted and with the right CSS configurations the user should access the link contained in the previous image instead of navigating manually through the files in GitHub repository*

## Notebook Publication Status

Publication status is available in a [**Google Spreadsheet**](https://docs.google.com/spreadsheets/d/1Hyt7iLidHzDLHTeXrIsrWGlcmKCHTPwtS_d5KYpTSpA/edit?usp=sharing)

## Installation of biosignalsnotebooks package
In order to *biosignalsnotebooks* package be installed, the user should open a Windows command prompt (by searching for "cmd") and type the following instruction:
```
pip install biosignalsnotebooks
```
