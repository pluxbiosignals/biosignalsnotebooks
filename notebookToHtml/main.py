
# ======================================================================================================================
# ========================================= Imported Packages ==========================================================
# ======================================================================================================================

import bs4 as htmlLib
import os
from shutil import copyfile
import subprocess
import pylab as plt
import time
import shutil

# ======================================================================================================================
# ===================================== Access to each notebook file ===================================================
# ======================================================================================================================
cssFile = open("../biosignalsnotebooks/biosignalsnotebooks_notebooks/styles/theme_style.css", "r")
cssText = cssFile.read().replace("<style>", "")
filePath = "../biosignalsnotebooks/header_footer/biosignalsnotebooks_environment/Categories"
projectAbsPath = os.getcwd()
# print(os.path.dirname(os.path.abspath(__file__)))
listOfNbCategories = os.listdir(filePath)

# --------------------------------------------------------------------------------------------------
# ----- Creation of folder hierarchy where the HTML version of opensignalstools will be stored -----
# --------------------------------------------------------------------------------------------------
ost_dir = projectAbsPath + "\\biosignalsnotebooks_html"
if not os.path.exists(ost_dir):
    os.makedirs(ost_dir)

path_temp = ost_dir + "\\Categories"
if not os.path.exists(path_temp):
    os.makedirs(path_temp)

# Copy of css file and images folder.
path_temp = "../biosignalsnotebooks/biosignalsnotebooks_notebooks/"
for var in ["images", "styles"]:
    if not os.path.isdir(ost_dir + "\\" + var):
        src = path_temp + var
        destination = ost_dir + "\\" + var
        shutil.copytree(src, destination)
    else:
        shutil.rmtree(ost_dir + "\\" + var)
        src = path_temp + var
        destination = ost_dir + "\\" + var
        shutil.copytree(src, destination)

# Generation of HTML version of each Notebook.
for category in listOfNbCategories:
    # Creation of directory when it don't exist.
    path_temp = ost_dir + "\\Categories\\" + category
    if not os.path.exists(path_temp):
        os.makedirs(path_temp)

    print ("\nEntering in " + category + " category...")
    if "." not in category: # If "." is contained in the string it means that we are not analysing a desired folder.
        print ("'mytemplate.tpl' copy started...")
        # Update nbconvert.tpl template file.
        copyfile("mytemplate.tpl", filePath + "/" + category + "/template.tpl")
        time.sleep(2)

        print("'CustomPreprocessor.py' copy started...")
        # Update nbconvert.tpl template file.
        copyfile("CustomPreprocessor.py", filePath + "/" + category + "/CustomPreprocessor.py")
        time.sleep(2)

        # Access to the folder content.
        nbList = os.listdir(filePath + "/" + category)
        for notebook in nbList:
            os.chdir(projectAbsPath)
            if notebook.endswith(".ipynb") and "Template" not in notebook: # Only .ipynb files will be processed.
                # Copy of .ipynb file to the output file hierarchy.
                copyfile(filePath + "/" + category + "/" + notebook,
                         path_temp + "\\" + notebook)

                # Generation of HTML file.
                print("\nThe conversion of " + notebook + " started...")
                os.chdir(filePath + "/" + category)
                #os.popen("jupyter nbconvert --to html " + notebook + "  --template=template.tpl")
                print (path_temp)
                os.popen("jupyter nbconvert --output-dir='" + path_temp.replace("\\", "/") + "' --config='" + projectAbsPath.replace("\\", "/") + "/nbconvert_config.py' --to html " + notebook + " --template=template.tpl")
                time.sleep(10)

                # Read of the generated html file.
                print("Creating HTML object...")
                htmlFile = open(path_temp + "\\" + notebook.split(".")[0] + ".html", "r")
                htmlObject = htmlLib.BeautifulSoup(htmlFile, "html.parser")

                # Hide all tagged inputs.
                print("Hiding unwanted cells...")
                cellIn = htmlObject.find_all("div", attrs={"class": "hide_in"})
                for cell in cellIn:
                    # Add class "hide" to the current div.
                    inputContainer = cell.find_next(attrs={"class": "input"})
                    inputContainer["class"] = inputContainer.get('class', []) + ['hide']

                # Hide all tagged outputs.
                cellOut = htmlObject.find_all("div", attrs={"class": "hide_out"})
                for cell in cellOut:
                    # Add class "hide" to the current div.
                    outputContainer = cell.find_next(attrs={"class": "output"})
                    outputContainer["class"] = outputContainer.get('class', []) + ['hide']

                # Hide all tagged containers.
                cellBoth = htmlObject.find_all("div", attrs={"class": "hide_both"})
                for cell in cellBoth:
                    # Add class "hide" to the input div.
                    bothContainer = cell.find_next(attrs={"class": "input"})
                    bothContainer["class"] = bothContainer.get('class', []) + ['hide']

                    # Add class "hide" to the output div.
                    bothContainer = cell.find_next(attrs={"class": "output"})
                    if bothContainer != None:
                        bothContainer["class"] = bothContainer.get('class', []) + ['hide']

                # Hide all tagged markdown cells.
                cellMark = htmlObject.find_all("div", attrs={"class": "hide_mark"})
                for cell in cellMark:
                    # Add class "hide" to the current div.
                    cell["class"] = cell.get('class', []) + ['hide']

                # Import css style.
                print("Importing CSS style...")
                styleContainer = htmlObject.find_all(attrs={"id": "style_import"})
                if len(styleContainer) != 0:
                    tag = htmlObject.new_tag("style")
                    tag.string = cssText
                    styleContainer[0].insert_before(tag)

                # headerContainer = htmlObject.find_all(attrs={"id": "image_td"})
                # if len(headerContainer) != 0:
                #     headerContainer[0]["height"] = "50px"
                #
                # headerContainer = htmlObject.find_all(attrs={"id": "image_img"})
                # if len(headerContainer) != 0:
                #     headerContainer[0]["height"] = "50px"


                # Generate the new html file with the applied corrections.
                #print (htmlObject.original_encoding)
                print("Storage of the final HTML version...")
                html = htmlObject.prettify("utf-8")
                with open(path_temp + "\\" + notebook.split(".")[0] + "_rev" + ".html", "wb") as file:
                    file.write(html)
                time.sleep(5)

                # Delete original Notebook HTML file.
                htmlFile.close()
                os.remove(path_temp + "\\" + notebook.split(".")[0] + ".html")

                #     print (inputContainer["class"])
                # print (htmlObject.find_all("div", attrs={"class": "hide_in"})[0].find_next(attrs={"class": "input"}))

# # Repetir o procedimento seguinte para cada ficheiro .ipynb contido na pasta "Categories" varrendo as subpastas.
# htmlFile = open("../Notebooks/Categories/Template.html", "r")
# htmlObject = htmlLib.BeautifulSoup(htmlFile, "html.parser")
#
# print (htmlObject.prettify().split("\n"))


# ======================================================================================================================
# ===================================== Execution of cmd command =======================================================
# ======================================================================================================================


# 17/10/2018 22h24m