"""
OpenSignalsTools module intended to give the user the possibility of programmatically generate a
Notebook.

"""

import json
import os
import re
import shutil
import warnings
import importlib.util

import nbformat as nb
from .notebook_files.MainFiles.group_by_difficulty import STAR_TABLE_HEADER
from .notebook_files.MainFiles.group_by_tag import TAG_TABLE_HEADER

from .notebook_files.MainFiles.signal_samples import IMPORT_CODE, PLOTS_SIGNAL_SAMPLES

from .notebook_files.cell_content_strings import DESCRIPTION_GROUP_BY, DESCRIPTION_SIGNAL_SAMPLES, \
                                 HEADER_ALL_CATEGORIES, HEADER_MAIN_FILES, \
                                 DESCRIPTION_CATEGORY, HEADER_TAGS, SEPARATOR, AUX_CODE_MESSAGE, \
                                 JS_CODE_AUTO_PLAY, CSS_STYLE_CODE, FOOTER, HEADER, MD_EXAMPLES, \
                                 CODE_EXAMPLES, OPEN_IMAGE

SIGNAL_TYPE_LIST = ["emg", "ecg"]

NOTEBOOK_KEYS = {"Install": 13, "Connect": 14, "Record": 2, "Load": 1, "Visualise": 3, "Pre-Process": 4, "Detect": 5,
                 "Extract": 6, "Train_And_Classify": 7, "Understand": 8, "Evaluate": 12,
                 "Other": 15, "MainFiles": 0}

# ==================================================================================================
# ======================================= notebook Class ===========================================
# ==================================================================================================


class notebook:
    def __init__(self, notebook_type=None, notebook_title="Notebook Title", tags="tags",
                 difficulty_stars=1, notebook_description="Notebook Description",
                 dict_by_difficulty=None, dict_by_tag=None, notebook_file=None, new_notebooks=[]):
        """
        -----
        Brief
        -----
        Class constructor that generates a new Notebook template, taking into account the
        specified 'notebook_type'.

        -----------
        Description
        -----------
        OpenSignals notebooks have specific templates according to different types. They possess specific headers,
        footers and general arrangement and features, such as, the way of presenting the difficulty level and keywords.
        All of these elements need to be implemented using HTML and CSS in order to use all functionalities of the
        jupyter notebook environment.
        That environment allows to easily and clearly present and compile Python code as well as information in markdown
        cells, and has been widely used in data mining applications.

        This class allows to generate a jupyter notebook template in order to facilitate content creation without the
        need to worry about the design.

        ----------
        Parameters
        ----------
        notebook_type : str
            Notebook type: - "Main_Files_Signal_Samples"
                           - "Main_Files_By_Category"
                           - "Main_Files_By_Difficulty"
                           - "Main_Files_By_Tag"
                           - "Main_Files_By_Signal_Type"
                           - "Acquire"
                           - "Open"
                           - "Visualise"
                           - "Process"
                           - "Detect"
                           - "Extract"
                           - "Train_And_Classify"
                           - "Explain"

        notebook_title : None or str
            The Notebook title should only be defined when 'notebook_type' is:
           - "Acquire"
           - "Open"
           - "Visualise"
           - "Process"
           - "Detect"
           - "Extract"
           - "Train_And_Classify"
           - "Explain"

        tags : str
            Sequence of tags that characterize the Notebook.

        difficulty_stars : int
            This input defines the difficulty level of the Notebook instructions.

        notebook_description : str
            An introductory text to present the Notebook and involve the reader.

        dict_by_difficulty : dict
            Global Dictionary that groups Notebooks names/files by difficulty level.

        dict_by_tag : dict
            Dictionary where each key is a tag and the respective value will be a list containing the
            Notebooks (title and filename) that include this tag.

        notebook_file : str
            Notebook filename.

        new_notebooks : list
            List containing the set of NEW notebooks where the "NEW" tag will be added.
        """

        # ========================= Initialisation of Object variables =============================
        self.difficulty_stars = difficulty_stars
        self.tags = tags
        self.notebook_title = notebook_title

        # =============================== Creation of a Notebook ===================================
        self.notebook = nb.v4.new_notebook()

        if "Main" in notebook_type:
            warnings.warn("The arguments 'tags' and 'difficulty_stars' does not have effect for "
                          "the " + notebook_type + " notebook type !")

        if notebook_type in ["Load", "Record", "Visualise", "Pre-Process", "Detect",
                             "Extract", "Train_And_Classify", "Understand", "Evaluate", "Other", "Install", "Connect"]:
            self.notebook_type = notebook_type
            _generate_header(self.notebook, self.notebook_type, notebook_file)
            _generate_notebook_header(self.notebook, notebook_type, notebook_title, tags,
                                      difficulty_stars, notebook_description)

        elif notebook_type == "Main_Files_By_Category":
            self.notebook_type = "MainFiles"
            _generate_header(self.notebook, self.notebook_type, notebook_file)
            _generate_notebooks_by_category(self.notebook, dict_by_tag, new_notebooks=new_notebooks)
            if os.path.exists("../biosignalsnotebooks_notebooks"):
                _generate_github_readme(self.notebook, dict_by_tag)

        elif notebook_type == "Main_Files_Signal_Samples":
            self.notebook_type = "MainFiles"
            _generate_header(self.notebook, self.notebook_type, notebook_file)
            _generate_main_files_header(self.notebook, notebook_title, DESCRIPTION_SIGNAL_SAMPLES)
            _generate_signal_samples_body(self.notebook)

        elif notebook_type == "Main_Files_By_Difficulty":
            self.notebook_type = "MainFiles"
            _generate_header(self.notebook, self.notebook_type, notebook_file)
            _generate_main_files_header(self.notebook, notebook_title, DESCRIPTION_GROUP_BY)
            #opensignals_hierarchy()
            _generate_notebook_by_difficulty_body(self.notebook, dict_by_difficulty)

        elif notebook_type == "Main_Files_By_Tag":
            self.notebook_type = "MainFiles"
            _generate_header(self.notebook, self.notebook_type, notebook_file)
            _generate_main_files_header(self.notebook, notebook_title, DESCRIPTION_GROUP_BY)
            # opensignals_hierarchy()
            _generate_notebook_by_tag_body(self.notebook, dict_by_tag)

        elif notebook_type == "Main_Files_By_Signal_Type":
            self.notebook_type = "MainFiles"
            _generate_header(self.notebook, self.notebook_type, notebook_file)
            _generate_main_files_header(self.notebook, notebook_title, DESCRIPTION_GROUP_BY)
            # opensignals_hierarchy()
            _generate_notebook_by_signal_type_body(self.notebook, dict_by_tag)

    def write_to_file(self, path, filename, footer=True, group_by=False):
        """
        -----
        Brief
        -----
        Class method responsible for generating a file containing the notebook object data.

        -----------
        Description
        -----------
        biosignalsnotebooks allows to create jupyter notebook objects that includes all of the information required to
        generate a jupyter notebook file.

        This function write a jupyter notebook file from a jupyter notebook object.

        ----------
        Parameters
        ----------
        path : str
            OpenSignalsTools Root folder path (where the notebook will be stored).

        filename : str
            Defines the name of the notebook file.

        footer : bool
            Flag that defines when the footer needs to be included in the Notebook.

        group_by : bool
            If True then the group by pages that compose the biosignalsnotebooks project will be
            automatically generated (grouping Notebooks by difficulty, tags ...)
        """

        # =============================== Storage of Filename ======================================
        self.filename = filename

        # ======================== Inclusion of Footer in the Notebook =============================
        if footer is True:
            _generate_footer(self.notebook, self.notebook_type)

        # ========== Code segment for application of the OpenSignalsTools CSS style ===========
        self.notebook["cells"].append(nb.v4.new_markdown_cell(AUX_CODE_MESSAGE,
                                                              **{"metadata":
                                                                     {"tags": ["hide_mark",
                                                                               "aux"]}}))
        self.notebook["cells"].append(nb.v4.new_code_cell(CSS_STYLE_CODE,
                                                          **{"metadata":
                                                                 {"tags": ["hide_both"]}}))
        self.notebook["cells"].append(nb.v4.new_code_cell(JS_CODE_AUTO_PLAY,
                                                          **{"metadata":
                                                                 {"tags": ["hide_both"]}}))

        full_path = path + "/Categories/" + self.notebook_type + "/" + filename + ".ipynb"

        # Check if file exists.
        if not os.path.exists(full_path) or self.notebook_type == "MainFiles":
            nb.write(self.notebook, full_path)
        else:
            raise RuntimeError("The specified filename already exists. The Notebook creation was interrupted !")

        # ========================== Run Notebook Code Instructions ================================
        os.system("jupyter nbconvert --execute --inplace --ExecutePreprocessor.timeout=-1 " +
                  full_path)
        os.system("jupyter trust " + full_path)

        # ==== Automatic generation of pages that group the Notebooks by different criteria ========
        if group_by is True:
            _generate_group_by_pages(path)

    def add_markdown_cell(self, content, tags=None):
        """
        -----
        Brief
        -----
        Class method responsible for adding a markdown cell with content 'content' to the
        Notebook object.

        -----------
        Description
        -----------
        Jupyter notebooks allow to use multiple format cells. One of those formats is the markdown cell, which allows
        to write informational content, write HTML and CSS code and structure the overall content of the notebook.

        This function allows to programmatically create a markdown cell with the content specified in the respective
        input.

        ----------
        Parameters
        ----------
        content : str
            Text/HTML code/... to include in the markdown cell (triple quote for multiline text).

        tags : list
            A list of tags to include in the markdown cell metadata.
        """
        self.notebook["cells"].append(nb.v4.new_markdown_cell(content, **{"metadata":
                                                                          {"tags": tags}}))

    def add_code_cell(self, content, tags=None):
        """
        -----
        Brief
        -----
        Class method responsible for adding a code cell with content 'content' to the
        Notebook object.

        -----------
        Description
        -----------
        Jupyter notebooks allow to use multiple format cells. One of those formats is the code cell, which allows
        to write Python code that can be ran in the notebooks.

        This function allows to programmatically create a code cell with the content specified in the respective
        input.

        ----------
        Parameters
        ----------
        content : str
            Code in a string format to include in the cell (triple quote for multiline
            text).

        tags : list
            A list of tags to include in the code cell metadata.
        """
        self.notebook["cells"].append(nb.v4.new_code_cell(content, **{"metadata":
                                                                      {"tags": tags}}))

# ==================================================================================================
# ========================== Generate OpenSignalTools File Hierarchy ===============================
# ==================================================================================================


def opensignals_hierarchy(root=None, update=False, clone=False):
    """
    -----
    Brief
    -----
    Function that generates the OpenSignalsTools Notebooks File Hierarchy programatically.

    -----------
    Description
    -----------
    OpenSignalsTools Notebooks folder obey to a predefined hierarchy that allows to run the code of online available
    notebooks and using the sample files, figures and CSS files in an easy way.

    This function generates the folder hierarchy programatically and automatically.

    ----------
    Parameters
    ----------
    root : None or str
        The file path where the OpenSignalsTools Environment will be stored.

    update : bool
        If True the old files will be replaced by the new ones.

    clone : bool
        If True then all the available Notebooks will be stored in the users computer.
        If False only the folder hierarchy of OpenSignalsTools will be generated, giving to the
        user a blank template for creating his own Notebook Environment.

    Returns
    -------
    out : str
        The root file path of OpenSignalsTools Environment is returned.
    """

    if root is None:
        root = os.getcwd()

    categories = list(NOTEBOOK_KEYS.keys())

    # ============================ Creation of the main directory ==================================
    current_dir = root + "/biosignalsnotebooks_environment"
    if not os.path.isdir(current_dir):
        os.makedirs(current_dir)

    # ================== Copy of 'images' 'styles' and 'signal_samples' folders ====================
    package_path = os.path.abspath(__file__).split(os.path.basename(__file__))[0].replace("\\", "/")
    for var in ["images", "styles", "signal_samples"]:
        if not os.path.isdir(root + "/biosignalsnotebooks_environment/" + var):
            src = (package_path + "notebook_files/osf_files/" + var).replace("\\", "/")
            destination = current_dir + "/" + var
            shutil.copytree(src, destination)
        elif update is True:
            shutil.rmtree(root + "/biosignalsnotebooks_environment/" + var)
            src = (package_path + "notebook_files/osf_files/" + var).replace("\\", "/")
            destination = current_dir + "/" + var
            shutil.copytree(src, destination)

    # =========================== Generation of 'Categories' folder ================================
    current_dir = root + "/biosignalsnotebooks_environment/Categories"
    if not os.path.isdir(current_dir):
        os.makedirs(current_dir)

    for category in categories:
        if not os.path.isdir(current_dir + "/" + category):
            os.makedirs(current_dir + "/" + category)
            if category == "MainFiles":
                # Copy aux folder.
                src = package_path + "notebook_files/osf_files/aux_folders/" + category + "/aux_files"
                shutil.copytree(src, current_dir + "/" + category + "/aux_files")

    # if clone is True:
    #     # Fill each folder inside "Categories" directory with the respective notebooks.
    #     # Each notebook will be created by a specific function.
    #     dir_path = root + "/notebook_code"
    #     list_of_code_dirs = os.listdir(dir_path)
    #     for folder in list_of_code_dirs:
    #         folder_path = root + "/notebook_code/" + folder
    #         if folder != "MainFiles" and folder != "__pycache__":
    #             list_of_code_files = os.listdir(folder_path)
    #             for file in list_of_code_files:
    #                 if file != "__pycache__":
    #                     spec = importlib.util.spec_from_file_location(file, folder_path +
    #                                                                   "/" + file)
    #                     foo = importlib.util.module_from_spec(spec)
    #                     spec.loader.exec_module(foo)
    #                     foo.run(root + "/biosignalsnotebooks_environment")
    #
    #     # Generation of biosignalsnotebooks environment main files.
    #     main_page = notebook("Main_Files_By_Category")
    #     main_page.write_to_file(root + "/biosignalsnotebooks_environment", "biosignalsnotebooks",
    #                             footer=False)
    #
    #     by_difficulty = notebook("Main_Files_By_Difficulty", "Notebooks Grouped by Difficulty", notebook_description=DESCRIPTION_GROUP_BY)
    #     by_difficulty.write_to_file(root + "/biosignalsnotebooks_environment", "by_diff",
    #                                 footer=False)
    #
    #     by_tags = notebook("Main_Files_By_Tag", "Notebooks Grouped by Tag Values",
    #                        notebook_description=DESCRIPTION_GROUP_BY)
    #     by_tags.write_to_file(root + "/biosignalsnotebooks_environment", "by_tag",
    #                           footer=False)
    #
    #     by_signal_type = notebook("Main_Files_By_Signal_Type", "Notebooks Grouped by Signal Type",
    #                               notebook_description=DESCRIPTION_GROUP_BY)
    #     by_signal_type.write_to_file(root + "/biosignalsnotebooks_environment",
    #                                  "by_signal_type", footer=False)
    #
    #     signal_samples = notebook("Main_Files_Signal_Samples", "Signal Samples Library",
    #                               notebook_description=DESCRIPTION_SIGNAL_SAMPLES)
    #     signal_samples.write_to_file(root + "/biosignalsnotebooks_environment",
    #                                  "signal_samples", footer=False)

    return root + "/biosignalsnotebooks_environment"

# ==================================================================================================
# ========================= Auxiliary Functions for Notebook Generation ============================
# ==================================================================================================


def _generate_notebook_header(notebook_object, notebook_type, notebook_title="Notebook Title",
                              tags="tags", difficulty_stars=1,
                              notebook_description="Notebook Description"):
    """
    Internal function that is used for generation of the generic notebooks header.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the header will be created.

    notebook_type : str
        Notebook type: - "Main_Files_Signal_Samples"
                       - "Main_Files_By_Category"
                       - "Main_Files_By_Difficulty"
                       - "Main_Files_By_Tag"
                       - "Acquire"
                       - "Open"
                       - "Visualise"
                       - "Process"
                       - "Detect"
                       - "Extract"
                       - "Train_And_Classify"
                       - "Explain"

    notebook_title : None or str
        The Notebook title should only be defined when 'notebook_type' is:
       - "Acquire"
       - "Open"
       - "Visualise"
       - "Process"
       - "Detect"
       - "Extract"
       - "Train_And_Classify"
       - "Explain"

    tags : str
        Sequence of tags that characterize the Notebook.

    difficulty_stars : int
        This input defines the difficulty level of the Notebook instructions.

    notebook_description : str
        An introductory text to present the Notebook and involve the reader.

    """

    # ============================= Creation of Header ====================================
    header_temp = HEADER_ALL_CATEGORIES.replace("header_image_color_i", "header_image_color_" +
                                                str(NOTEBOOK_KEYS[notebook_type]))
    header_temp = header_temp.replace("header_image_i", "header_image_" +
                                      str(NOTEBOOK_KEYS[notebook_type]))
    header_temp = header_temp.replace("Notebook Title", notebook_title)
    notebook_object["cells"].append(nb.v4.new_markdown_cell(header_temp, **{"metadata": {"tags": ["intro_info_title"]}}))

    # =============== Inclusion of the div with "Difficulty" and "Tags" ===================
    tags_and_diff = HEADER_TAGS.replace('<td class="shield_right" id="tags">tags</td>',
                                        '<td class="shield_right" id="tags">' + "&#9729;".join(tags)
                                        + '</td>')
    for star in range(1, 6):
        if star <= difficulty_stars:
            tags_and_diff = tags_and_diff.replace("fa fa-star " + str(star), "fa fa-star "
                                                                             "checked")
        else:
            tags_and_diff = tags_and_diff.replace("fa fa-star " + str(star), "fa fa-star")

    notebook_object["cells"].append(nb.v4.new_markdown_cell(tags_and_diff,
                                                            **{"metadata": {"tags": ["intro_info_tags"]}}))

    # ================= Insertion of the div reserved to the Notebook Description ==================
    notebook_object["cells"].append(nb.v4.new_markdown_cell(notebook_description,
                                                            **{"metadata":
                                                                {"tags": ["test"]}}))
    notebook_object["cells"].append(nb.v4.new_markdown_cell(SEPARATOR))

    # ======================= Insertion of a blank Markdown and Code cell ==========================
    notebook_object["cells"].append(nb.v4.new_markdown_cell(MD_EXAMPLES))
    notebook_object["cells"].append(nb.v4.new_code_cell(CODE_EXAMPLES))


def _generate_main_files_header(notebook_object, notebook_title="Notebook Title",
                                notebook_description="Notebook Description"):
    """
    Internal function that is used for generation of the 'MainFiles' notebooks header.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the header will be created.

    notebook_title : None or str
        Title of the Notebook.

    notebook_description : str
        An introductory text to present the Notebook and involve the reader.

    """

    # =================================== Creation of Header =======================================
    header_temp = HEADER_MAIN_FILES.replace("Notebook Title", notebook_title)
    notebook_object["cells"].append(nb.v4.new_markdown_cell(header_temp))

    # ================ Insertion of the div reserved to the Notebook Description ===================
    notebook_object["cells"].append(nb.v4.new_markdown_cell(notebook_description,
                                                            **{"metadata":
                                                               {"tags": ["test"]}}))
    # notebook_object["cells"].append(nb.v4.new_markdown_cell(SEPARATOR))


def _generate_footer(notebook_object, notebook_type):
    """
    Internal function that is used for generation of the notebooks footer.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the footer will be created.

    notebook_type : str
        Notebook type: - "Main_Files_Signal_Samples"
                       - "Main_Files_By_Category"
                       - "Main_Files_By_Difficulty"
                       - "Main_Files_By_Tag"
                       - "Acquire"
                       - "Open"
                       - "Visualise"
                       - "Process"
                       - "Detect"
                       - "Extract"
                       - "Train_And_Classify"
                       - "Explain"

    """

    footer_aux = FOOTER
    if "Main_Files" in notebook_type:
        footer_aux = footer_aux.replace("../MainFiles/", "")

    # ================ Insertion of the div reserved to the Notebook Description ===================
    notebook_object["cells"].append(nb.v4.new_markdown_cell(footer_aux,
                                                            **{"metadata":
                                                               {"tags": ["footer"]}}))


def _generate_header(notebook_object, notebook_type, notebook_file):
    """
    Internal function that is used for generation of the notebooks header.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the header will be created.

    notebook_file : str
        Notebook filename.

    notebook_type : str
        Notebook type: - "Main_Files_Signal_Samples"
                       - "Main_Files_By_Category"
                       - "Main_Files_By_Difficulty"
                       - "Main_Files_By_Tag"
                       - "Acquire"
                       - "Open"
                       - "Visualise"
                       - "Process"
                       - "Detect"
                       - "Extract"
                       - "Train_And_Classify"
                       - "Explain"
                       - "Other"
                       - "Install"
                       - "Connect"

    """

    header_aux = HEADER
    if notebook_file != None:
        header_aux = header_aux.replace("FILENAME", notebook_file.split(".")[0] + ".zip")
        header_aux = header_aux.replace("SOURCE", "https://mybinder.org/v2/gh/biosignalsplux/biosignalsnotebooks/mybinder_complete?filepath=biosignalsnotebooks_environment%2Fcategories%2F" + notebook_type + "%2F" + notebook_file + ".dwipynb")

    if "Main_Files" in notebook_type:
        header_aux = header_aux.replace("../MainFiles/", "")

    # ================ Insertion of the div reserved to the Notebook Description ===================
    notebook_object["cells"].append(nb.v4.new_markdown_cell(header_aux,
                                                            **{"metadata":
                                                               {"tags": ["header"]}}))


def _generate_signal_samples_body(notebook_object):
    """
    Internal function that is used for the generation of the table that enumerates all signal samples and respective
    descriptions.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the signal samples table is generated.

    """

    # =========================== Code Cell for Importing Packages =================================
    notebook_object["cells"].append(nb.v4.new_code_cell(IMPORT_CODE,
                                                        **{"metadata":
                                                            {"tags": ["hide_both"]}}))

    # ========= Generation of a table that synthesises the information about each signal ===========
    signal_samples_dir_jupyter = "../../signal_samples"
    signal_samples_dir_project = os.path.abspath(__file__).split(os.path.basename(__file__))[0].replace("\\", "/") + "notebook_files/osf_files/signal_samples"
    list_of_files = os.listdir(signal_samples_dir_project)
    for file in list_of_files:
        if ".json" not in file and ".h5" in file:
            file_name = file.split(".")[0]
            with open(signal_samples_dir_project + "/" + file_name + '_info.json') as json_data:
                signal_info = json.load(json_data)

            info_table = "<table width='100%'>\n" \
                         "\t<tr>\n" \
                         "\t\t<td colspan='2' class='signal_samples_header'>" + file_name + \
                         "</td>\n" + "</tr>\n"
            info_keys = list(signal_info.keys())
            for key in info_keys:
                info_table += "\t<tr>\n" \
                              "\t\t<td class='signal_samples_info_keys'>" + key + "</td>\n" + \
                              "\t\t<td class='signal_samples_info_values'>" + signal_info[key] + \
                              "</td>\n" + \
                              "\t</tr>\n"

            info_table += "</table>"

            # ============== Insertion of the HTML table inside a markdown cell ===================
            notebook_object["cells"].append(nb.v4.new_markdown_cell(info_table))

            # ========================= Graphical Representation of Signals =======================
            path_str = '"' + (signal_samples_dir_jupyter + "\\").replace("\\", "/") + '"'
            plot_signal_samples_temp = re.sub(re.compile(r'\bsignal_samples_dir\b'),
                                              path_str, PLOTS_SIGNAL_SAMPLES)
            plot_signal_samples_temp = re.sub(re.compile(r'\bfile\b'),
                                              '"' + str(file) + '"',
                                              plot_signal_samples_temp)
            notebook_object["cells"].append(nb.v4.new_code_cell(plot_signal_samples_temp,
                                                                **{"metadata":
                                                                    {"tags": ["hide_in"]}}))


def _generate_notebook_by_difficulty_body(notebook_object, dict_by_difficulty):
    """
    Internal function that is used for generation of the page where notebooks are organized by
    difficulty level.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the body will be created.

    dict_by_difficulty : dict
        Global Dictionary that groups Notebooks names/files by difficulty level.

    """

    difficulty_keys = list(dict_by_difficulty.keys())
    difficulty_keys.sort()
    for difficulty in difficulty_keys:
        markdown_cell = STAR_TABLE_HEADER
        markdown_cell = _set_star_value(markdown_cell, int(difficulty))
        for notebook_file in dict_by_difficulty[str(difficulty)]:
            split_path = notebook_file.replace("\\", "/").split("/")
            notebook_type = split_path[-2]
            notebook_name = split_path[-1].split("&&")[0]
            notebook_title = split_path[-1].split("&&")[1]
            markdown_cell += "\t<tr>\n\t\t<td width='20%' class='header_image_color_" + \
                             str(NOTEBOOK_KEYS[notebook_type]) + "'><img " \
                             "src='../../images/icons/" + notebook_type.title() +\
                             ".png' width='15%'>\n\t\t</td>"
            markdown_cell += "\n\t\t<td width='60%' class='center_cell open_cell_light'>" + \
                             notebook_title + "\n\t\t</td>"
            markdown_cell += "\n\t\t<td width='20%' class='center_cell'>\n\t\t\t<a href='" \
                             "../" + notebook_type.title() + "/" + notebook_name + \
                             "'><div class='file_icon'></div></a>\n\t\t</td>\n\t</tr>"

        markdown_cell += "</table>"

        # ==================== Insertion of HTML table in a new Notebook cell ======================
        notebook_object["cells"].append(nb.v4.new_markdown_cell(markdown_cell))


def _set_star_value(star_code, number_stars):
    """
    Internal function that is used for update the number of active stars (that define notebook
    difficulty level)

    ----------
    Parameters
    ----------
    star_code : str
        String with the HTML code to be changed.

    number_stars : int
        Number of stars that will be active.

    Returns
    -------
    out : str
        It is returned a string with the HTML code after updating the number of active stars.

    """

    for star in range(1, 6):
        if star <= number_stars:
            star_code = star_code.replace("fa fa-star " + str(star), "fa fa-star "
                                                                             "checked")
        else:
            star_code = star_code.replace("fa fa-star " + str(star), "fa fa-star")

    return star_code


def _generate_notebook_by_tag_body(notebook_object, dict_by_tag):
    """
    Internal function that is used for generation of the page where notebooks are organized by
    tag values.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the body will be created.

    dict_by_tag : dict
        Dictionary where each key is a tag and the respective value will be a list containing the
        Notebooks (title and filename) that include this tag.

    """

    tag_keys = list(dict_by_tag.keys())
    tag_keys.sort()
    for tag in tag_keys:
        if tag.lower() not in SIGNAL_TYPE_LIST:
            markdown_cell = TAG_TABLE_HEADER
            markdown_cell = markdown_cell.replace("Tag i", tag)
            for notebook_file in dict_by_tag[tag]:
                split_path = notebook_file.replace("\\", "/").split("/")
                notebook_type = split_path[-2]
                notebook_name = split_path[-1].split("&&")[0]
                notebook_title = split_path[-1].split("&&")[1]
                markdown_cell += "\t<tr>\n\t\t<td width='20%' class='header_image_color_" + \
                                 str(NOTEBOOK_KEYS[notebook_type]) + "'><img " \
                                 "src='../../images/icons/" + notebook_type.title() +\
                                 ".png' width='15%'>\n\t\t</td>"
                markdown_cell += "\n\t\t<td width='60%' class='center_cell open_cell_light'>" + \
                                 notebook_title + "\n\t\t</td>"
                markdown_cell += "\n\t\t<td width='20%' class='center_cell'>\n\t\t\t<a href='" \
                                 "../" + notebook_type.title() + "/" + notebook_name + \
                                 "'><div class='file_icon'></div></a>\n\t\t</td>\n\t</tr>"

            markdown_cell += "</table>"

            # ==================== Insertion of HTML table in a new Notebook cell ======================
            notebook_object["cells"].append(nb.v4.new_markdown_cell(markdown_cell))


def _generate_notebooks_by_category(notebook_object, dict_by_tag, new_notebooks=[]):
    """
    Internal function that is used for generation of the page "Notebooks by Category".

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the body will be created.

    dict_by_tag : dict
        Dictionary where each key is a tag and the respective value will be a list containing the
        Notebooks (title and filename) that include this tag.

    new_notebooks : list
        List containing the set of NEW notebooks where the "NEW" tag will be added.

    """

    # ============================ Insertion of an opening text ====================================
    markdown_cell = OPEN_IMAGE

    # == Generation of a table that group Notebooks by category the information about each signal ==
    category_list = list(NOTEBOOK_KEYS.keys())
    tag_keys = list(dict_by_tag.keys())

    markdown_cell += """\n<table id="notebook_list" width="100%">
    <tr>
        <td width="20%" class="center_cell group_by_header_grey"> Category </td>
        <td width="55%" class="center_cell group_by_header"></td>
        <td width="5%"></td>
        <td width="20%" class="center_cell"></td>
    </tr>"""

    for i, category in enumerate(category_list):
        if category != "MainFiles":
            if category.lower() in tag_keys:
                if i == 0:
                    first_border = "color1_top"
                else:
                    first_border = ""


                nbr_notebooks = len(dict_by_tag[category.lower()])
                markdown_cell += "\n\t<tr>" \
                                 "\n\t\t<td rowspan='" + str(nbr_notebooks + 1) + "' class='center_cell open_cell_border_" + str(NOTEBOOK_KEYS[category]) + "'><span style='float:center'><img src='../../images/icons/" + category + ".png' class='icon' style='vertical-align:middle' alt='biosignalsnotebooks | " + category + " icon'></span> <span style='float:center' class='color" + str(NOTEBOOK_KEYS[category]) + "'>" + category.replace("_", " ").replace("And", "and") + "</span></td>" \
                                 "\n\t\t<td colspan='2' class='center_cell color" + str(NOTEBOOK_KEYS[category]) + "_cell " + first_border + "'><span style='float:center'>" + category.replace("_", " ").replace("And", "and") + "</span></td>" \
                                 "\n\t\t<td class='center_cell gradient_color" + str(NOTEBOOK_KEYS[category]) + "'></td>" \
                                 "\n\t</tr>"

                notebook_list = dict_by_tag[category.lower()]
                for j, notebook_file in enumerate(notebook_list):
                    if j == len(notebook_list) - 1:
                        last_border = "class='border_cell_bottom_white'"
                    else:
                        last_border = ""

                    split_path = notebook_file.replace("\\", "/").split("/")
                    notebook_name = split_path[-1].split("&&")[0]
                    notebook_title = split_path[-1].split("&&")[1]
                    markdown_cell += "\n\t<tr " + last_border + ">" \
                                     "\n\t\t<td class='center_cell open_cell_light' style='padding-left:5%'> <a href='../" + category + "/" + notebook_name + "'>" + notebook_title + "</a> </td>"
                    if notebook_name.split(".")[0] in new_notebooks:
                        markdown_cell += "\n\t\t<td class='center_cell back_color_" + str(NOTEBOOK_KEYS[category]) + "'>NEW</td>"
                    else:
                        markdown_cell += "\n\t\t<td class='center_cell open_cell_light'></td>"
                    markdown_cell += "\n\t\t<td class='center_cell open_cell_light'> <a href='../" + category + "/" + notebook_name + "'><div class='file_icon'></div></a> </td>" \
                                     "\n\t</tr>"

    markdown_cell += "\n</table>"

    # ============================ Insertion of an introductory text ===============================
    markdown_cell += DESCRIPTION_CATEGORY

    # =================== Insertion of the HTML table inside a markdown cell =======================
    notebook_object["cells"].append(nb.v4.new_markdown_cell(markdown_cell))


def _generate_github_readme(notebook_object, dict_by_tag):
    """
    Internal function that is used for generation of the GitHub and PyPI README file.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the body will be created.

    dict_by_tag : dict
        Dictionary where each key is a tag and the respective value will be a list containing the
        Notebooks (title and filename) that include this tag.

    """

    # ==================== List of urls that contain each Category icon ============================
    icons = {"Detect": "https://i.ibb.co/rymrvFL/Detect.png",
             "Evaluate": "https://i.ibb.co/yfwcy2M/Evaluate.png",
             "Extract": "https://i.ibb.co/tchq7Cc/Extract.png",
             "Load": "https://i.ibb.co/YPbCnzD/Load.png",
             "Pre-Process": "https://i.ibb.co/1rKWccX/Pre-Process.png",
             "Record": "https://i.ibb.co/d2jZH1s/Record.png",
             "Train_And_Classify": "https://i.ibb.co/CQ4cyGb/Train-and-Classify.png",
             "Understand": "https://i.ibb.co/MnhRRQT/Understand.png",
             "Visualise": "https://i.ibb.co/wh4HKzf/Visualise.png",
             "Other": "https://i.ibb.co/ry9BzhV/Other.png",
             "Install": "https://i.ibb.co/LgrhTz9/Install.png",
             "Connect": "https://i.ibb.co/8cNpQFM/Connect.png"}

    # =========================== biosignalsnotebooks website ======================================
    biosignalsnotebooks_web = "http://www.biosignalsplux.com/notebooks/Categories/"

    # == Generation of a table that group Notebooks by category the information about each signal ==
    category_list = list(NOTEBOOK_KEYS.keys())
    tag_keys = list(dict_by_tag.keys())

    markdown_cell = """<table width="100%">
    <tr>
        <td width="20%" align="center"><strong> Category <strong></td>
        <td width="80%"></td>
    </tr>"""

    for i, category in enumerate(category_list):
        if category != "MainFiles":
            if category.lower() in tag_keys:
                nbr_notebooks = len(dict_by_tag[category.lower()])
                notebook_list = dict_by_tag[category.lower()]
                split_path = notebook_list[0].replace("\\", "/").split("/")
                notebook_name = split_path[-1].split("&&")[0]
                notebook_title = split_path[-1].split("&&")[1]
                markdown_cell += "\n\t<tr>" \
                                 "\n\t\t<td rowspan='" + str(nbr_notebooks) + "'><p align='center'><img src='" + icons[category] + "' width='50%' align='center'></p></td>" \
                                 "\n\t\t<td align='center'> <a href='" + biosignalsnotebooks_web + category + "/" + notebook_name.replace(".ipynb", "_rev.php") + "' target='_blank'>" + notebook_title + "</a> </td>" \
                                 "\n\t</tr>"

                for j, notebook_file in enumerate(notebook_list[1:]):
                    split_path = notebook_file.replace("\\", "/").split("/")
                    notebook_name = split_path[-1].split("&&")[0]
                    notebook_title = split_path[-1].split("&&")[1]
                    markdown_cell += "\n\t<tr>" \
                                     "\n\t\t<td align='center'> <a href='" + biosignalsnotebooks_web + category + "/" + notebook_name.replace(".ipynb", "_rev.php") + "'>" + notebook_title + "</a> </td>" \
                                     "\n\t</tr>"

    markdown_cell += "\n</table>"

    # ============================ Generation of README files ======================================
    # [Open template]
    template_path = os.path.abspath(__file__).split(os.path.basename(__file__))[0].replace("\\", "/") + "/notebook_files/github/README_TEMPLATE.md"
    with open(template_path, 'r') as readme:
        readme_str = readme.read()

    readme_str = readme_str.replace("LIST_OF_NOTEBOOKS", markdown_cell)

    # [Storage of the updated files]
    for path in ["../biosignalsnotebooks/README_BSN.md", "../README.md"]:
        with open(path, 'w') as readme_out:
            readme_out.write(readme_str)
        readme_out.close()


def _generate_notebook_by_signal_type_body(notebook_object, dict_by_tag):
    """
    Internal function that is used for generation of the page where notebooks are organized by
    signal type where they are applicable.

    ----------
    Parameters
    ----------
    notebook_object : notebook object
        Object of "notebook" class where the body will be created.

    dict_by_tag : dict
        Dictionary where each key is a tag and the respective value will be a list containing the
        Notebooks (title and filename) that include this tag.
    """

    tag_keys = list(dict_by_tag.keys())
    tag_keys.sort()
    for tag in tag_keys:
        if tag.lower() in SIGNAL_TYPE_LIST:
            markdown_cell = TAG_TABLE_HEADER
            markdown_cell = markdown_cell.replace("Tag i", tag.upper())
            for notebook_file in dict_by_tag[tag]:
                split_path = notebook_file.replace("\\", "/").split("/")
                notebook_type = split_path[-2]
                notebook_name = split_path[-1].split("&&")[0]
                notebook_title = split_path[-1].split("&&")[1]
                markdown_cell += "\t<tr>\n\t\t<td width='20%' class='header_image_color_" + \
                                 str(NOTEBOOK_KEYS[notebook_type]) + "'><img " \
                                                                     "src='../../images/icons/" + notebook_type.title() + \
                                 ".png' width='15%'>\n\t\t</td>"
                markdown_cell += "\n\t\t<td width='60%' class='center_cell open_cell_light'>" + \
                                 notebook_title + "\n\t\t</td>"
                markdown_cell += "\n\t\t<td width='20%' class='center_cell'>\n\t\t\t<a href='" \
                                 "../" + notebook_type.title() + "/" + notebook_name + \
                                 "'><div class='file_icon'></div></a>\n\t\t</td>\n\t</tr>"

            markdown_cell += "</table>"

            # ==================== Insertion of HTML table in a new Notebook cell ======================
            notebook_object["cells"].append(nb.v4.new_markdown_cell(markdown_cell))

def _generate_group_by_pages(root):
    dict_group_by_diff, dict_group_by_tag = _search_in_notebooks(root)
    file_path = root

    # Generation of biosignalsnotebooks environment main files.
    filename = "biosignalsnotebooks"
    main_page = notebook("Main_Files_By_Category", dict_by_difficulty=dict_group_by_diff,
                         dict_by_tag=dict_group_by_tag, notebook_file=filename)
    main_page.write_to_file(file_path, filename)
    filename = "by_diff"
    by_difficulty = notebook("Main_Files_By_Difficulty", "Notebooks Grouped by Difficulty",
                             dict_by_difficulty=dict_group_by_diff,
                             dict_by_tag=dict_group_by_tag,
                             notebook_file=filename)
    by_difficulty.write_to_file(file_path, filename)

    filename = "by_tag"
    by_tags = notebook("Main_Files_By_Tag", "Notebooks Grouped by Tag Values",
                       dict_by_difficulty=dict_group_by_diff, dict_by_tag=dict_group_by_tag,
                       notebook_file=filename)
    by_tags.write_to_file(file_path, filename)

    filename = "by_signal_type"
    by_signal_type = notebook("Main_Files_By_Signal_Type",
                              "Notebooks Grouped by Signal Type",
                              dict_by_difficulty=dict_group_by_diff,
                              dict_by_tag=dict_group_by_tag,
                              notebook_file=filename)
    by_signal_type.write_to_file(file_path, filename)

    filename = "signal_samples"
    signal_samples = notebook("Main_Files_Signal_Samples", "Signal Samples Library",
                              notebook_file=filename)
    signal_samples.write_to_file(file_path, filename)

def _search_in_notebooks(root):
    # Variable definition.
    dict_group_by_diff = {}
    dict_group_by_tag = {}

    categories = os.listdir(root + "/Categories")
    for category in categories:
        current_folder_path = root + "/Categories/" + category
        list_files = os.listdir(current_folder_path)
        for file in list_files:
            current_file_path = current_folder_path + "/" + file
            # Access to all Notebook files (with the extension .ipynb)
            if file.endswith(".ipynb"):
                # Read of the current Notebook.
                notebook = nb.read(current_file_path, nb.NO_CONVERT)

                # Search for "header" and/or "footer".
                header_cell, footer_cell, title, nbr_stars, tags = _get_metadata(notebook, file,
                                                                                 category)

                # Storage of Notebook metadata in global dictionaries.
                if category != "MainFiles":
                    if str(nbr_stars) not in (dict_group_by_diff.keys()):
                        dict_group_by_diff[str(nbr_stars)] = []
                    dict_group_by_diff[str(nbr_stars)].append(current_file_path + "&&" + title)

                    for tag in tags:
                        if tag not in (dict_group_by_tag.keys()):
                            dict_group_by_tag[str(tag)] = []
                        dict_group_by_tag[str(tag)].append(current_file_path + "&&" + title)

    print(dict_group_by_diff)
    print(dict_group_by_tag)
    return dict_group_by_diff, dict_group_by_tag


def _get_metadata(notebook, filename, category):
    # Variable initialisation.
    header_cell = None
    footer_cell = None
    title = None
    nbr_stars = None
    tags = None
    list_cells = notebook["cells"]

    # Search for "header" and "footer" tags and collect Notebook "difficulty" and "tags".
    for cell_nbr, cell in enumerate(list_cells):
        if "tags" in list(cell["metadata"].keys()):
            # [Header and Footer identification]
            if "header" in cell["metadata"]["tags"] and header_cell is None:
                header_cell = cell_nbr
            elif "footer" in cell["metadata"]["tags"] and footer_cell is None:
                footer_cell = cell_nbr
            elif "aux" in cell["metadata"]["tags"] and footer_cell is None:
                footer_cell = cell_nbr
            elif ("header" in cell["metadata"]["tags"] and header_cell is not None) or \
                    ("footer" in cell["metadata"]["tags"] and footer_cell is not None):
                raise RuntimeError("Duplicated 'header' or 'cell' tags inside the Notebook " +
                               filename + " !")

            # [Title, Difficulty and Tags]
            if category != "MainFiles":
                # [Title]
                if "intro_info_title" in cell["metadata"]["tags"]:
                    cell_content = cell["source"]

                    # Notebook Title.
                    title = cell_content.split('<td class="header_text">')[1].split('</td>')[0]

                # [Tags]
                if "intro_info_tags" in cell["metadata"]["tags"]:
                    cell_content = cell["source"]

                    # Notebook tag list.
                    tags = cell_content.split('<td class="shield_right" id="tags">')[1].split('</td>')[0].split("&#9729;")

                    # Difficulty level.
                    nbr_stars = cell_content.count("checked")

    return header_cell, footer_cell, title, nbr_stars, tags

# 29/11/2018  17h18m :)
