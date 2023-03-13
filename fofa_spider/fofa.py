#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/9/14 22:20
# @Author  : Cl0udG0d
# @File    : fofa.py
# @Github: https://github.com/Cl0udG0d
from datetime import datetime
from datetime import timedelta
import base64
import time
from urllib.parse import quote_plus
import config

from tookit import unit, fofa_useragent
import argparse

from tookit.levelData import LevelData
from tookit.outputData import OutputData

host_list = []
timestamp_list = []

filename=""

# 账户指针
ACCOUNT_INDEX=0





import re, requests

from lxml import etree



class Fofa:
    headers_use=""
    level=0

    def __init__(self):
        self.want_page = None
        self.session = requests.session()
        print('''
         ____  ____  ____  ____      
        | ===|/ () \| ===|/ () \     
        |__|  \____/|__| /__/\__\    
             _   _   ____   ____  __  __ 
            | |_| | / () \ / (__`|  |/  /
            |_| |_|/__/\__\\\\____)|__|\__\\ V{}
        '''.format(config.VERSION_NUM))

    def fofa_captcha(self, src):
        """
        识别FOFA登录界面验证码
        :param src:
        :return:
        """
        import ddddocr
        ocr = ddddocr.DdddOcr()

        captcha_api = f'https://i.nosec.org{src}'
        resp = self.session.get(url=captcha_api, headers=fofa_useragent.getFofaCaptchaHeaders())
        return ocr.classification(resp.content)

    def fofa_login(self, fofa_username, fofa_password):
        """
        使用FOFA账号密码进行登录
        :param fofa_username:
        :param fofa_password:
        :return:
        """
        print('[*] 尝试登录')
        TEMP_RETRY_NUM=0
        while TEMP_RETRY_NUM<config.MAX_LOGIN_RETRY_NUM:
            try:
                authen = self.session.get(url='https://i.nosec.org/login?service=https://fofa.info/f_login', headers=fofa_useragent.getFofaLoginHeaders())
                src = re.findall('class="rucaptcha-image" src="(.*?)"', authen.text)[0]

                captcha = self.fofa_captcha(src)
                authenticity_token = re.findall('"csrf-token" content="(.*?)" /', authen.text)[0]
                lt = re.findall('id="lt" value="(.*?)" /', authen.text)[0]
                data = {
                    'utf8': '%E2%9C%93',
                    'authenticity_token': authenticity_token,
                    'lt': lt,
                    'service': 'https://fofa.info/f_login',
                    'username': fofa_username,
                    'password': fofa_password,
                    '_rucaptcha': captcha,
                    'rememberMe': '1',
                    'button': '',
                    'fofa_service': '1',
                }
                user_login_api = 'https://i.nosec.org/login'
                res_login = self.session.post(url=user_login_api, data=data)
                if '登录验证码错误' in res_login.text:
                    print("[-] 验证码错误，重新运行脚本")
                    raise
                elif '用户名或密码错误' in res_login.text:
                    print('[-] 用户名或密码错误,请检查账户名和密码后重试')
                    raise
                elif '账号未激活' in res_login.text:
                    print('[-] 账号未激活，继续操作前请先确认激活您的帐号')
                    raise
                else:
                    # print(res_login.text)
                    print("[*] 登录成功")
                    tempstr = ''
                    for key, value in self.session.cookies.get_dict().items():
                        tempstr += key + "=" + value + "; "
                    # print(tempstr)
                    with open('fofa_cookie.txt', 'w') as f:
                        f.write(tempstr)
                    return self.session.cookies, 1
            except Exception as e:
                print("[-] error:{}".format(e))
                TEMP_RETRY_NUM+=1
                print('[-] 第{}次尝试登录'.format(TEMP_RETRY_NUM))
                pass
        print('[-] FOFA登录失败,即将切换账号进行尝试')
        raise

    def check_login(self, cookies):
        """
        检测cookie是否生效
        :param cookies:
        :return:
        """
        resp = requests.get(url='https://fofa.info/result?qbase64=MQ==&page=2&page_size=10', headers=fofa_useragent.getCheckHeaders(cookies))
        tree = etree.HTML(resp.text)
        urllist = tree.xpath('//span[@class="hsxa-host"]/a/@href')
        return len(urllist), cookies

    def cookie_info(self):
        """
        读取cookie
        :rtype: object
        """
        with open('fofa_cookie.txt', 'r') as f:
            cookies = f.read()
            return cookies if cookies!='' else ''

    def headers(self,cookie):
        headers_use = {
            'User-Agent': fofa_useragent.getFakeUserAgent(),
            'Accept': 'application/json, text/plain, */*',
            "cookie": cookie.encode("utf-8").decode("latin1")
        }
        return headers_use


    def init(self):
        parser = argparse.ArgumentParser(description='Fofa-hack v{} 使用说明'.format(config.VERSION_NUM))
        parser.add_argument('--timesleep', '-t', help='爬取每一页等待秒数,防止IP被Ban,默认为3',default=3)
        parser.add_argument('--keyword', '-k', help='fofa搜索关键字,默认为test', required=True)
        parser.add_argument('--username', '-u', help='fofa用户名')
        parser.add_argument('--password', '-p', help='fofa密码')
        parser.add_argument('--endpage', '-e', help='爬取结束页码')
        parser.add_argument('--level', '-l', help='爬取等级: 1-3 ,数字越大内容越详细,默认为 1')
        parser.add_argument('--output', '-o', help='输出格式:txt、json、csv,默认为txt')
        args = parser.parse_args()
        config.TimeSleep = int(args.timesleep)
        print("[*] 爬取延时: {}s".format(config.TimeSleep))
        config.SearchKEY = args.keyword
        print("[*] 爬取关键字: {}".format(config.SearchKEY))
        if args.username and args.password:
            config.fofa_account[0]["fofa_username"]=args.username
            config.fofa_account[0]["fofa_password"] = args.password
            print("[*] 使用账号: {}".format(args.username))
        elif args.username and not args.password:
            print("[-] 请输入 [ {} ] 账号对应密码".format(args.username))
            exit(0)
        elif args.password and not args.username:
            print("[-] 请输入账号")
            exit(0)
        if args.endpage:
            self.want_page=args.endpage
            print("[*] 爬取页码数: {}".format(self.want_page))
        self.level=args.level if args.level else "1"
        self.levelData=LevelData(self.level)


        self.output = args.output if args.output else "txt"
        print("[*] 输出格式为: {}".format(self.output))


        global filename
        filename = "{}.{}".format(config.SearchKEY,self.output)
        print("[*] 存储文件名: {}".format(filename))
        self.outputData = OutputData(filename, pattern=self.output)
        return

    def get_page_num(self, search_key,cookie):
        # 获取页码
        headers_use = fofa_useragent.getFofaPageNumHeaders(cookie)
        searchbs64 = base64.b64encode(f'{search_key}'.encode()).decode()
        print("[*] 爬取页面为:https://fofa.info/result?qbase64=" + searchbs64)
        html = requests.get(url="https://fofa.info/result?qbase64=" + searchbs64, headers=headers_use).text
        tree = etree.HTML(html)
        try:
            pagenum = tree.xpath('//li[@class="number"]/text()')[-1]
        except Exception as e:
            print("[-] error:{}".format(e))
            pagenum = '0'
            pass
        print("[*] 存在页码:" + pagenum)
        return searchbs64, headers_use

    def getTimeList(self, text):
        # 获取时间列表
        timelist = list()
        pattern = "<span>[0-9]*-[0-9]*-[0-9]*</span>"
        result = re.findall(pattern, text)
        for temp in result:
            timelist.append(temp.replace("<span>", "").replace("</span>", "").strip())
        return timelist

    def fofa_spider_page(self, page, search_key, searchbs64, headers_use, turn_num):
        """
        获取某一页内的URL数据
        :rtype: object
        """
        global host_list
        global timestamp_list
        TEMP_RETRY_NUM=0
        print("[*] 正在爬取第" + str(5 * int(turn_num) + int(page)) + "页")
        global ACCOUNT_INDEX
        while ACCOUNT_INDEX < len(config.fofa_account):

            while TEMP_RETRY_NUM < config.MAX_MATCH_RETRY_NUM:
                try:
                    request_url = 'https://fofa.info/result?qbase64=' + searchbs64 + '&full=false&page=' + str(
                        page) + "&page_size=10"
                    # print(f'request_url:{request_url}')
                    rep = requests.get(request_url, headers=self.headers_use)
                    self.levelData.startSpider(rep)

                    # tree = etree.HTML(rep.text)
                    # urllist = tree.xpath('//span[@class="hsxa-host"]/a/@href')
                    timelist = self.getTimeList(rep.text)
                    print("[*] 当页数据:"+str(self.levelData.formatData))

                    for i in self.levelData.formatData:
                        with open(filename, 'a+', encoding="utf-8") as f:
                            f.write(str(i) + "\n")
                    host_list.extend(self.levelData.formatData)
                    timestamp_list.extend(timelist)

                    time.sleep(config.TimeSleep)
                    return
                except Exception as e:
                    print("[-] error:{}".format(e))
                    TEMP_RETRY_NUM+=1
                    print('[-] 第{}次尝试获取页面URL'.format(TEMP_RETRY_NUM))
                    pass

            self.headers_use=self.refresh_cookie()

        print('[-] FOFA资源获取重试超过最大次数,程序退出')
        exit(0)



    def refresh_cookie(self):
        """
        当前获取不到数据的时候,该方法会重置cookie数据进行账号切换
        1.重置cookie文件
        2.切换账号重新获取cookie
        3.返回新的cookie以供爬取
        :return:
        """
        global ACCOUNT_INDEX
        while ACCOUNT_INDEX < len(config.fofa_account):
            username = config.fofa_account[ACCOUNT_INDEX]["fofa_username"]
            password = config.fofa_account[ACCOUNT_INDEX]["fofa_password"]
            # print("username:{};password:{}".format(username, password))
            try:
                if self.fofa_login(username, password)[1] == 1:
                    cookie=self.cookie_info()
                    return fofa_useragent.getFofaPageNumHeaders(cookie)
                raise
            except Exception as e:
                print("[-] error:{}".format(e))
                ACCOUNT_INDEX += 1
                if ACCOUNT_INDEX < len(config.fofa_account):
                    print("[*] 切换账号:{}".format(config.fofa_account[ACCOUNT_INDEX]["fofa_username"]))
                    pass
                else:
                    break
        print("[-] 账号无法登录,程序退出")
        exit(0)


    def getNewHeaders(self):
        cookie = self.cookie_info()
        return fofa_useragent.getFofaPageNumHeaders(cookie)


    def fofa_spider(self, search_key, searchbs64, headers_use):
        global host_list

        # start_page = input("[*] 请输入开始页码: ")
        if not self.want_page:
            self.want_page = input("[*] 请输入终止页码: ")
        if self.want_page==None:
            print("[+] 终止页码设置为默认值 20")
            self.want_page=20
        if int(self.want_page) <= 5 and int(self.want_page) > 0:
            stop_page = self.want_page
            for page in range(1, int(stop_page) + 1):
                self.fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num=0)
        elif int(self.want_page) > 5:
            if int(self.want_page) % 5 == 0:
                # start_page = start_page
                stop_page = 5
                for turn_num in range(int(int(self.want_page) / 5)):
                    global timestamp_list
                    # print('[*] 第 ' + str(turn_num + 1) + ' turn抓取')
                    timestamp_list.clear()
                    for page in range(1, int(stop_page) + 1):
                        self.fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num)

                    search_key_modify, searchbs64_modify = self.modify_search_url(search_key)
                    search_key = search_key_modify
                    searchbs64 = searchbs64_modify
            else:
                turn_sum = int(self.want_page) // 5
                page_last = int(self.want_page) % 5
                for turn_num in range(int(self.want_page) // 5):
                    # start_page = start_page
                    stop_page = 5
                    # print('[*] 第 ' + str(turn_num + 1) + ' turn抓取')
                    timestamp_list.clear()
                    for page in range(1, int(stop_page) + 1):
                        self.fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num)

                    search_key_modify, searchbs64_modify = self.modify_search_url(search_key)
                    search_key = search_key_modify
                    searchbs64 = searchbs64_modify
                for page in range(1, page_last + 1):
                    # print('[*] 第 ' + str(turn_num + 2) + ' turn抓取')
                    self.fofa_spider_page(page, search_key, searchbs64, headers_use, turn_num=turn_sum)
        else:
            print('[-] 输入错误')
            exit(0)
        return

    def modify_search_url(self, search_key):
        global timestamp_list
        # timestamp_length = len(timestamp_list)
        if timestamp_list[-1] == timestamp_list[0]:
            time_before = timestamp_list[-1].strip('\n').strip()
        else:
            time_last = timestamp_list[-1].split(' ')[0].strip('\n').strip()
            # print(time_last)
            time_last_time = datetime.strptime(time_last, "%Y-%m-%d").date()
            # print(str(time_last_time))
            time_before = (time_last_time - timedelta(days=1))
            # print('time_before' + str(time_before))
        if 'before' in search_key:
            search_key = search_key.split('&& before')[0]
            search_key = search_key.strip(' ')
            search_key = search_key + ' && ' + 'before="' + str(time_before) + '"'
        else:
            search_key = search_key + ' && ' + 'before="' + str(time_before) + '"'
        search_key_modify = search_key

        searchbs64_modify = quote_plus(base64.b64encode(search_key_modify.encode()))
        # print('[*] 搜索词： ' + search_key_modify)

        return search_key_modify, searchbs64_modify


    def run(self, cookie):

        searchbs64, self.headers_use = self.get_page_num(config.SearchKEY,cookie)
        self.fofa_spider(config.SearchKEY, searchbs64, self.headers_use)
        print('[*] 抓取结束，共抓取数据 ' + str(len(host_list)) + ' 条\n')

    def main(self):
        self.init()
        print('[*] 账户检测')
        urllist, cookie = self.check_login(self.cookie_info())
        if urllist == 0:
            print("[-] 未登录")
            global ACCOUNT_INDEX
            while ACCOUNT_INDEX < len(config.fofa_account):
                username=config.fofa_account[ACCOUNT_INDEX]["fofa_username"]
                password = config.fofa_account[ACCOUNT_INDEX]["fofa_password"]
                # print("username:{};password:{}".format(username,password))
                try:
                    if self.fofa_login(username,password)[1] == 1:
                        print('[*] 开始搜索')
                        self.run(self.cookie_info())
                        print('[*] 运行结束')
                        exit(0)
                except Exception as e:
                    print("[-] error:{}".format(e))
                    ACCOUNT_INDEX += 1
                    if ACCOUNT_INDEX < len(config.fofa_account):
                        print("[*] 切换账号:{}".format(config.fofa_account[ACCOUNT_INDEX]["fofa_username"]))
                        pass
                    else:
                        break
            print("[-] 账号无法登录,程序退出")
            exit(0)
        else:
            print('[*] 已登录')
            self.run(cookie)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()






if __name__ == '__main__':
    fofa = Fofa()
    fofa.main()
