# 2023.3.13 
# L0nelyC1ty,SummerOne
# 获取补天src

import requests, json, time, os, csv
from bs4 import BeautifulSoup

Cookie = 'your_cookie'
headers = {
    'Origin': 'https://www.butian.net',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    'Host': 'www.butian.net',
    'Origin': 'https://www.butian.net',
    'Referer': 'https://www.butian.net/Reward/plan',
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

# 获取总页数
print("\033[1;32m[+]正在获取总页数...\033[0m")
try:
    res = requests.post('https://www.butian.net/Reward/pub',
                        headers=headers,
                        timeout=10)
    result = json.loads(res.text)
    total = result['data']['count']
except Exception:
    print("\033[1;31m[-]总页数获取失败\033[0m")
    os._exit(0)
print("\033[1;32m[+]总页数：{0}\033[0m".format(total))

# 获取所有company_id
try:
    companyId = []
    for i in range(1, total + 1):
        print("\033[1;33m{0}/{1} 正在获取company_id\033[0m".format(i, total))
        time.sleep(1)
        data = {'s': 1, 'p': i, 'token': ''}
        res = requests.post('https://www.butian.net/Reward/pub',
                            headers=headers,
                            data=data,
                            timeout=10)
        result = json.loads(res.text)
        list = result['data']['list']
        for item in list:
            companyId.append(item['company_id'])
except Exception:
    print("\033[1;31m[-]company_id获取失败\033[0m")
    os._exit(0)
    
print("\033[1;32m[+]company_id获取完毕，共{0}个\033[0m".format(len(companyId)))
headers = {
    'Host': 'www.butian.net',
    'User-Agent':
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cookie': Cookie
}

# 获取所有URL
print("\033[1;32m[+]正在获取url...\033[0m")
with open("butian.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    #writer.writerow(['url', 'name'])
    total = len(companyId)
    for i in range(len(companyId)):
        params = {'cid': companyId[i]}
        try:
            time.sleep(1)
            res = requests.get('https://www.butian.net/Loo/submit',
                               headers=headers,
                               params=params,
                               timeout=10)
        except Exception:
            print("\033[1;31m[-]{0}/{1} companyId{2}:获取失败\033[0m".format(
                i + 1, total, companyId[i]))
            continue
        result = BeautifulSoup(res.text, 'lxml')
        url = result.find(name='input', attrs={'name': 'host'}).attrs['value']
        company_name = result.find(name='input',
                                   attrs={
                                       'name': 'company_name'
                                   }).attrs['value']
        # 写入文件
        print("\033[1;33m{0}/{1} {2} {3}\033[0m".format(i + 1, total, url, company_name))
        writer.writerow([url, company_name])

print("\033[1;32m[+]执行完毕，文件保存在./butian.csv\033[0m")
