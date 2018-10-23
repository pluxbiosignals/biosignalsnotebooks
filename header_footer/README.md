## Description
With these files, each Notebook inside **biosignalsnotebooks_notebooks** upper directory is read and an header and footer will be incorporated automatically.

The current functionality is particularly important for the project developers, becoming easy to make a single change in "header" and "footer" source code, which is globally applied to all the pre-existent Notebooks.

## Main Files
+ ***main.py** &#x0219D; central file that should be executed in order to add header and footer to each Notebook;
+ ***osf_notebook_class.py*** &#x0219D; supporting file that contains a class responsible for the generation of "blank" *biosignalsnotebooks* templates;
+ ***cell_content_strings.py*** &#x0219D; supporting file that includes a sequence of constants. Each constant stores a Python code in a string format needed for generating header and footer automatically;
