"""
    Private module uniquely dedicated to clone the last version of bsnb_files, from the
    biosignalsnotebooks original folder.

"""

import os
import shutil

def run_update():
    current_dir = os.path.abspath(__file__).split(os.path.basename(__file__))[0].replace("\\", "/")

    # =============== Update of "images", "signal_samples" and "styles" directories ================
    aux_dir = current_dir + "osf_files/"
    for folder in ["images", "signal_samples", "styles"]:
        # Removal of oldest directory versions.
        if os.path.isdir(aux_dir + folder):
            shutil.rmtree(aux_dir + folder)

        # Clone the updated folder.
        src = "../../../biosignalsnotebooks_notebooks/" + folder
        if os.path.isdir(src):
            shutil.copytree(src, aux_dir + folder)
        else:
            raise RuntimeError("The current module has a private state. It should only be used by "
                               "the package developers!")

    # ================================ Checking if aux folder already exists ========================
    if not os.path.exists(aux_dir + "aux_folders"):
        os.makedirs(aux_dir + "aux_folders")

    # =============================== Copying aux_files folders =====================================
    src = "../../../biosignalsnotebooks_notebooks/Categories"
    categories = os.listdir(src)
    for category in ["MainFiles"]:
        # Check if an aux_files folder is available.
        possible_src = src + "/" + category + "/aux_files"
        if os.path.isdir(possible_src):
            # Removal of oldest directory versions.
            dst = aux_dir + "aux_folders/" + category + "/aux_files"
            if os.path.isdir(dst):
                shutil.rmtree(dst)

            # Copy new files
            shutil.copytree(possible_src, dst)




run_update()