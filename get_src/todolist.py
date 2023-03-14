# -*- coding: utf-8 -*-
#2023.3.14
#Author:SummerOne
#读取各csv文件中的url，输出域名及ip对应文件、主域名文件和ip去重待扫描文件。

import csv
import tldextract
import socket

urls = []
iplist = []
domainlist = []

def dowith_urls():
    i = 0
    #print("\033[1;32m[+]开始进行域名-->IP地址转换...\033[0m")
    with open("domain_ip.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        for url in urls:
            i += 1
            url = url.strip()
            # 数据清洗
            if ':' in url:
                if url.startswith('http'):
                    domain = url.split(':')[1][2:]
                else:
                    domain = url.split(':')[0]
            else:
                domain = url
            
            try:
                # 域名转换为IP地址
                ip_address = socket.gethostbyname(domain)
                writer.writerow([domain, ip_address])
                iplist.append(ip_address)
                
            except socket.gaierror:
                #print("\033[1;31m[-]{0} 解析失败\033[0m".format(domain))
                ip_address = ''

            # 提取主域名
            tld = tldextract.extract(domain)
            main_domain = tld.domain + '.' + tld.suffix
            domainlist.append(main_domain)

            print("\033[1;34m[{}] {:<30}{:<30}{:<30}\033[0m".format(i,domain,ip_address,main_domain))

# with open("butian.csv", "r") as f:
#     reader = csv.reader(f)
#     for row in reader:
#         url = row[0]
#         if(url):
#             urls.append(url)

# with open("vulbox.csv", "r") as f:
#     reader = csv.reader(f)
#     for row in reader:
#         url = row[0]
#         if(url):
#             urls.append(url)

with open("aizhantop.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        url = row[0]
        if(url):
            urls.append(url)

dowith_urls()
iplist = list(set(iplist))
domainlist = list(set(domainlist))

with open("ip.txt",'w') as f:
    for ip in iplist:
        f.write(ip+'\n')
    f.close()

with open("main_domain.txt",'w') as f:
    for domain in domainlist:
        f.write(domain+'\n')
    f.close()

print("\033[1;32m[+]执行完毕，文件保存在./domian_ip.csv ,./ip.txt, ./main_domain.txt\033[0m")