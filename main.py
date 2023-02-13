

import os
import traceback
import lxml.html

import requests
import threading
import logging
import time
from send_mail import g_mail
import open_html
from urllib.parse import quote
import urllib.request as re
import json
from my_config import g_config



class Imager:
    def Analysis(self,url):
        # 解决中文搜索问题 对于：？=不进行转义
        root_url = quote(url, safe='/:?=')
        openhtml=open_html.HtmlLoader()
        html = openhtml.Open(url)
        # 将HTML解析为统一的格式
        tree = lxml.html.fromstring(html)
        #  通过lxml的xpath获取src属性的值，返回一个列表

        img = tree.xpath('//img/@src')
        return img

    def find_blog_article(self,url):

        root_url = quote(url, safe='/:?=')
        openhtml = open_html.HtmlLoader()
        html = openhtml.Open(url)
        # 将HTML解析为统一的格式
        tree = lxml.html.fromstring(html)
        #  通过lxml的xpath获取src属性的值，返回一个列表

        article = tree.xpath('//div[@dir="ltr"]/p/span/text()')
        return article

class Loader:
    def callback(self,a,b,c):
        '''回调函数可以用来显示进度
        @a:已经下载的数据块个数
        @b:数据块的大小
        @c:远程文件的大小
        '''
        per=100.0*a*b/c
        if per>100:
            per=100
        # print('%.2f%%' % per)

    def Down(self, url, filename):
        try: 
        # dir = os.path.abspath('.')
        # work_path = os.path.join(dir, 'baidu.html')
            re.urlretrieve(url, filename, self.callback)
        except BaseException as e:
            print(f"error when Down pic file, url is {url}")
            traceback.print_exc()
            


url = 'https://www.nogizaka46.com/s/n46/api/list/blog?ima=5652&rw=32&st=0&callback=res'

datestr = ''
title = ''
logger = None

g_image_save_dir = g_config.get_config("images_save_dir", './images')
g_blog_save_dir = g_config.get_config("blogs_save_dir", './blog_archive')
g_qry_interval = g_config.get_config("qry_interval", 30)
g_blog_signature = []
g_blog_max_cache = 100

def set_logger():
    global logger
    logging.basicConfig(filename='out.txt', level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', filemode='w')
    logger = logging.getLogger("test")

    # 第二步：创建控制台日志处理器+文件日志处理器
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("./myapp.log", mode="a", encoding="utf-8")

    # 第三步：设置控制台日志的输出级别,需要日志器也设置日志级别为info；----根据两个地方的等级进行对比，取日志器的级别
    console_handler.setLevel(level="INFO")

    fmt = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] %(message)s')

    console_handler.setFormatter(fmt)
    file_handler.setFormatter(fmt)

    # 第五步：将控制台日志器、文件日志器，添加进日志器对象中
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def save_blog_from_html_content(desc, html_content):
    # 保存blog原文
    with open(g_blog_save_dir + "/" + desc + ".html", "w", encoding="utf-8") as f:
        f.write(html_content)

def get_latest_release_from_url(url: str):
    res = requests.request('get', url, timeout=10)

    # 时间
    date_index = res.text.find('bl--card__date')
    datestr = res.text[date_index + 16:date_index + 32]

    # 标题
    title_index_el = res.text.find('bl--card__ttl')
    title_index_el_start = res.text.find('>', title_index_el)
    title_index_el_end = res.text.find('<', title_index_el)

    title_str = res.text[title_index_el_start + 1:title_index_el_end]

    # 链接
    href_index_el = res.text.find('bl--card js-pos a--op hv--thumb')
    href_index_el_start = res.text.find('href="', href_index_el)
    href_index_el_end = res.text.find('">', href_index_el)

    href_str = res.text[href_index_el_start + 6:href_index_el_end]

    # bl--card__img hv--thumb__i  查找缩略图
    thumb = None

    return datestr, title_str, "https://www.nogizaka46.com" + href_str, thumb

def handle_new_blog_release(new_date, new_title, new_href, new_thumb, new_member, desc, html_content):
    
    global datestr, title

    logger.info(f"find new blog: date: [{new_date}], title: [{new_title}]")

    # 下载图片
    image_list = save_img_from_url(new_href, g_image_save_dir, desc)
    mail_context = gen_mail_content(new_date, new_title, new_href, new_thumb, new_member, image_list, html_content)

    
    g_mail.send("乃木坂blog更新提醒", mail_context, 'html')

    # 更新最新的记录
    datestr = new_date
    title = new_title

    # 保存blog原文
    with open(g_blog_save_dir + "/" + desc + ".html", "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"query blog release, snapshot: [{desc}]")



def get_latest_release_from_blog_main_page(url: str):
    global g_blog_signature
    try:
        res = requests.request('get', url, timeout= 10)
    except BaseException as e:
        logger.error(f"failed to request: {e}")
        return
    
    res_len = len(res.text)
    res_str = res.text[4:res_len-2]
    res_json = json.loads(res_str)
    
    send_flag = True
    
    if len(g_blog_signature) == 0:
        send_flag = False
        
    for blog_json_item in res_json['data']:
        identifier = blog_json_item['date'] + blog_json_item['code'] + blog_json_item['title']  + blog_json_item['arti_code']
        print(f"blog identifier [{identifier}]")
        if identifier not in g_blog_signature :
            print(f"g_blog_signature is {g_blog_signature}")
            first_release_item = blog_json_item
            # 时间

            datestr = first_release_item['date']

            # 标题

            title_str = first_release_item['title']

            # 链接

            href_str = first_release_item['link']

            # bl--card__img hv--thumb__i  查找缩略图
            thumb = first_release_item['img']

            member = first_release_item['name']
            html_content = first_release_item['text']
            
            g_blog_signature.append(identifier)
            
            if send_flag:
                handle_new_blog_release(datestr, title_str, href_str, thumb, member, (datestr + member).replace('/', '-').replace(':', '.'), html_content)
    
    print(f"len of cache is {len(g_blog_signature)}, cache is [{g_blog_signature}]")            
            
    if len(g_blog_signature) >= g_blog_max_cache:
        g_blog_signature = g_blog_signature[g_blog_max_cache/2:]
    
    if len(res_json['data']) > 0:
        
        return res_json['data'][0]['date'], res_json['data'][0]['title'], res_json['data'][0]['link'], res_json['data'][0]['img'], res_json['data'][0]['name'], '', res_json['data'][0]['text']
    
    return '', '', '', '', '', '', ''
    
def get_blog_main_by_url(url: str):
    res = requests.request('get', url)



def gen_blog_content(datestr, title, href, thumb, member):
    return f"BLOG更新提醒, [{member}] ,更新时间为[{datestr}],  标题为[{title}], 链接为[{href}]"


def gen_mail_content(datestr, title, href, thumb, member, image_list, html_content):
    ouline = f"BLOG更新提醒, [{member}] ,更新时间为[{datestr}],  标题为[{title}], 链接为[{href}]"
    images_tag = ''
    for image in image_list:
        images_tag += ('<img src="%s" width="500" />' % image)
        
    html_content = html_content.replace("/files", "https://www.nogizaka46.com/files")
    html_str = '<!DOCTYPE html><html><head><meta charset="utf-8"><title></title></head><body><h1>%s:</h1>%s'  \
        '<p>------------------------------标题-----------------------------</p>%s'  \
        '<p>------------------------------正文-----------------------------</p>%s'     \
        '</body></html>' % (ouline, images_tag, title, html_content)

    return html_str


def save_img_from_url(url, filepath, desc) -> list:
    list = []
    imganalysis = Imager()
    img = imganalysis.Analysis(url)
    # article = imganalysis.find_blog_article(url)
    # 迭代列表img,将图片保存在当前目录下
    x = 0
    download = Loader()
    for i in img:
        filename = (filepath + '/%s-%s.jpg') % (desc, x)
        download.Down('https://www.nogizaka46.com' + i, filename)
        x += 1
        list.append('https://www.nogizaka46.com' + i)

    return list




def poll_blog_attr():
    
    while True:
        global datestr, title
        time.sleep(g_qry_interval)
        try:
            logger.info(f"try get snapshot")
            get_latest_release_from_blog_main_page(url)
        except BaseException as e:
            traceback.print_exc()
            logger.error(f"encounter exception: {e}")
            time.sleep(g_qry_interval)


if __name__ == '__main__':
    set_logger()
    logger.info(f"开始运行乃木坂blog更新提醒工具， 图片保存位置为{g_image_save_dir}, BLOG原文保存位置为{g_blog_save_dir}, 查询间隔为{g_qry_interval}秒")
    datestr, title, href, thumb, member, desc, html_content = get_latest_release_from_blog_main_page(url)
    init_context = gen_blog_content(datestr, title, href, thumb, member)
    logger.info(f"初始状态为: {init_context}")
    
    image_list = save_img_from_url(href, g_image_save_dir, desc)
    save_blog_from_html_content(desc, html_content)
    

    poll_blog_attr()
