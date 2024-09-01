import os
from pdf_remove_header_footer import PDFRemoveHeaderFooter
cwd = os.getcwd()
path_in = os.path.join(cwd, 'PDF_IN')
path_out = os.path.join(cwd, 'PDF_OUT')
pdfs = os.listdir(path_in)
if(len(pdfs) >= 1):
        for pdf in pdfs:
            remove = PDFRemoveHeaderFooter(f'{path_in}\\{pdf}', f'{path_out}\\{pdf}')
            remove.run()
else:
      print("Pasta de entrada vazia!!!")