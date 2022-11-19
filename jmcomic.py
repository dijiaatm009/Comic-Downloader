#coding=gbk
import requests
from lxml import etree
from myran import Myran
import re,io
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

class JmComic:
    def __init__(self,proxy):
        self.proxy=proxy
    def getTypes(self,url):
        headers={
            "User-Agent":Myran().agents()
        }
        try:
            rsp = requests.get(url, headers=headers,proxies=self.proxy)
            if rsp.status_code == 200:
                rsptree = etree.HTML(rsp.text)
                type_list = rsptree.xpath("//div[contains(@class,'list-group')]/a")
                rank_title_list = rsptree.xpath("//div[contains(@class,'pull-left')]/div[@class='hidden-xs']/div[last()]/ul[@class='dropdown-menu']/li/a")
                rank_dict = {}
                type_dict={}
                print(rank_title_list)
                for rank_title in rank_title_list:
                    #rank_title_name = rank_title.xpath("button/text()")[0].strip()
                    #rank_item_list = rank_title.xpath( "ul[@class='dropdown-menu']/li/a")
                    #print(rank_title,rank_item_list)
                    #rank_dict[rank_title_name]={}
                    # for rank_item in rank_item_list:
                    #     rank_name=rank_item.xpath("text()")[0]
                    #     rank_dict[rank_title_name][rank_name]=re.findall(r'\?(\w+=\w+)',rank_item.attrib['href'])[0]
                    rank_dict[rank_title.xpath('text()')[0]]=re.findall(r'\?(\w+=\w+)',rank_title.attrib['href'])[0]
                print('rank_dict',rank_dict)
                for type in type_list:
                    type_dict[type.text.strip()]=type.attrib['href']
                return rank_dict,type_dict
        except Exception as e:
            print(e.__traceback__.tb_lineno,e)

    def getcomic_ml(self,url):
        headers = {
            "User-Agent": Myran().agents()
        }
        try:
            print('getcomic_ml',url)
            rsp  = requests.get(url, headers=headers,proxies=self.proxy)
            if rsp.status_code == 200:
                rsptree = etree.HTML(rsp.text)
                #获取漫画列表
                comic_list=rsptree.xpath("//div[@class='container']/div[@class='row']/div/div[contains(@class,'row')]/div")
                max_num=rsptree.xpath("//div/ul[contains(@class,'pagination')]/li/select/option[last()]/text()")
                max_num=int(max_num[0]) if max_num else 0
                max_ym_list=[num for num in range(1,max_num+1)]
                print('max_ym',max_ym_list,len(comic_list))
                comic_dict={}
                for comic in comic_list:
                    comic_name_xpath=comic.xpath("div/a/span/text()")
                    if comic_name_xpath==[]:
                        comic_name_xpath=comic.xpath("div/span/text()")
                    comic_name=comic_name_xpath[0]
                    comic_name = comic_name.encode('GBK', 'ignore').decode('GBk')
                    comic_url_xpath=comic.xpath("div[1]/a/@href")
                    if comic_url_xpath==[]:comic_url_xpath=comic.xpath("div/div[1]/a/@href")
                    comic_url=comic_url_xpath[0]
                    comic_dict[comic_name]=comic_url
                    #print('comic_name,comic_url',comic_name,comic_url)
                return comic_dict,max_ym_list
        except Exception as e:
            print(e.__traceback__.tb_lineno,e)

    def getPhoto(self,url):
        excutor = ThreadPoolExecutor(2)
        def getcoverImg(img_url):
            for i in range(2):
                cover_rsp = requests.get(url=img_url, headers=headers, proxies=self.proxy)
                if cover_rsp.status_code == 200:
                    dataBytesIO = io.BytesIO(cover_rsp.content)
                    img = Image.open(dataBytesIO)
                    cover_img = img
                    return cover_img
                else:continue
            return ''
        headers = {
            "User-Agent": Myran().agents()
        }
        try:
            print('getPhoto',url)

            referer = re.findall(r'(https://\w+\.\w+)/', url)[0]
            rsp = requests.get(url, headers=headers,proxies=self.proxy)
            if rsp.status_code == 200:
                rsptree = etree.HTML(rsp.text)
                # 获取话数列表
                nums = rsptree.xpath("//div[@class='row']/div[6]/div[1]/div[1]/ul[contains(@class,'btn-toolbar')]/a")
                book_name = rsptree.xpath("//div[@itemprop='name']/h1[@id='book-name']/text()")
                if book_name:
                    book_name=book_name[0]
                    book_name = re.sub(r'[\\\/\|\(\)\~\?\.\:\：\-\*\<\>]', '', book_name)
                cover_img_url=rsptree.xpath("//div[@id='album_photo_cover']/div/a/div/img/@src")[0]
                cover_img=excutor.submit(getcoverImg,cover_img_url).result()
                print('cover_img',cover_img)
                #print('cover_img_url', cover_img_url,cover_img)
                photo_dict={book_name:{}}
                if nums:
                    for i in nums:
                        photo_name_list = i.xpath("li/text()")[0].split()
                        #print(re.findall(r'[\u4E00-\u9FA5]+.*?', i.xpath("li/text()")[0]))
                        try:
                            if re.findall(r'[\u4E00-\u9FA5]', photo_name_list[2]):
                                photo_name=re.sub(r'\s','',photo_name_list[0])+' '+photo_name_list[2]
                            else:photo_name=re.sub(r'\s','',photo_name_list[0])
                        except Exception as e:
                            photo_name = re.sub(r'\s', '', photo_name_list[0])
                        photo_name = re.sub(r'[\\\/\|\(\)\~\?\.\:\：\-\*\<\>\-]', '',photo_name)
                        #print(photo_name)
                        photoid=i.attrib['data-album']
                        phurl=referer + i.attrib['href']
                        photo_dict[book_name][photo_name] = [photoid,phurl]
                else:
                    photo_name = "共一話"
                    # print(photo_name)
                    album_photo_cover_xpath =rsptree.xpath("//div[@class='row']/div[@id='album_photo_cover']/div[1]/a/@href")[0]
                    photoid = re.findall(r'/(\d+)/', album_photo_cover_xpath)[0]
                    phurl = "%s/photo/%s"%(referer,photoid)
                    photo_dict[book_name][photo_name] = [photoid,phurl]
                excutor.shutdown(True)
                return photo_dict,cover_img
        except Exception as e:
            print(e.__traceback__.tb_lineno, e)

    def getcover(self,url):
        pass

#
#
# if __name__ == '__main__':
#     print([num for num in range(100)])
