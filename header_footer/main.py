"""
biosignalsnotebooks module intended to generate programatically the header and footer of each
Jupyter Notebook.

"""

import os
import shutil
import nbformat
import json

from biosignalsnotebooks.notebook_files.cell_content_strings import HEADER, FOOTER, \
    DESCRIPTION_SIGNAL_SAMPLES, DESCRIPTION_GROUP_BY
from biosignalsnotebooks.factory import notebook, NOTEBOOK_KEYS

# ==================================================================================================
# =================================== Script Constants =============================================
# ==================================================================================================

DICT_GROUP_BY_DIFF = {}

DICT_GROUP_BY_TAG = {}

# ==================================================================================================
# ===================== Inclusion of Header and Footer in each Notebook ============================
# ==================================================================================================

def run(list_notebooks=["All"], exclude_notebooks=["None"], signal_samples_flag=True, delete_old_files=False, new_notebooks_list=[]):
    # Storage of the current directory path.
    root = os.getcwd()

    # ============================= Creation of the main directory =================================
    current_dir = root + "\\biosignalsnotebooks_environment"
    if not os.path.isdir(current_dir):
        os.makedirs(current_dir)

    # ============================= Copy of  =================================

    # ==================== Copy of 'images' 'styles' and 'signal_samples' folders ==================
    for var in ["images", "styles", "signal_samples", "categories"]:
        new_dir = current_dir + "\\" + var

        # Delete of old files if the directory was previously created.
        if delete_old_files is True:
            if os.path.isdir(new_dir):
                shutil.rmtree(new_dir)

            # Definition of the "source" folder to copy.
            src = "..\\biosignalsnotebooks_notebooks\\" + var

            # Definition of the "destination" folder where the files will be stored after copying.
            destination = new_dir

            # Clone directory.
            shutil.copytree(src, destination)

    # ======================== Copy of the original versions of Notebooks ==========================
    current_dir = os.getcwd() + "\\biosignalsnotebooks_environment\\categories"
    for category in list(NOTEBOOK_KEYS.keys()):
        src = "..\\biosignalsnotebooks_notebooks\\categories\\" + category
        list_files = os.listdir(src)
        for file in list_files:
            # Access to all Notebook files (with the extension .ipynb)
            if file.endswith(".ipynb") and (file.split(".ipynb")[0] not in exclude_notebooks or "None" in exclude_notebooks):
                # Copy file if it is not already in the destination folder.
                shutil.copyfile(src + "\\" + file, current_dir + "\\" + category + "\\" + file)

                # Read of the current Notebook.
                file_dir = current_dir + "\\" + category + "\\" + file
                notebook = nbformat.read(file_dir, nbformat.NO_CONVERT)

                # Search for "header" and/or "footer".
                header_cell, footer_cell, title, nbr_stars, tags = _get_metadata(notebook, file,
                                                                                 category)

                if file.split(".ipynb")[0] in list_notebooks or "All" in list_notebooks:
                    # Update or Insertion of header and footer.
                    # [Header]
                    header_rev = HEADER.replace("FILENAME", file.split(".")[0] + ".zip")
                    header_rev = header_rev.replace("SOURCE", "https://mybinder.org/v2/gh/biosignalsplux/biosignalsnotebooks/mybinder_complete?filepath=biosignalsnotebooks_environment%2Fcategories%2F" + category + "%2F" + file.split(".")[0] + ".dwipynb")

                    if header_cell is None:
                        notebook["cells"].insert(0, nbformat.v4.new_markdown_cell(header_rev, **{"metadata": {"tags": ["header"]}}))
                        if footer_cell is not None:
                            footer_cell += 1
                    else:
                        notebook["cells"][header_cell] = nbformat.v4.new_markdown_cell(header_rev, **{"metadata": {"tags": ["header"]}})

                    # [Footer]
                    if footer_cell is None:
                        notebook["cells"].append(nbformat.v4.new_markdown_cell(FOOTER, **{"metadata": {"tags": ["footer"]}}))
                    else:
                        notebook["cells"][footer_cell] = nbformat.v4.new_markdown_cell(FOOTER, **{"metadata": {"tags": ["footer"]}})

                    # Generation of the Notebook with the header and footer.
                    nbformat.write(notebook, file_dir)

                    # Run Notebook.
                    os.system("jupyter nbconvert --execute --inplace --ExecutePreprocessor.timeout=-1 "
                              + file_dir)
                    os.system("jupyter trust " + file_dir)

                # Storage of Notebook metadata in global dictionaries.
                if category != "MainFiles":
                    if str(nbr_stars) not in (DICT_GROUP_BY_DIFF.keys()):
                        DICT_GROUP_BY_DIFF[str(nbr_stars)] = []

                    DICT_GROUP_BY_DIFF[str(nbr_stars)].append(file_dir + "&" + title)

                    for tag in tags:
                        if tag not in (DICT_GROUP_BY_TAG.keys()):
                            DICT_GROUP_BY_TAG[str(tag)] = []
                        DICT_GROUP_BY_TAG[str(tag)].append(file_dir + "&" + title)

    # ==============================================================================================
    # ============================ Generate "Group by ..." Pages ===================================
    # ==============================================================================================
    _generate_group_by_pages(signal_samples=signal_samples_flag, new_notebooks_list=new_notebooks_list)

    # ==============================================================================================
    # ======================== Generate a Post-Build File for Binder ===============================
    # ==============================================================================================
    _generate_post_build_files()

    # ==============================================================================================
    # ========= Store the list of updated Notebooks (for the HTML generation script) ===============
    # ==============================================================================================
    with open(os.getcwd() + "\\biosignalsnotebooks_environment\\last_updated_nbs.json", 'w') as outfile:
        json.dump({"updated_notebooks": list_notebooks}, outfile)

# ==================================================================================================
# ================================== Private Functions =============================================
# ==================================================================================================

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


def _generate_group_by_pages(signal_samples=True, new_notebooks_list=[]):
    file_path = os.getcwd() + "\\biosignalsnotebooks_environment"

    # Generation of biosignalsnotebooks environment main files.
    filename = "biosignalsnotebooks"
    main_page = notebook("Main_Files_By_Category", dict_by_difficulty=DICT_GROUP_BY_DIFF,
                         dict_by_tag=DICT_GROUP_BY_TAG, notebook_file=filename, new_notebooks=new_notebooks_list)
    main_page.write_to_file(file_path, filename)

    filename = "by_diff"
    by_difficulty = notebook("Main_Files_By_Difficulty", "Notebooks Grouped by Difficulty",
                             dict_by_difficulty=DICT_GROUP_BY_DIFF, dict_by_tag=DICT_GROUP_BY_TAG,
                             notebook_file=filename)
    by_difficulty.write_to_file(file_path, filename)

    filename = "by_tag"
    by_tags = notebook("Main_Files_By_Tag", "Notebooks Grouped by Tag Values",
                       dict_by_difficulty=DICT_GROUP_BY_DIFF, dict_by_tag=DICT_GROUP_BY_TAG,
                       notebook_file=filename)
    by_tags.write_to_file(file_path, filename)

    filename = "by_signal_type"
    by_signal_type = notebook("Main_Files_By_Signal_Type", "Notebooks Grouped by Signal Type",
                              dict_by_difficulty=DICT_GROUP_BY_DIFF, dict_by_tag=DICT_GROUP_BY_TAG,
                              notebook_file=filename)
    by_signal_type.write_to_file(file_path, filename)

    if signal_samples is True:
        filename = "signal_samples"
        signal_samples = notebook("Main_Files_Signal_Samples", "Signal Samples Library",
                                  notebook_file=filename)
        signal_samples.write_to_file(file_path, filename)

def _generate_post_build_files():
    # Constant Values
    relative_path_for_binder = "biosignalsnotebooks_environment/categories/"
    source_path = "biosignalsnotebooks_environment/categories/"

    # Dynamic string
    post_build_str = "jupyter contrib nbextension install --user\n"

    # Inclusion of data inside the dynamic string.
    categories = os.listdir(source_path)
    for category in categories:
        if category != ".ipynb_checkpoints":
            current_file_path = source_path + category + "/"
            list_files = os.listdir(current_file_path)
            for file in list_files:
                if ".ipynb" in file and ".ipynb_checkpoints" not in file:
                    post_build_str += "jupyter nbconvert --execute --inplace --ExecutePreprocessor.timeout=-1 " + relative_path_for_binder + category + "/" + file + "\n"
                    post_build_str += "jupyter trust " + relative_path_for_binder + category + "/" + file + "\n"

    # Write to file.
    post_build_file = open("../postBuild", "w")
    post_build_file.write(post_build_str)
    post_build_file.close()

# Execute Script.
#run(list_notebooks=["eeg_extract_alphaband"])
run(list_notebooks=["tachogram"], exclude_notebooks=["hands_on_biostec", "hands_on_biostec_solutions", "quick_start_guide"],
    signal_samples_flag=False, delete_old_files=False, new_notebooks_list=["unit_conversion_RIP", "poincare_plot", "tachogram"])
#run(exclude_notebooks=["hands_on_biostec", "hands_on_biostec_solutions"], signal_samples_flag=False)

# 29/11/2018  17h18m :)
