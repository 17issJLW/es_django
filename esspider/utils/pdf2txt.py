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

from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import os

def parse_pdf_to_txt(filepath):
    result_txt = ""
    fp = open(filepath, 'rb') # 以二进制读模式打开
    #用文件对象来创建一个pdf文档分析器
    praser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    praser.set_document(doc)
    doc.set_parser(praser)
    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    doc.initialize()

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages(): # doc.get_pages() 获取page列表
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
            for x in layout:
                if (isinstance(x, LTTextBoxHorizontal)):
                    results = x.get_text()
                    result_txt += results
                    # with open(r'E:/2.txt', 'a') as f:
                    #     results = x.get_text()
                    #     print(results)
                    #     f.write(results + '\n')
        return result_txt