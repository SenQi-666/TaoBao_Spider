from Header import UAPool
from conf.Settings import *
import pandas as pd
import requests
import pymongo
import json
import time
import re


class TaoBao:
    def __init__(self, login_id, password2, ua2):
        self.LoginId = login_id
        self.PassWord2 = password2
        self.Ua2 = ua2
        self.LoginURL = 'https://login.taobao.com/member/login.jhtml'
        self.SpiderURL = 'https://s.taobao.com/search?q={}&s={}'
        self.HEADERS = {
            'user-agent': self.UA,
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://login.taobao.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
        self.UA = UAPool().get_header()
        self.PROXY = requests.get('http://114.55.137.192:8000/random').text
        self.SESSION = requests.session()

    def login_form(self):
        response = requests.get(self.LoginURL, headers={'user-agent': self.UA})
        res_dict = json.loads(re.findall('window.viewData = (.*?);', response.text)[0])
        csrf_token = res_dict['loginFormData']['_csrf_token']
        umid_token = res_dict['loginFormData']['umidToken']
        hsiz = res_dict['loginFormData']['hsiz']
        return csrf_token, umid_token, hsiz

    def login_request(self):
        sendinfo_url = 'https://login.taobao.com/newlogin/login.do?appName=taobao&fromSite=0'
        csrf_token, umid_token, hsiz = self.login_form()
        data = {
            'loginId': str(self.LoginId),
            'password2': self.PassWord2,
            'keepLogin': 'false',
            'ua': self.Ua2,
            'umidGetStatusVal': '255',
            'screenPixel': '1440x900',
            'navlanguage': 'zh-CN',
            'navUserAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
            'navPlatform': 'MacIntel',
            'appName': 'taobao',
            'appEntrance': 'taobao_pc',
            '_csrf_token': csrf_token,
            'umidToken': umid_token,
            'hsiz': hsiz,
            'bizParams': '',
            'style': 'default',
            'appkey': '00000000',
            'from': 'tb',
            'isMobile': 'false',
            'lang': 'zh_CN',
            'returnUrl': '',
            'fromSite': '0'
        }

        response = self.SESSION.post(sendinfo_url, headers=self.HEADERS, data=data, verify=False)
        async_url = response.json()['content']['data']['asyncUrls'][0]
        return async_url

    def st_login(self):
        alibaba_url = self.login_request()
        response = self.SESSION.post(alibaba_url, headers=self.HEADERS, verify=False)
        if response.status_code == 200:
            print('交换ST码成功')
        else:
            print('交换ST码失败')

    def get_user(self):
        login_verify_url = 'https://i.taobao.com/my_taobao.htm'
        response = self.SESSION.get(login_verify_url, headers=self.HEADERS, verify=False)
        username = re.findall('input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)[0]
        return username

    def parse(self, keyword):
        user = self.get_user()
        if user:
            page_num = 0
            print('欢迎用户：%s，您已登陆，骚呢！' % user)
            while page_num <= 100:
                if page_num >= 5:
                    self.HEADERS['user-agent'] = UAPool().get_header()
                    self.PROXY = requests.get('http://114.55.137.192:8000/random').text
                url = self.SpiderURL.format(keyword, page_num * 44)
                print('开始抓取第 %s 页商品信息' % page_num)
                try:
                    response = self.SESSION.get(url, headers=self.HEADERS,
                                                proxies={self.PROXY.split('://')[0]: self.PROXY},
                                                verify=False, timeout=5)
                    global_info = re.findall('g_page_config = (.*?)};', response.text)[0] + '}'
                    goods_list = json.loads(global_info)['mods']['itemlist']['data']['auctions']
                    info_lst = []
                    for item in goods_list:
                        goods_detail = re.sub('<span class=H>|</span>', '', item['title'])
                        goods_price = int(float(item['view_price']))
                        goods_sales = self.reformat_sales(item['view_sales'])
                        shop_name = item['nick']
                        shop_addr = item['item_loc']
                        goods_pic = 'https:' + item['pic_url']
                        goods_url = 'https:' + item['detail_url']
                        print('商品：%s  价格：%s  销量：%s  店铺名称：%s  店铺地址：%s  商品图片：%s  商品主页：%s' % (
                            goods_detail, goods_price, goods_sales, shop_name, shop_addr, goods_pic, goods_url
                        ))

                        goods_dict = {
                            '商品详情': goods_detail,
                            '商品价格': goods_price,
                            '商品销量': goods_sales,
                            '店铺名称': shop_name,
                            '店铺地址': shop_addr,
                            '商品图片': goods_pic,
                            '商品主页': goods_url
                        }
                        info_lst.append(goods_dict)
                        time.sleep(0.5)

                    self.save_mongo(info_lst)
                    page_num += 1
                    print('第 %s 页商品信息抓取完成' % page_num)
                    time.sleep(5)
                except Exception as e:
                    print(e)

            print('商品信息全部抓取完成')

    def reformat_sales(self, sale):
        sale = re.sub(r'人付款|[+]', '', sale)
        if '万' in sales:
            sales = float(re.sub(r'万', '', sales)) * 10000
        return int(sales)

    def save_mongo(self, info_lst):
        self.Collection.insert_many(info_lst)

    def run(self, keyword):
        print('开始尝试登陆，并交换ST码')
        self.st_login()
        self.parse(keyword)


if __name__ == '__main__':
    TaoBao(TaoBaoUSER, EncryPWD, EncryUA).run(KEYWORD)

