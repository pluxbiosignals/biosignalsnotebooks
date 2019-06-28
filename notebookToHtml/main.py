
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
import zipfile

def run(apply_to_biosignalsplux_website=False):
    # ======================================================================================================================
    # ===================================== Access to each notebook file ===================================================
    # ======================================================================================================================
    filePath = "../header_footer/biosignalsnotebooks_environment/Categories"
    projectAbsPath = os.getcwd()
    # print(os.path.dirname(os.path.abspath(__file__)))
    listOfNbCategories = os.listdir(filePath)

    # --------------------------------------------------------------------------------------------------
    # ----- Creation of folder hierarchy where the HTML version of opensignalstools will be stored -----
    # --------------------------------------------------------------------------------------------------
    if apply_to_biosignalsplux_website is False:
        ost_dir = projectAbsPath + "\\biosignalsnotebooks_html"
    else:
        ost_dir = projectAbsPath + "\\biosignalsnotebooks_html_publish"

    if not os.path.exists(ost_dir):
        os.makedirs(ost_dir)

    path_temp = ost_dir + "\\Categories"
    if not os.path.exists(path_temp):
        os.makedirs(path_temp)

    # Copy of css file and images folder.
    path_temp = "../biosignalsnotebooks_notebooks/"
    for var in ["images", "styles", "signal_samples"]:
        if not os.path.isdir(ost_dir + "\\" + var):
            src = path_temp + var
            destination = ost_dir + "\\" + var
            shutil.copytree(src, destination)
        else:
            shutil.rmtree(ost_dir + "\\" + var)
            src = path_temp + var
            destination = ost_dir + "\\" + var
            shutil.copytree(src, destination)

        if var == "styles" and apply_to_biosignalsplux_website is True:
            # # Read CSS file and adapt relative paths.
            # with open(destination + "\\theme_style.css", "r") as css_in:
            #     with open(destination + "\\theme_style_rev.css", "w") as css_out:
            #         for line in css_in:
            #             css_out.write(line.replace('../../', ''))
            # css_in.close()
            # css_out.close()
            #
            # # Rename Files.
            # os.rename(destination + "\\theme_style.css", destination + "\\theme_style_old.css")
            # os.rename(destination + "\\theme_style_rev.css", destination + "\\theme_style.css")

            # Remove <style> markup.
            cssFile = open(destination + "\\theme_style.css", "r")
            cssText = cssFile.read().replace("<style>", "")
            cssFile.close()

    # Generation of HTML version of each Notebook.
    for category in listOfNbCategories:
        # Creation of directory when it don't exist.
        path_temp = ost_dir + "\\Categories\\" + category
        if not os.path.exists(path_temp):
            os.makedirs(path_temp)

        # Copy of aux_files folder.
        if category == "MainFiles":
            source_path = "../biosignalsnotebooks_notebooks/Categories/MainFiles/aux_files"
            destination_path = path_temp + "\\aux_files"
            if not os.path.isdir(destination_path):
                shutil.copytree(source_path, destination_path)
            else:
                shutil.rmtree(destination_path)
                shutil.copytree(source_path, destination_path)

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

            # Inclusion of a specialized "CustomPreprocessor.py" file, used during .ipynb to .html
            # conversion of main page.
            if category == "MainFiles" and apply_to_biosignalsplux_website is True:
                copyfile("CustomPreprocessorIndex.py", filePath + "/" + category + "/CustomPreprocessorIndex.py")
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
                    if apply_to_biosignalsplux_website is False:
                        os.popen("jupyter nbconvert --output-dir='" + path_temp.replace("\\", "/") + "' --config='" + projectAbsPath.replace("\\", "/") + "/nbconvert_config.py' --to html " + notebook + " --template=template.tpl")
                    else:
                        os.popen("jupyter nbconvert --output-dir='" + path_temp.replace("\\", "/") + "' --config='" + projectAbsPath.replace("\\", "/") + "/nbconvert_config_index.py' --to html " + notebook + " --template=template.tpl")

                        # Generation of an index.php file (Ensuring detection by the crawlers).
                        php_path = path_temp + "/" + notebook.split(".")[0] + "_rev.php"
                        copyfile((projectAbsPath + "/index.php").replace("\\", "/"), php_path)

                        # Adjustment of index.php content in order to include the path to the
                        # current Notebook.
                        with open(php_path, "r") as php_in:
                            with open(path_temp + notebook.split(".")[0] + "_temp.php", "w") as php_out:
                                for line in php_in:
                                    php_out.write(line.replace('RELATIVE_PATH', notebook.split(".")[0] +
                                                               "_rev.html").replace('Notebbok Title Here',
                                                                                    "Notebook - " +
                                                                                    notebook.split(".")[0].replace("_", " ")))
                        php_in.close()
                        php_out.close()

                        # Delete original file and rename the new one.
                        os.remove(php_path)
                        os.rename(path_temp + notebook.split(".")[0] + "_temp.php", php_path)

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

                    # Tracking script.
                    #scriptSoup = htmlLib.BeautifulSoup("<!-- Global site tag (gtag.js) - Google Analytics --><script async src='https://www.googletagmanager.com/gtag/js?id=UA-38036509-2'></script><script>window.dataLayer = window.dataLayer || [];function gtag(){dataLayer.push(arguments);}gtag('js', new Date());gtag('config', 'UA-38036509-2');</script>",
                    #                                   "html.parser")
                    #headContainer = htmlObject.find_all("head")
                    #headContainer[0].append(scriptSoup)

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

                    # Generation of a zip archive intended to create a downloadable version of each Notebook
                    # with all the styles and minimal size.
                    zipf = zipfile.ZipFile(path_temp + "\\" + notebook.split(".")[0] + ".zip", 'w',
                                           zipfile.ZIP_DEFLATED)

                    # Populating the .zip file with the images and styles folders.
                    print("Creating a zip file with the Notebook and style elements")
                    os.chdir(projectAbsPath)
                    for folder in ["images", "styles"]:
                        # Images and styles folders.
                        # Adapt filepath to the type of folder under analysis.
                        if folder is "images":
                            path_for_zip = ost_dir + "\\" + folder + "\\" + category + "\\" + notebook.split(".")[0]

                            # Icons folder.
                            for root, dirs, files in os.walk(ost_dir + "\\" + folder + "\\icons"):
                                for file in files:
                                    zipf.write(os.path.relpath(os.path.join(root, file), os.path.join(folder, "..")))

                            # General images.
                            for file in os.listdir(ost_dir + "\\" + folder):
                                if not os.path.isdir(ost_dir + "\\" + folder + "\\" + file):
                                    zipf.write(os.path.relpath(os.path.abspath(ost_dir + "\\" + folder + "\\" + file), os.path.join(folder, "..")))
                        else:
                            path_for_zip = ost_dir + "\\" + folder

                        # Continue to the next Notebook if the current Notebook does not have images.
                        if not os.path.exists(path_for_zip):
                            continue

                        # Filling the zip file.
                        for root, dirs, files in os.walk(path_for_zip):
                            for file in files:
                                zipf.write(os.path.relpath(os.path.join(root, file), os.path.join(folder, "..")))

                    # Notebook file.
                    zipf.write(os.path.relpath(os.path.join(path_temp, notebook), os.path.join(folder, "..")))

                    zipf.close()

                    # Delete original Notebook HTML file.
                    htmlFile.close()
                    os.remove(path_temp + "\\" + notebook.split(".")[0] + ".html")

run(apply_to_biosignalsplux_website=True)

# 29/11/2018  17h18m :)