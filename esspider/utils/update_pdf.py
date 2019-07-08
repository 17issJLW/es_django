
import re
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import os
import jieba


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

secret_id = 'AKID3tUpuiIWXHlzxenE8mAH8i25sOdbkmxr'      # 替换为用户的 secretId
secret_key = 'kEcnjQt64nHXYO0NVO2RbWCcnjQr30jD'      # 替换为用户的 secretKey
region = 'ap-guangzhou'     # 替换为用户的 Region
token = None                # 使用临时密钥需要传入 Token，默认为空，可不填
scheme = 'https'            # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
# 2. 获取客户端对象
client = CosS3Client(config)

#pip install -U cos-python-sdk-v5
#pip install -U macholib
#pip install -U pefile
#pip install -U pypiwin32

base_url = 'https://esdoc-1255312386.cos.ap-guangzhou.myqcloud.com/'



baidu_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?access_token=24.baaa3b46f31dd47773b8974f5a6ac7d9.2592000.1564365738.282335-16651003'


def get_title(text_word):
    # 最初的str 要做一些更改
    primary_str = text_word
    # print((primary_str))
    # 更改
    # 去掉页码
    content = re.sub(r' +[0-9]{1,2} / [0-9]{1,2}\n', '', primary_str)
    # 去掉标记
    content = re.sub(r'Powered by TCPDF \(www.tcpdf.org\)', '', content)
    # 真正的分段 换行符后首行两个空格 最初的str中应该不会有 &#& 把
    content = re.sub(r'\n  ', '&#&  ', content)
    # 每行字数限制造成的换行  但换行符后是“裁判结果”之类的是真的需要换行 排除
    content = re.sub(r'\n(?=[^裁判结果\|审判\|人民陪审员\|陪审员\|书记员\|二〇\|一九])', '', content)
    # 真正的分段 恢复
    content = re.sub(r'&#&  ', '\n  ', content)
    str = content
    # print(str)
    # --------------更改完成-----------------------------
    # 添加词典
    jieba.load_userdict(os.getcwd()+"/esspider/utils/text.txt")

    # 文书名
    caseName = re.search(r'[^\t|\n]*(?=\n)', str)

    # 案由
    reason = re.search(r'(?<= )[^ 号]+?(?= (?:一|二|三|再)审| 刑罚变更| 其他| 复核| 再审| 执行 | 非诉执行审查)', str)
    # print(reason)

    # 案号
    try:
        caseNumber = re.search(r'(?:（|\()[1-2][0-9]{3}(?:）|\))[^号]*?号', str)
    except AttributeError:
        try:
            caseNumber = re.search(r'(?<= )《.*?最高人民法院公报》.+?(?= )', str)
        except AttributeError:
            caseNumber = re.search(r'[^ ]+?(?= %s)' % reason.group(0), str)
    return caseName.group(0) + '_' + caseNumber.group(0)


def get_list(dirname):
    for root, dirs, files in os.walk(dirname):
        return files

# 通用  root为要上传的pdf的相对路径（部分） 如 root = './each_case_pdf/'
def update_pdf(uuid:str,text_tilte:str,root:str): # uuid已定 上传指定目录下的pdf（原名为uuid 更名为text_tilte）
    file_name = root+uuid+'.pdf'
    if os.path.exists(file_name):
        key_value=text_tilte+'.pdf'
        with open(file_name, 'rb') as fp:
            response = client.put_object(
                Bucket='esdoc-1255312386',
                Body=fp,
                Key=key_value,
                StorageClass='STANDARD',
                EnableMD5=False
        )
    else:
        print('不存在'+file_name+',上传失败')





# 遍历文件中的txt 如果有对应txt文件才尝试上传pdf 上传要改名 如果获取title失败就删除txt
# title为 caseName_caseNumber
# list_ = get_list(r'C:\Users\Q\PycharmProjects\pdf2txt\each_txt_14')
# i = 0
# count = 0
# for file_name in list_:
#     txt_name = './each_txt_14/' + file_name
#     uuid = re.sub(r'.txt','',file_name)
#     print(uuid)
#     i = i+1
#     print(i)
#     print(uuid)
#     try:
#         print(get_title(txt_name))
#         update_pdf(uuid=uuid, text_tilte=get_title(txt_name), root='./each_pdf_14/')
#     except AttributeError:
#         count = count + 1
#         # print(count)
#         # os.remove(path)  # 激进办法 直接删除
# print(count)


def get_title_new(txt):

    str = txt
    # 获取正文
    str1 = str.replace('\t\t', "\t")
    # print(str1)
    str1 = re.sub(r'[0-9]{1,2} / [0-9]{1,2}', '', str1)  # 去除页码
    str1 = re.sub(r'', '', str1)  # 去除页码
    str1 = re.sub(r'Powered by TCPDF \(www.tcpdf.org\)', '', str1)  # 去除标记
    str1 = str1.replace('\n\n  ', "###")  # 真新段落
    str1 = str1.replace('\n\n', "&&&")  # 真新段落 末尾审判人姓名后直接换行
    str1 = str1.replace('\n', "")  # 假新段落
    # print(str1)
    str1 = re.sub(r'### {0,}### {0,}', '\n  ', str1)  # 恢复段落（换页的情况）
    str1 = str1.replace("###", "\n  ")  # 恢复段落
    str1 = str1.replace('&&&', "\n")  # 恢复换行
    str1 = re.sub(r'\n{1,} {1,}\n{1,}', '', str1)
    content = str1
    # print(str1)

    # 文书名
    case_name = re.search(r'[^\t|\n]*(?=\n)',str1)
    # 案由
    try:
        reason = re.search(r'(?<= )[^ ]+?(?= (?:一|二|三|再)审| 刑罚变更| 其他| 复核| 再审| 执行 | 非诉执行审查)', str1)
        print(reason.group(0))
    finally:
        print('案由')
    # 案号
    try:
        caseNumber = re.search(r'(?:（|\()[1-2][0-9]{3}(?:）|\))[^号]*?号', str1)
        print(caseNumber.group(0))
    except AttributeError:
        try:
            caseNumber = re.search(r'(?<= )《.*?最高人民法院公报》.+?(?= )', str1)
            print(caseNumber.group(0))
        except AttributeError:
            caseNumber = re.search(r'[^ ]+?(?= %s)' % reason.group(0), str1)
            print(caseNumber.group(0))
    return case_name.group(0) + '_' + caseNumber.group(0)





