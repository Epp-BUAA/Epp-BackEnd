from markdown import markdown
import pdfkit
from django.conf import settings
import os
import platform

def is_linux():
    if os.name == 'posix':
        return True
    if platform.system() == 'Linux':
        return True
    return False

path_wk = settings.LINUX_WKHTMLTOPDF_PATH if is_linux() else settings.WIN_WKHTMLTOPDF_PATH
config = pdfkit.configuration(wkhtmltopdf = path_wk)

def md2pdf(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:
        html_text = markdown(f.read(), output_format='html4')
 
    pdfkit.from_string(html_text, output_filename, configuration = config, options={'encoding': 'UTF-8', 'quiet': ''})