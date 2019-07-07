import sys
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from io import open
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')

# os.listdir(os.getcwd()+"/each_pdf_7")
# print(os.listdir(os.getcwd()+"/each_pdf_1"))
def readPDF(pdfFile):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    process_pdf(rsrcmgr, device, pdfFile)
    device.close()
    content = retstr.getvalue()
    retstr.close()
    return content


def saveTxt(title,txt):
    with open("each_txt_14/"+title, "w",encoding='utf-8') as f:
    # with open("istxt.txt", "wb") as f:
        f.write(txt)
# k = 0
# for i in os.listdir(os.getcwd()+"/each_pdf_14"):
#     if i[-4:] == ".pdf":
#         txt = readPDF(open(os.getcwd()+"/each_pdf_14/"+i,"rb"))
#         saveTxt(i.replace(".pdf",".txt"),txt)
#         k = k + 1
#         print(k)