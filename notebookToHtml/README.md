## Description
In order to **biosignalsnotebooks** be massively disseminated and accessible for all users of *Plux's* devices, **.ipynb** are converted to **.html** format.

After the conversion process is done, the **.html** Notebooks can easily be published online like a normal website.

## Main Files
+ ***main.py*** &#x0219D; central file that should be executed in order to start the conversion of each Notebook;
+ ***CustomPreprocessor.py*** &#x0219D; formed by some instructions (pre-process configurations) used by [nbconvert <img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline">](https://github.com/jupyter/nbconvert) function before conversion task starts;
+ ***CustomPreprocessorIndex.py*** &#x0219D; like ***CustomPreprocessor.py***, this file will be used by nbconvert before the conversion tasks start. However, it will be specifically applied before conversion of some "MainFiles";
+ ***nbconvertTemplate.py*** &#x0219D; code that should be executed in Python console before running *main.py*. It is responsible for the generation of a template.tpl to be taken into account during the conversion task;
+ ***nbconvert_config.py*** &#x0219D; a file where the nbconvert pre-processors and export format are specified;
+ ***nbconvert_config_index.py*** &#x0219D; identical to ***nbconvert_config.py*** but applicable to "MainFiles";
+ ***index.php*** &#x0219D; a .php template that is extremelly useful for a correct integration of **biosignalsnotebooks** html files on [**biosignalnsplux** <img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline">](http://biosignalsplux.com/) website; 
+ ***my_template.tpl*** &#x0219D; file generated after executing code instructions inside *nbconvertTemplate.py*.

*In "biosignalsnotebooks_html" or "biosignalsnotebooks_html_publish" folders are stored all .html files generated during the conversion task*
