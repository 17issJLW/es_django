import jieba
import re
# 你的text.py
from .test import parse
import json
import requests
import os
from urllib.parse import quote


# 通用 返回上传至服务器的pdf的url -》以便写入字典
def get_doc_url(text_tilte:str):
    # 上传pdf的url的共同部分
    base_url = 'https://esdoc-1255312386.cos.ap-guangzhou.myqcloud.com/'
    key_name = text_tilte+'.pdf'
    url = base_url + quote(key_name)
    return url
def get_litigant(text_tilte:str):
    baidu_url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?access_token=24.baaa3b46f31dd47773b8974f5a6ac7d9.2592000.1564365738.282335-16651003'
    litigant = []
    post_data = {
        "text":""
    }
    post_data["text"]=text_tilte
    sess = requests.session()
    r =sess.post(url=baidu_url,data=json.dumps(post_data),headers={'Content-Type': 'application/json'})
    content = r.text
    if (content):
        # print(content)
        text = json.loads(content)
        # print(text)
        for record in text["items"]:
           if record['ne'] == 'PER':
               # print(record['item'])
               litigant.append(record['item'])
    return litigant

def getdict(text_word):
    doc = {
        "caseName": "",
        "court": "",
        "caseType": [],
        "caseNumber": "",
        "docType": "",
        "reason": "",
        "content": "",
        "litigant": [],
        "time": "",
        "url": "",
        "lawList": [],
        "stage": [],
        "location": "",
        "lawNameList": []
    }
    law_brief = [
        {
            "name": "《中华人民共和国民事诉讼法》",
            "brief": "民事诉讼法",
        },
        {
            "name": "《中华人民共和国刑事诉讼法》",
            "brief": "刑事诉讼法",
        },
        {
            "name": "《中华人民共和国刑法》",
            "brief": "刑法",
        }
    ]

    #最初的str 要做一些更改
    primary_str=text_word
    # print((primary_str))
    # 更改
    # 去掉页码
    content = re.sub(r' +[0-9]{1,2} / [0-9]{1,2}\n', '', primary_str)
    # 去掉标记
    content = re.sub(r'Powered by TCPDF \(www.tcpdf.org\)', '', content)
    # 真正的分段 换行符后首行两个空格 最初的str中应该不会有 &#& 把
    content = re.sub(r'\n  ', '&#&  ', content)
    # 每行字数限制造成的换行  但换行符后是“裁判结果”之类的是真的需要换行 排除
    content = re.sub(r'\n', '', content)
    # content = re.sub(r'\n(?=([^裁判结果\|\^审判\|\^人民\|\^陪审员\|\^书记员\|\^二〇\|\^一九]))', '', content)
    content = re.sub(r'(?=裁判结果|审判长|审判员|审 判 长|审 判 员|人民审判员|代理审判员|书记员|书 记 员|二〇|一九)', '\n', content)
    content = re.sub(r'(?<=人民|代理)(?=审判员)', '', content)
    # 真正的分段 恢复
    content = re.sub(r'&#&  ', '\n  ', content)
    str = content
    # print(str)
    # --------------更改完成-----------------------------

    # 全文
    doc["content"]=str

    # 添加词典
    jieba.load_userdict(os.getcwd()+"/esspider/utils/text.txt")

    # 全模式
    seg_list_1 = jieba.cut(str, cut_all=True)
    str_1 = "/".join(seg_list_1)
    # print(str_1)

    # 精准模式
    seg_list_2 = jieba.cut(str)
    str_2 = "/".join(seg_list_2)
    # print(str_2)

    # 文书名
    caseName = re.search(r'[^\t|\n]*(?=\n)', str)
    doc["caseName"] = caseName.group(0)

    # 当事人
    litigant = get_litigant(caseName.group(0))
    doc["litigant"] = litigant

    # 时间
    time = re.search(r'[1-2][0-9]{3}-[0-9]{2}-[0-9]{2}', str)
    doc["time"] = time.group(0)

    # 案由
    reason = re.search(r'(?<= )[^ 号]+?(?= (?:一|二|三|再)审| 刑罚变更| 其他| 复核| 再审| 执行 | 非诉执行审查)', str)
    doc["reason"] = reason.group(0)
    # print(reason)

    # 流程
    stage = re.search(r'(?<=%s ).+?(?= )' % reason.group(0), str)
    doc["stage"] = stage.group(0)
    # print(stage)

    # 案号
    try:
        caseNumber = re.search(r'(?:（|\()[1-2][0-9]{3}(?:）|\))[^号]*?号', str)
        doc["caseNumber"] = caseNumber.group(0)
        # print(caseNumber)
    except AttributeError:
        try:
            caseNumber = re.search(r'(?<= )《.*?最高人民法院公报》.+?(?= )', str)
            doc["caseNumber"] = caseNumber.group(0)
            # print(caseNumber)
        except AttributeError:
            caseNumber = re.search(r'[^ ]+?(?= %s)' % reason.group(0), str)
            doc["caseNumber"] = caseNumber.group(0)
            # print(caseNumber)

    # url
    url = get_doc_url(caseName.group(0) + '_' + caseNumber.group(0))
    doc["url"] = url

    # 法院
    court = re.search(r'(?<= )[^ 《]+?(人民)*法院', str)
    court = re.sub(r'行政|[刑民]事', '', court.group(0))
    doc["court"] = court
    # print(court)

    # 地理位置
    if court == '最高人民法院':
        location = '北京市'
        doc["location"] = location
    else:
        location = re.search(r'.*?(?=((?:高|中|初)级)*(人民)*法院)', court)
        location = re.sub(r'(?:第(?:一|二|三|四|五|六)|铁路运输)', '', location.group(0))
        doc["location"] = location
        # print(location)

    # 案件类型
    caseType = []
    caseType_1 = re.search(r'(?:行政|刑事|民事|国家赔偿)', str_1)
    caseType.append(caseType_1.group(0))
    caseType_2 = re.search(r'(?:判决|裁定|决定|调解|通知)', str_1)
    caseType.append(caseType_2.group(0))
    doc["caseType"] = caseType
    # print(caseType)

    # 文书类型
    try:
        docType = re.search(r'刑事附带民事..书', caseName.group(0))
        doc["docType"] = docType.group(0)
        # print(docType)
    except:
        docType = caseType_1.group(0) + caseType_2.group(0) + '书'
        doc["docType"] = docType
        # print(docType)

    # lawNameList
    lawNameList = re.findall(r'《中[^》]*?法》', str)
    temp = re.findall(r'(?:＜|〈)中华人民共和国[^》]*?法(?:＞|〉)', str)
    # print(temp)
    lawNameList_ = []
    for name in temp:
        name_1 = re.sub(r'(?:＜|〈)', '《', name)
        name_2 = re.sub(r'(?:＞|〉)', '》', name_1)
        lawNameList_.append(name_2)
    lawNameList = lawNameList + lawNameList_
    lawNameList = list(set(lawNameList))
    doc["lawNameList"] = lawNameList
    # print(lawNameList)

    # lawList
    lawList = []  # 具体到第几条
    law = []  # 法律（某部）的名称列表
    law_first_part = []  # 进行两次搜索 这是第一次得到的结果
    law_second_part = []
    base_law = re.findall(r'《中[^》]*?法》[^，、及]*?第[^，、及]*?条', str)
    temp = []
    for i in base_law:
        temp.append(re.sub(r'(?:\（|\().+简称.+?(?:\)|）)', '', i))
    for i in temp:
        law_first_part.append(re.sub(r'(?:\（|\(|\)|）)', '', i))
    for i in base_law:
        law_full_name = re.search(r'《[^》]*》', i).group(0)
        law.append(law_full_name)
    temp_str1 = str
    for i in law:
        for j in law_brief:
            if j["name"] == i:
                temp_str1 = str.replace(j["brief"], j["name"])
    temp_2 = re.findall(r'《中[^》]*法》第[^，、]*?条', temp_str1)
    for i in temp_2:
        law_second_part.append(re.sub(r'(?:\（|\(|\)|）)', '', i))
    lawList = law_first_part + law_second_part
    lawList = list(set(lawList))
    doc["lawList"] = lawList

    return doc




# 测试
# print(getdict("0a483cfdc242b1bdd479b09e16019807.pdf"))
