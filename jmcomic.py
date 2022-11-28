#coding=utf-8
import threading

import PySimpleGUI as sg
import requests
from lxml import etree
from myran import Myran
import re,io,json
from PIL import Image

from concurrent.futures import ThreadPoolExecutor

class JmComic:
    def __init__(self,proxy):
        self.proxy=proxy
        self.getcomic_json_thdid=''
        self.wz_xpath_dict = {
        "jm天堂":{
            "type_url":"",
            "rank_url":"",
            "type_title": "text()",
            "rank_title": "text()",
            "type_title_href": "@href",
            "rank_title_href": "@href",
            "type_all":"//div[contains(@class,'list-group')]/a",
            "rank_all":"//div[contains(@class,'pull-left')]/div[@class='hidden-xs']/div[last()]/ul[@class='dropdown-menu']/li/a",
            "comic_all":"//div[@class='container']/div[@class='row']/div/div[contains(@class,'row')]/div",
            "max_ye":"//div/ul[contains(@class,'pagination')]/li/select/option[last()]/text()",
            "comic_name1":"div/a/span/text()",
            "comic_name2":"div/span/text()",
            "comic_url1":"div[1]/a/@href",
            "comic_url2":"div/div[1]/a/@href",
            "photo_all":"//div[@class='row']/div[6]/div[1]/div[1]/ul[contains(@class,'btn-toolbar')]/a",
            "photo_name":"li/text()",
            "photo_url":'@href',
            "book_name":"//div[@itemprop='name']/h1[@id='book-name']/text()",
            "cover_url":"//div[@id='album_photo_cover']/div/a/div/img/@src",

    },
        "樱花漫画":{
            "type_url":"",
            "rank_url":"",
            "type_title": "text()",
            "rank_title": "",
            "type_title_href": "@href",
            "rank_title_href": "",
            "type_all":"//div[@class='classify-nav'][1]/div/a",
            "rank_all":"none",
            "comic_all":"//div[contains(@class,'classify-items')]/div",
            "max_ye":"//div[@id='pagelink']/div[@id='pagelink']/a[last()]/text()",
            "comic_name1": "a[2]/div/text()",
            "comic_name2": "",
            "comic_url1": "a[2]/@href",
            "comic_url2": "",
            "photo_all": "//div[contains(@class,'l-box')]/div[@id='chapter-items'][2]/div",
            "photo_name": "a/div/span/text()",
            "photo_url": 'a/@href',
            "book_name": "//div[contains(@class,'comics-detail__info')]/h1/text()",
            "cover_url": "//div[contains(@class,'de-info__box')]/div/img/@src",
        },
        "奇漫屋": {
            "type_url":"http://www.qiman57.com/sort/1-1.html",
            "rank_url":"http://www.qiman57.com/rank/1-1.html",
            "type_title": "li/text()",
            "rank_title": "li/text()",
            "type_title_href": "@href",
            "rank_title_href": "@href",
            "type_all":"//div[contains(@class,'rankNavNew')]/ul/a",
            "rank_all":"//div[contains(@class,'rankNavNew')]/ul/a",
            "comic_all": "//div[@class='updateList']/div[contains(@class,'bookList_3')]/div",
            #下一页符号的上一个li标签
            "max_ye_p_url": "//div[contains(@class,'page-pagination')]/ul/li[last()-1]/a/@href",
            "max_ye": "//div[contains(@class,'page-pagination')]/ul/li[last()]/a/text()",
            "comic_name1": "p[1]/a/text()",
            "comic_name2": "",
            "comic_url1": "p[1]/a/@href",
            "comic_url2": "",
            "photo_all": "//div[@id='chapter-list1']/a",
            "photo_name": "text()",
            "photo_url": '@href',
            "book_name": "//h1[@class='name_mh']/text()",
            "cover_url": "//div[@class='img']/img/@src",
        }

}

    # 获取类型和排行
    def getTypes(self,wz_name,url):
        print("wz_name,url:",wz_name,url)
        headers={
            "User-Agent":Myran().agents()
        }
        def gettype():
            nonlocal type_list,rank_title_list
            try:
                type_rsp = requests.get(url, headers=headers, proxies=self.proxy)
                type_rsp_text = type_rsp.text
                if re.findall(r"utf|gbk", type_rsp.encoding, re.I) == []:#把网页源代码编码解码后在xpath查找
                    type_rsp_text = type_rsp_text.encode(type_rsp.encoding).decode("gbk")
                if type_rsp.status_code == 200:
                    type_rsptree = etree.HTML(type_rsp_text)
                    #获取类别
                    type_list = type_rsptree.xpath(self.wz_xpath_dict[wz_name]["type_all"])
                    print("xpath获取type:%s个"%len(type_list))
                    if wz_name == "jm天堂":
                        rank_title_list = type_rsptree.xpath(self.wz_xpath_dict[wz_name]["rank_all"])
            except Exception as e:
                print(e.__traceback__.tb_lineno,e)

        def getrank():
            nonlocal rank_title_list
            try:
                rank_url = self.wz_xpath_dict[wz_name]['rank_url']
                if rank_url:
                    rank_rsp = requests.get(self.wz_xpath_dict[wz_name]["rank_url"], headers=headers, proxies=self.proxy)
                    rank_rsp_text = rank_rsp.text
                    if re.findall(r"utf|gbk", rank_rsp.encoding, re.I) == []:
                        rank_rsp_text = rank_rsp_text.encode(rank_rsp.encoding).decode("gbk")
                    if rank_rsp.status_code == 200:
                        rank_rsptree = etree.HTML(rank_rsp_text)
                        rank_title_list = rank_rsptree.xpath(self.wz_xpath_dict[wz_name]["rank_all"])
            except Exception as e:
                print(e.__traceback__.tb_lineno,e)

        try:
            rank_dict = {}
            type_dict={}
            type_list=[]
            rank_title_list=[]
            gettype_thd=threading.Thread(target=gettype)
            getrank_thd=threading.Thread(target=getrank)
            gettype_thd.start()
            getrank_thd.start()
            gettype_thd.join()
            getrank_thd.join()
            print("rank_title_list",rank_title_list)
            for rank_title_xpath in rank_title_list:
                rank_title = rank_title_xpath.xpath(self.wz_xpath_dict[wz_name]["rank_title"])
                if rank_title != []:
                    if wz_name == "jm天堂":
                        rank_dict[rank_title[0].strip()] =re.findall(r'\?(\w+=\w+)',rank_title_xpath.xpath(self.wz_xpath_dict[wz_name]["rank_title_href"])[0])[0]
                    else:
                        rank_dict[rank_title[0].strip()] =rank_title_xpath.xpath(self.wz_xpath_dict[wz_name]["rank_title_href"])[0]
            print('rank_dict',rank_dict)
            for type in type_list:
                type_title=type.xpath(self.wz_xpath_dict[wz_name]["type_title"])
                if type_title != []:
                    type_dict[type_title[0].strip() ]=type.xpath(self.wz_xpath_dict[wz_name]["type_title_href"])[0]
            if wz_name=='奇漫屋':#网站没有类别和排行一起查询 合并到类别
                type_dict.update(rank_dict)
                return {},type_dict
            return rank_dict,type_dict
        except Exception as e:
            print(e.__traceback__.tb_lineno,e)

    #获取当前页面所有漫画列表
    def getcomic_ml(self,window: sg.Window,wz_name,url):
        excutor = ThreadPoolExecutor(2)
        def getmaxye(rsptree_max):
            nonlocal max_num
            print("递归获取最大页码")
            try:
                next_ye_xpath = rsptree_max.xpath(self.wz_xpath_dict[wz_name]["max_ye"])
                if next_ye_xpath:
                    next_ye=next_ye_xpath[0].strip()
                    print('next_ye',next_ye,next_ye.isdigit())
                    if next_ye.isdigit():
                        max_num=next_ye
                        max_ym_list = [num for num in range(1, int(max_num) + 1)]
                        window["-ye-"].update(values=max_ym_list, value=max_ym_list[0] if len(max_ym_list) else [])
                    else:
                        host = re.findall(r'(https://.*?)/', url)
                        host = host if host else re.findall(r'(http://.*?)/', url)
                        host = host[0] if host else ''
                        p_ye_url = rsptree_max.xpath(self.wz_xpath_dict[wz_name]["max_ye_p_url"])[0]
                        next_url = host + p_ye_url
                        print('host,p_ye_xpath', host, p_ye_url)
                        rsp_next = requests.get(next_url, headers=headers)
                        if rsp_next.status_code == 200:
                            rsp_next_etree = etree.HTML(rsp_next.text)
                            getmaxye(rsp_next_etree)
            except:
                pass
        headers = {
            "User-Agent": Myran().agents()
        }
        try:
            print('getcomic_ml',url)
            rsp  = requests.get(url, headers=headers,proxies=self.proxy)
            if rsp.status_code == 200:
                rsp_text = rsp.text
                if re.findall(r"utf|gbk", rsp.encoding, re.I) == []:
                    rsp_text = rsp_text.encode(rsp.encoding).decode("gbk")
                rsptree = etree.HTML(rsp_text)
                #获取漫画列表
                comic_list=rsptree.xpath(self.wz_xpath_dict[wz_name]["comic_all"])
                max_num=0
                if wz_name=="奇漫屋":#页码
                    excutor.submit(getmaxye,rsptree)
                    print("最大页码", max_num)
                else:
                    max_num=rsptree.xpath(self.wz_xpath_dict[wz_name]["max_ye"])
                    max_num=int(max_num[0]) if max_num else 0

                max_ym_list=[num for num in range(1,int(max_num)+1)]
                print('max_ym',max_ym_list,len(comic_list))
                comic_dict={}
                for comic in comic_list:
                    comic_name_xpath=comic.xpath(self.wz_xpath_dict[wz_name]["comic_name1"])
                    if comic_name_xpath==[]:#备用xpath
                        comic_name_xpath=comic.xpath(self.wz_xpath_dict[wz_name]["comic_name2"])
                    comic_name=comic_name_xpath[0]
                    #漫画名编码解码 避免特殊符号报错
                    comic_name = comic_name.encode('GBK', 'ignore').decode('GBK')
                    comic_url_xpath=comic.xpath(self.wz_xpath_dict[wz_name]["comic_url1"])
                    if comic_url_xpath==[]:#备用xpath
                        comic_url_xpath=comic.xpath(self.wz_xpath_dict[wz_name]["comic_url2"])
                    comic_url=comic_url_xpath[0]
                    comic_dict[comic_name]=comic_url
                    print('comic_name,comic_url',comic_name,comic_url)
                return comic_dict,max_ym_list
        except Exception as e:
            print(e.__traceback__.tb_lineno,e)
    #获取漫画所有章数
    def getPhoto(self,window: sg.Window,wz_name,book_name,url):
        photo_name=''
        photoid = ''
        phurl=''
        nums = []
        thread_id=threading.get_ident()
        print('threading.get_ident():%s'%threading.get_ident())
        if book_name:
            # 过滤特殊符号 避免创建文件夹错误
            book_name = re.sub(r'[\\\/\|\(\)\~\?\.\:\：\-\*\<\>]', '', book_name)

        photo_dict = {book_name: {}}
        #封面加载
        def getcoverImg(img_url):
            try:
                if wz_name=='jm天堂':
                    img_url=re.sub(r'(https://.*?)/',host+"/", img_url)
                #print("host:%s,img_url:%s"%(host,img_url))
                #print('threading.get_ident()getcoverImg:%s'%threading.get_ident())
                cover_rsp = requests.get(url=img_url, headers=headers, proxies=self.proxy)
                if cover_rsp.status_code == 200:
                    dataBytesIO = io.BytesIO(cover_rsp.content)
                    img = Image.open(dataBytesIO)
                    cover_img = img
                    if cover_img:
                        imh_w, img_h = cover_img.size#获取图片长宽
                        f_wifth, f_height = window['-f_img-'].get_size()#获取框架宽高
                        new_img_w = int(f_height * imh_w / img_h) #根据边框调整图片大小
                        cover_img_resize = cover_img.resize((int(new_img_w), int(f_height)))
                        with io.BytesIO() as bio:#把图片加载到内存再读取
                            cover_img_resize.save(bio, format="PNG")
                            del cover_img_resize
                            cover_base64 = bio.getvalue()
                        if self.getcomic_json_thdid==thread_id:
                            window['-cover_img-'].update(data=cover_base64)
                        del cover_img,cover_base64

                        # with io.BytesIO() as bio2:#原图
                        #     cover_img.save(bio2, format="PNG")
                        #     del cover_img
                        #     cover_resize_base64 = bio2.getvalue()
            except Exception as e:
                print(e.__traceback__.tb_lineno,e)

        #奇漫屋异步加载数据
        def getcomic_json_qmw():
            print("奇漫屋异步加载数据")
            nonlocal photo_dict
            bookid = re.findall(r'com/(\w+?)/',url)[0]
            photoid=''
            if bookid:
                xhr_url="http://www.qiman58.com/bookchapter/"
                data={
                    "id":bookid,
                    "id2":1
                }
                xhr_rsp = requests.post(xhr_url,headers=headers,data=data)
                xhr_json = xhr_rsp.text
                xhr_list = json.loads(xhr_json)
                for item_dict in xhr_list:
                    photo_name=item_dict['chaptername']
                    phurl='%s/%s/%s.html'%(host,bookid,item_dict['chapterid'])
                    photo_dict[book_name][photo_name] = [photoid,phurl]

        def getcomic_json():
            nums = rsptree.xpath(self.wz_xpath_dict[wz_name]["photo_all"])
            if nums:
                for i in nums:
                    if wz_name == "jm天堂":
                        photo_name_list = i.xpath(self.wz_xpath_dict[wz_name]["photo_name"])[0].split()
                        # print(re.findall(r'[\u4E00-\u9FA5]+.*?', i.xpath("li/text()")[0]))
                        try:
                            if re.findall(r'[\u4E00-\u9FA5]', photo_name_list[2]):
                                photo_name = re.sub(r'\s', '', photo_name_list[0]) + ' ' + photo_name_list[2]
                            else:
                                photo_name = re.sub(r'\s', '', photo_name_list[0])
                        except Exception as e:
                            photo_name = re.sub(r'\s', '', photo_name_list[0])
                    else:
                        photo_name = i.xpath(self.wz_xpath_dict[wz_name]["photo_name"])[0]
                    photo_name = re.sub(r'[\\\/\|\(\)\~\?\.\:\：\-\*\<\>\-\s]', '', photo_name)
                    print('photo_name', photo_name)
                    photoid = ''
                    phurl = host + i.xpath(self.wz_xpath_dict[wz_name]["photo_url"])[0]
                    try:
                        if wz_name == 'jm天堂':
                            photoid = i.attrib['data-album']
                    except:
                        pass
                    print(book_name, photo_name, photoid, phurl)
                    photo_dict[book_name][photo_name] = [photoid, phurl]

            else:
                if wz_name == "jm天堂":
                    photo_name = "共一話"
                    # print(photo_name)
                    # album_photo_cover_xpath =rsptree.xpath("//div[@class='row']/div[@id='album_photo_cover']/div[1]/a/@href")[0]
                    photoid = re.findall(r'/(\d+)/', url)[0]
                    phurl = "%s/photo/%s" % (host, photoid)
                    photo_dict[book_name][photo_name] = [photoid, phurl]
        headers = {
            "User-Agent": Myran().agents()
        }
        try:

            host = re.findall(r'(https://.*?)/', url)
            host = host if host else re.findall(r'(http://.*?)/', url)
            host = host[0] if host else ''
            if wz_name == '奇漫屋':
                getcomic_json_qmw_thd=threading.Thread(target=getcomic_json_qmw)
                getcomic_json_qmw_thd.start()
                getcomic_json_qmw_thd.join()
            rsp = requests.get(url, headers=headers,proxies=self.proxy)
            if rsp.status_code == 200:
                rsp_text = rsp.text
                if re.findall(r"utf|gbk", rsp.encoding, re.I) == []:
                    rsp_text = rsp_text.encode(rsp.encoding).decode("gbk")
                rsptree = etree.HTML(rsp_text)

                cover_img=''
                cover_img_url=rsptree.xpath(self.wz_xpath_dict[wz_name]["cover_url"])
                if cover_img_url!=[]:
                    cover_img_url=cover_img_url[0]
                    getcoverImg_thread=threading.Thread(target=getcoverImg,args=(cover_img_url,))
                    getcoverImg_thread.start()
                # 获取话数列表
                print("getphoto", wz_name, book_name, url,host)
                if wz_name != '奇漫屋':
                    getcomic_json_thd=threading.Thread(target=getcomic_json)
                    getcomic_json_thd.start()
                    getcomic_json_thd.join()
                #print("photo_dict",photo_dict)
                return photo_dict,thread_id
        except Exception as e:
            print(e.__traceback__.tb_lineno, e)


    def getcover(self,url):
        pass



# if __name__ == '__main__':
#     pass