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



run_update()