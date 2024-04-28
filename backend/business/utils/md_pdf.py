from markdown import markdown
import pdfkit
from django.conf import settings

path_wk = settings.WIN_WKHTMLTOPDF_PATH
config = pdfkit.configuration(wkhtmltopdf = path_wk)

def md2pdf(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:
        html_text = markdown(f.read(), output_format='html4')
 
    pdfkit.from_string(html_text, output_filename, configuration = config, options={'encoding': 'UTF-8', 'quiet': ''})