## Description

This folder includes all **Python** files (modules) inside **biosignalsnotebooks** package. A simple description of the main purpose of each module is presented in the following item list.

+ ***__notebook_support__*** &#x0219D; module that contains graphical functions needed for plotting data in specific notebooks;
+ ***aux_functions*** &#x0219D; set of functions (most of them private) to be used in other modules of the package;
+ ***conversion*** &#x0219D; includes a list of functions dedicated to convert units, namely sample number to seconds and raw samples to mV;
+ ***detect*** &#x0219D; functions inside this module ensure that specific events of physiological signals can be detected, giving rise to the signal segmentation;
+ ***extract*** &#x0219D; each physiological signal can be explored in objective terms through time or frequency domain analysis. From each domain different parameters that objectively characterise the signal can be extracted;
+ ***factory*** &#x0219D; with this module and the class inside it, all users can start to create their own notebooks using the **biosignalsnotebooks** styles;
+ ***load*** &#x0219D; all functions responsible for reading data from .txt and .h5 files are defined in this module;
+ ***process*** &#x0219D; processing tasks such as generation of Poincaré plot or smoothing a signal can take place with process module;
+ ***signal_samples*** &#x0219D; *biosignalsnotebooks* project uses different signals in the Notebooks, being this module very useful for managing *biosignalsnotebooks* signal library;
+ ***visualise*** &#x0219D; responsible for ensuring some graphical tasks, like plotting data acquired with *Plux* devices;
