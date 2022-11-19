import requests
import re
from lxml import etree
from myran import Myran
from concurrent.futures import ThreadPoolExecutor

excutor = ThreadPoolExecutor(5)
def get_url():
    url_list=[]
    myran = Myran()
    headers={
        "User-Agent":myran.agents()
    }
    url='https://jmcomic.bet/'
    try:
        rsp = requests.get(url,headers=headers)
        if rsp.status_code==200:
            rsp.encoding="UTF-8"
            #print(rsp.text)
            htmlxpath = etree.HTML(rsp.text)
            p_list = htmlxpath.xpath("//div[@class='word']/p")
            #print(len(p_list))
            #print(p_list[0].__dir__())
            for tag_p in p_list:
                #print(tag_p.text)
                if re.findall(r'內地|分流',tag_p.text):
                    for p_text in tag_p.xpath("./text()"):
                        if re.findall(r'\w+\.\w+',p_text):
                            url = re.sub(r'\\n','',re.findall(r'\w+\.\w+',p_text)[0])
                            url_list.append(url)
            return url_list
    except Exception as e:
        print(e.__traceback__.tb_lineno,e)

def reqs_url(urlstr):
    myran = Myran()
    headers = {
        "User-Agent": myran.agents()
    }
    try:
        rsp2 = requests.get('https://%s' % urlstr, headers=headers)
        if rsp2.status_code==200:
            return urlstr
    except Exception as e:
        print(e.__traceback__.tb_lineno,e)

def appmain():
    urllist=[]
    for data in excutor.map(reqs_url, get_url()):
        if data:
            urllist.append(data)
    return urllist
# if __name__ == '__main__':
#     print(app())