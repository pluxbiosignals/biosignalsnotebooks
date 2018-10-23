"""
File with the set of strings that contain a markdown or code cell content for general application
in the notebooks.

"""

HEADER = """<table width="100%">
    <tr>
        <td style="text-align:left" width="10%" class="border_pre_gradient">
            <a href="../MainFiles/opensignalsfactory.ipynb"><img src="../../images/icons/download.png"></a>
        </td>
        <td style="text-align:left" width="10%" class="border_gradient">
            <a href="../MainFiles/opensignalsfactory.ipynb"><img src="../../images/icons/program.png"></a>
        </td>
        <td></td>
        <td style="text-align:left" width="5%">
            <a href="../MainFiles/opensignalsfactory.ipynb"><img src="../../images/icons/home.png"></a>
        </td>
        <td style="text-align:left" width="5%">
            <a href="../MainFiles/contacts.ipynb"><img src="../../images/icons/contacts.png"></a>
        </td>
        <td style="text-align:left" width="5%">
            <a href="https://pypi.org/project/opensignalsfactory/"><img src="../../images/icons/package.png"></a>
        </td>
        <td style="border-left:solid 3px #009EE3" width="20%">
            <img src="../../images/ost_logo.png">
        </td>
    </tr>
</table>"""

FOOTER = """<hr>
<table width="100%">
    <tr>
        <td style="border-right:solid 3px #009EE3" width="30%">
            <img src="../../images/ost_logo.png">
        </td>
        <td width="35%" style="text-align:left">
            <a href="https://github.com/opensignalsfactory/opensignalsfactory">&#9740; GitHub Repository</a>
            <br>
            <a href="../MainFiles/opensignalsfactory.ipynb">&#9740; Notebook Categories</a>
            <br>
            <a href="https://pypi.org/project/opensignalsfactory/">&#9740; How to install opensignalsfactory Python package ?</a>
            <br>
            <a href="../MainFiles/signal_samples.ipynb">&#9740; Signal Library</a>
        </td>
        <td width="35%" style="text-align:left">
            <a href="../MainFiles/by_diff.ipynb">&#9740; Notebooks by Difficulty</a>
            <br>
            <a href="../MainFiles/by_signal_type.ipynb">&#9740; Notebooks by Signal Type</a>
            <br>
            <a href="../MainFiles/by_tag.ipynb">&#9740; Notebooks by Tag</a>
            <br>
            <br>
        </td>
    </tr>
</table>"""

DESCRIPTION_SIGNAL_SAMPLES = """With *Plux* acquisition systems, a vast set of physiological signals can be acquired.

All the signals that were used in **<span style="color:#009EE3">opensignalsfactory</span>** notebooks have been collected with **bitalino** or **biosignalsplux**, being this page a resource where relevant characteristics of each acquisition are presented, together with a temporal segment of the signal."""

DESCRIPTION_GROUP_BY = """Each Notebook content is summarized in his header through a quantitative scale ('"Difficulty" between 1 and 5 stars) and some keywords (Group of "tags").

Grouping Notebooks by difficulty level, by signal type to which it applies or by tags is an extremelly important task, in order to ensure that the **<span style="color:#009EE3">opensignalsfactory</span>** user could navigate efficiently in this learning environment.
"""

HEADER_ALL_CATEGORIES = """<link rel="stylesheet" href="../../styles/theme_style.css">
<!--link rel="stylesheet" href="../../styles/header_style.css"-->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

<table width="100%">
    <tr>
        <td id="image_td" width="15%" class="header_image_color_i"><div id="image_img"
        class="header_image_i"></div></td>
        <!-- Available classes for "image_td" element:
        - header_image_color_1 (For Notebooks of "Open" Area);
        - header_image_color_2 (For Notebooks of "Acquire" Area);
        - header_image_color_3 (For Notebooks of "Visualise" Area);
        - header_image_color_4 (For Notebooks of "Process" Area);
        - header_image_color_5 (For Notebooks of "Detect" Area);
        - header_image_color_6 (For Notebooks of "Extract" Area);
        - header_image_color_7 (For Notebooks of "Decide" Area);
        - header_image_color_8 (For Notebooks of "Explain" Area);

        Available classes for "image_img" element:
        - header_image_1 (For Notebooks of "Open" Area);
        - header_image_2 (For Notebooks of "Acquire" Area);
        - header_image_3 (For Notebooks of "Visualise" Area);
        - header_image_4 (For Notebooks of "Process" Area);
        - header_image_5 (For Notebooks of "Detect" Area);
        - header_image_6 (For Notebooks of "Extract" Area);
        - header_image_7 (For Notebooks of "Decide" Area);
        - header_image_8 (For Notebooks of "Explain" Area);-->
        <td class="header_text"> Notebook Title </td>
    </tr>
</table>"""

HEADER_MAIN_FILES = """<link rel="stylesheet" href="../../styles/theme_style.css">
<!--link rel="stylesheet" href="../../styles/header_style.css"-->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

<table width="100%">
    <tr>
        <td id="image_td" width="50%" class="header_image_color_2">
            <img id="image_img" src="../../images/ost_logo.png"></td>
        <td class="header_text header_gradient"> Notebook Title </td>
    </tr>
</table>"""

DESCRIPTION_CATEGORY = """<link rel="stylesheet" href="../../styles/theme_style.css">
![OpenSignals_logo](../../images/OS_logo_title.png)

**<span style="color:#009EE3">OpenSignals Tools</span>** is set of documents and a **<span class="color1">Python</span>** library to provide programming examples in the form of **<span class="color5">Jupyter Notebooks</span>**, as companion to the **<span style="color:#009EE3">OpenSignals</span>** biosignals acquisition tools.

This collection of code samples has the purpose to help users of PLUX Wireless Biosignals systems, such as **bitalino** or **biosignalsplux**, and to the researcher or student interested on recording processing and classifying biosignals. The examples are set on a level of complexity to inspire the users and programmers on how easy some tasks are and that more complex ones can also be achieved, by reusing and recreating some of the examples presented here.

A **<span class="color1">Python</span>** library (entitled **<span style="color:#009EE3">opensignalsfactory</span>** ) is the base toolbox to support the notebooks and to provide some useful functionalities. It can be installed through pip command, like demonstrated in a [PyPI <img src="../../images/icons/link.png" width="10px" height="10px" style="display:inline">](https://pypi.org/project/opensignalsfactory/) dedicated page.

In many cases we also point and illustrate with code the usage of other python toolboxes dedicated to biosignal processing.

The notebooks will cover the full topics pipeline of working with biosignals: **<span class="color1">Open</span>** a file; **<span class="color3">Visualise</span>** the data online and offline, **<span class="color4">Process</span>** a one channel signal or a multi-channel acquisition, **<span class="color5">Detect</span>** relevant events in the signals, **<span class="color6">Extract</span>** features from many different type of sensors and domains, **<span class="color7">Decide</span>** among a set of classes with several machine learning approaches, **<span class="color8">Explain</span>** the obtained results with metrics and validations techniques.

These examples are carried in a multitude of biosignals , from ECG, EDA, EMG, Accelerometer, Respiration among many others.
The notebooks have a set of labels to help navigate among topics <...>, types of signals <...>, application area <...> and complexity <...> level to support the search for particular solutions.

We encourage you to share new example ideas, to pose questions :::ADD email here:::, and to make improvements or suggestion to this set of notebooks.

**Be inspired on how to make the most of your biosignals!**

<br>

<div class="title"><h2 class="color11"> Available Notebooks </h2></div>"""

HEADER_TAGS = """<div id="flex-container">
    <div id="diff_level" class="flex-item">
        <strong>Difficulty Level:</strong>   <span class="fa fa-star 1"></span>
                                <span class="fa fa-star 2"></span>
                                <span class="fa fa-star 3"></span>
                                <span class="fa fa-star 4"></span>
                                <span class="fa fa-star 5"></span>
    </div>
    <div id="tag" class="flex-item-tag">
        <span id="tag_list">
            <table id="tag_list_table">
                <tr>
                    <td class="shield_left">Tags</td>
                    <td class="shield_right" id="tags">tags</td>
                </tr>
            </table>
        </span>
        <!-- [OR] Visit https://img.shields.io in order to create a tag badge-->
    </div>
</div>"""

SEPARATOR = """<hr>"""

AUX_CODE_MESSAGE = """<span class="color6">**Auxiliary Code Segment (should not be replicated by
the user)**</span>"""

CSS_STYLE_CODE = """from opensignalsfactory.__notebook_support__ import css_style_apply
css_style_apply()"""

FOOTER = """<hr>
<table width="100%">
    <tr>
        <td style="border-right:solid 3px #009EE3" width="30%">
            <img src="../../images/ost_logo.png">
        </td>
        <td width="35%" style="text-align:left">
            <a href="https://github.com/opensignalsfactory/opensignalsfactory">&#9740; GitHub Repository</a>
            <br>
            <a href="../MainFiles/opensignalsfactory.ipynb">&#9740; Notebook Categories</a>
            <br>
            <a href="https://pypi.org/project/opensignalsfactory/">&#9740; How to install opensignalsfactory Python package ?</a>
            <br>
            <a href="../MainFiles/signal_samples.ipynb">&#9740; Signal Library</a>
        </td>
        <td width="35%" style="text-align:left">
            <a href="../MainFiles/by_diff.ipynb">&#9740; Notebooks by Difficulty</a>
            <br>
            <a href="../MainFiles/by_signal_type.ipynb">&#9740; Notebooks by Signal Type</a>
            <br>
            <a href="../MainFiles/by_tag.ipynb">&#9740; Notebooks by Tag</a>
            <br>
            <br>
        </td>
    </tr>
</table>"""

# 11/10/2018 16h45m :)
