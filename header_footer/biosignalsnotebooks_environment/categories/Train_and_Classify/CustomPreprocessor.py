from nbconvert.preprocessors import Preprocessor
import re


class CustomPreprocessor(Preprocessor):

    def preprocess_cell(self, cell, resources, index):
        if 'source' in cell and cell.cell_type == "markdown":
            cell.source = re.sub(r"\[(.*)\]\(([^)]*)\.ipynb\)",r"[\1](\2_rev.html)",cell.source)
            cell.source = re.sub(r"\.ipynb", r"_rev.html", cell.source)

        return cell, resources