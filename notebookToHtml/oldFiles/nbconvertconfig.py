
import os

c = get_config()
custom_path = os.path.join("../Notebooks/Categories/mytemplate.tpl")
c.TemplateExporter.template_path.append(custom_path)
