# -*- coding: utf-8 -*-
# File  : IpPool.py
# Author: HuangXin
# Date  : 2022/7/22

import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib3


class IpPool(object):
    def __init__(self):
        """
            now_time:当前时间
            url:代理网站
            test_url：测试代理网站
            headers：请求头
        """
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()).split(" ", 2)
        date = now_time[0].replace("-", "/")
        hour = str(int(now_time[1].split(":", 3)[0]) - 1)
        # hour = str(int(now_time[1].split(":", 3)[0]))
        if len(hour) < 2:
            hour = "0" + hour
        self.url = "https://ip.ihuan.me/today/" + date + "/" + hour + ".html"
        print(self.url)
        self.test_url = 'http://icanhazip.com/'
        ua = UserAgent()
        self.headers = {
            'user-agent': ua.random
        }
        self.ip_list = []

    def ip_test(self, ip):
        """
            测试IP是否可用
        """
        proxy = {"http": ip}
        try:
            response = requests.get(self.test_url, headers=self.headers, proxies=proxy, timeout=0.5)
            if response.status_code == 200:
                return 1
            else:
                return 0
        except Exception as e:
            pass
            # print(e)

    def get_html(self):
        """
            获得代理网站HTML
        """
        # 代理请求
        # proxy_list = [
        #     {"http": "139.9.64.238:443"},
        #     {"http": "61.183.234.226:9091"},
        #     {"http": "110.189.88.20:9091"},
        #     {"http": "183.250.163.175:9091"},
        #     {"http": "123.56.175.31:3281"}
        # ]
        # for proxy in proxy_list:
        #     try:
        #         response = requests.get(self.url, headers=self.headers, proxies=proxy)
        #         # response = requests.get(self.url, headers=self.headers, timeout=5)
        #         print(response)
        #         if response.status_code == 200:
        #             return response.text
        #     except Exception as e:
        #         pass

        # 本机代理请求
        try:
            urllib3.disable_warnings()
            proxy = {"https": "127.0.0.1:10001"}
            response = requests.get(self.url, headers=self.headers, proxies=proxy, verify=False, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(e)

        # 无代理请求
        # try:
        #     urllib3.disable_warnings()
        #     response = requests.get(self.url, headers=self.headers, verify=False, timeout=10)
        #     if response.status_code == 200:
        #         return response.text
        # except Exception as e:
        #     print(e)

    def get_infos(self, html):
        """
            从页面数据提取IP
        """
        html = BeautifulSoup(html, "html.parser")
        ranks = html.select('.col-md-10 > div > div > p')
        result = str(ranks[0]).replace('<p class="text-left">', '').replace('</p>', '').strip().split("<br/>")
        if len(result) != 0:
            print("检测代理中...")
            for i in result[:20]:
                if ":" in i:
                    ip = i.split("@")[0]
                    a = IpPool.ip_test(self, ip)
                    if a == 1:
                        if ip not in self.ip_list:
                            self.ip_list.append(ip)
                            # print(ip, "有用")
                    else:
                        pass
                        # print(ip, "无用")
            return self.ip_list
        else:
            print("无可用代理")
            return self.ip_list

    def get_ip(self):
        """
            入口
        """
        print("获取代理中...")
        html = IpPool.get_html(self)
        # print(html)
        if html is None:
            print("无可用代理")
            return self.ip_list
        else:
            IpPool.get_infos(self, html)
            ip_num = str(len(self.ip_list[:10]))
            print("共获取到" + ip_num + "个IP")
            # print(ip_list)
            return self.ip_list[:10]


if __name__ == '__main__':
    spider = IpPool()
    ip_list = spider.get_ip()
    print(ip_list)
