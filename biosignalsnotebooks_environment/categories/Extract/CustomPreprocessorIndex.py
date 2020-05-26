from nbconvert.preprocessors import Preprocessor
import re


class CustomPreprocessor(Preprocessor):

    def preprocess_cell(self, cell, resources, index):
        if 'source' in cell and cell.cell_type == "markdown":
            cell.source = re.sub(r"'", r'"', cell.source)
            cell.source = re.sub(r"\[(.*)\]\(([^)]*)\.ipynb\)",r"[\1](\2_rev.php)",cell.source)
            #cell.source = re.sub(r"\[(.*)\]\(([^)]*)\.ipynb\)",r'<a href="#" data-notebook-link="\2_rev.html" onClick="getNotebookLink(this)">\1</a>',cell.source)
            cell.source = re.sub(r"\.ipynb", r"_rev.php", cell.source)
            cell.source = re.sub(r"\.dwipynb", r".ipynb", cell.source)
            # The following two lines should only be active when we want to publish the project at
            # biosignalsplux website.
            #cell.source = re.sub(r"\.\./\.\./", r"", cell.source)
            #cell.source = re.sub(r"\.\./", r"Categories/", cell.source)
            # cell.source = re.sub(r'href="Categories(.*)\.html"', r'href="#" data-notebook-link="Categories\1.html" onclick="getNotebookLink(this)"', cell.source)
        return cell, resources