## Description
In order to **biosignalsnotebooks** be massively disseminated and accessible for all users of *Plux's* devices, **.ipynb** are converted to **.html** format.

After the conversion process is done, the **.html** Notebooks can easily be published online like a normal website.

## Main Files
+ ***main.py** &#x0219D; central file that should be executed in order to start the conversion of each Notebook;
+ ***CustomPreprocessor.py*** &#x0219D; formed by some instructions (pre-process configurations) used by [nbconvert <img src="https://image.ibb.co/cNnx6V/link.png" width="10px" height="10px" style="display:inline">](https://github.com/jupyter/nbconvert) function before conversion task starts;
+ ***nbconvertTemplate.py*** &#x0219D; code that should be executed in Python console before running *main.py*. It is responsible for the generation of a template.tpl to be taken into account during the conversion task;
+ ***my_template.tpl*** &#x0219D; file generated after executing code instructions inside *nbconvertTemplate.py*.

*In "biosignalsnotebooks_html" folder are stored all .html files generated during the conversion task*
