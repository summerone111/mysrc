#2023.3.13
#Author:SummerOne
#获取漏洞盒子src

import requests, json, time, os, csv

url = "https://user.vulbox.com/api/hacker/bugs/business?page=1&per_page=50"
Cookie = 'your cookie'
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    'Host': 'user.vulbox.com',
    'Referer': 'https://user.vulbox.com/management/submit/72',
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': Cookie
}

print("\033[1;32m[+]正在获取待爬取数据量...\033[0m")
try:
    res = requests.get(url,
                        headers=headers,
                        timeout=10)
    result = json.loads(res.text)
    #print(result)
    total_page = result['data']['last_page']
    total = result['data']['total']
except Exception:
    print("\033[1;31m[-]数据获取失败\033[0m")
    os._exit(0)
print("\033[1;32m[+]总页数：{0}\033[0m".format(total_page))
print("\033[1;32m[+]总数目：{0}\033[0m".format(total))


with open("vulbox.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    #writer.writerow(['url', 'name'])
    for i in range(1,int(total_page)+1):
        time.sleep(1)
        print("\033[1;33m{0}/{1} 正在获取厂商数据...\033[0m".format(i, total_page))
        url = "https://user.vulbox.com/api/hacker/bugs/business?page="+str(i)+"&per_page=50"
        try:
            res = requests.get(url,
                                headers=headers,
                                timeout=10)
            result = json.loads(res.text)
            datas = result['data']['data']
            for item in datas:
                bus_url = item['bus_url']
                bus_name = item['bus_name']
                # 写入文件
                print("\033[1;33m {0} {1}\033[0m".format( bus_url, bus_name))
                writer.writerow([bus_url, bus_name])
        except Exception:
            print("\033[1;31m[-]{0}/{1}:获取失败\033[0m".format(i , total_page))
            continue

print("\033[1;32m[+]执行完毕，文件保存在./vulbox.csv\033[0m")


