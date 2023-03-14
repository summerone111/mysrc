#2023.3.14
#Author:SummerOne
#获取爱站各类型top排名中，百度权重大于2的域名

import requests, csv, time
import re

def get_top(site_type,pageid,number):
    headers =  {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Host': 'top.aizhan.com',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    with open("aizhantop.csv", "a") as csvfile:
        writer = csv.writer(csvfile)
        #writer.writerow(['site', 'rank'])

        for i in range(pageid,pageid + number +1):
            time.sleep(1)
            print("\033[1;32m[+]{0}/{1}正在获取...\033[0m".format(i,pageid + number))
            if pageid == 1:
                url = "https://top.aizhan.com/top/"+site_type+"/"
            else:
                url = "https://top.aizhan.com/top/"+site_type+"/p"+str(i)+".html"
            try:
                res = requests.get(url,
                                    headers = headers,
                                    timeout = 10).text
                #print(res)
                for item in re.findall("/baidu/([^/]+)/[^>]*>([\d\-]*)</a>", res):
                    #print(item)
                    site = item[0]
                    rank = item[1]
                    if (rank != "-" and int(rank) > 1) or site_type in ['t41','t29','t37','t10']:
                        print("\033[1;33m{0}, rank: {1}\033[0m".format(site, rank))
                        writer.writerow([site, rank])
            except Exception:
                print("\033[1;31m[-]{0}/{1}:获取失败\033[0m".format(i,pageid + number))
                continue 


get_top("t3-487", 3, 60)
print("\033[1;32m[+]执行完毕，文件保存在./aizhantop.csv\033[0m")