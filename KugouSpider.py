# -*- coding: utf-8 -*-
# File  : KugouSpider.py
# Author: HuangXin
# Date  : 2022/7/22

import requests
import time
import re
import csv
from fake_useragent import UserAgent
from IpPool import IpPool
import urllib3
import pymysql
import datetime


class KugouSpider(object):
    def __init__(self):
        """
            华语新歌榜：http://mobilecdnbj.kugou.com/api/v3/rank/newsong?version=9108&plat=0&with_cover=1&pagesize=100&
                    type=1&area_code=1&page=1&with_res_tag=1'
            热歌榜模板：http://mobilecdnbj.kugou.com/api/v3/rank/song?version=9108&ranktype=2&plat=0&pagesize=100&
                    area_code=1&page=1&rankid=52144&with_res_tag=1
            酷狗TOP100：rankid=8888  （每天更新）
            抖音热歌榜：rankid=52144  （每周六更新）
            快手热歌榜：rankid=52767  （每天更新）
        """
        # 获取代理
        a = IpPool()
        self.ip_list = a.get_ip()
        # 数据接口
        self.url_list = [
            ['http://mobilecdnbj.kugou.com/api/v3/rank/newsong?version=9108&plat=0&with_cover=1&pagesize=100&type=1&'
             'area_code=1&page=1&with_res_tag=1', "酷狗华语新歌"],
            ['http://mobilecdnbj.kugou.com/api/v3/rank/song?version=9108&ranktype=2&plat=0&pagesize=100&area_code=1&'
             'page=1&rankid=52767&with_res_tag=1', "酷狗快手热歌"],
            ['http://mobilecdnbj.kugou.com/api/v3/rank/song?version=9108&ranktype=2&plat=0&pagesize=100&area_code=1&'
             'page=1&rankid=8888&with_res_tag=1', "酷狗TOP100"]
        ]
        # 随机UA
        ua = UserAgent()
        self.headers = {
            'user-agent': ua.random
        }
        # 数据库数据
        self.music_info = []
        # CSV数据
        self.music_info_csv = []

    def get_response_0(self, url):
        """
            本地请求页面数据
        """
        print("本地请求")
        try:
            urllib3.disable_warnings()
            proxy = {"http": "127.0.0.1:10001"}
            response = requests.get(url, headers=self.headers, proxies=proxy)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(e)

    def get_response_1(self, url):
        """
            代理请求页面数据
        """
        # 代理测试
        # proxy_list = [
        #     {"http": "116.62.16.154:8118"},
        #     {"http": "113.96.62.246:8081"},
        #     {"http": "183.27.250.246:8085"},
        #     {"http": "120.196.186.248:9091"},
        #     {"http": "61.145.111.9:443"}
        # ]
        # 判断代理数据为空，是则走本地请求
        if len(self.ip_list) == 0:
            response = spider.get_response_0(url)
            return response
        else:
            # 代理测试
            # for proxy in proxy_list:
            for ip in self.ip_list:
                proxy = {"http": ip}
                try:
                    response = requests.get(url, headers=self.headers, proxies=proxy, verify=False, timeout=10)
                    if response.status_code == 200:
                        print(proxy, "有效")
                        return response.text
                except Exception as e:
                    print(proxy, "无效")
                    print(e)
            time.sleep(3)

    def insert_mysql(self):
        """
            数据库存储
        """
        db = pymysql.connect(host='localhost', user='root', password='abc7811066', database='kugou_music')
        cursor = db.cursor()
        sql = "INSERT INTO music_info(排名,上次排名,歌名,歌手,会员,歌曲分类,更新时间) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        try:
            for i in self.music_info:
                data = tuple(i)
                cursor.execute(sql, data)
                db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            print("插入数据失败")
        db.close()

    def csv(self):
        """
            CSV存储
        """
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()).split(" ", 2)
        date = now_time[0].replace("-", "")
        fp = open('E://demo//pycharm//kugou_spider//data//' + '酷狗(' + date + ')' + '.csv', 'wt', newline='',
                  encoding='utf-8')
        writer = csv.writer(fp)
        writer.writerow(('排名', '上次排名', '歌名', '歌手', '会员', '歌曲分类', '更新时间'))
        for i in self.music_info_csv:
            data = tuple(i)
            writer.writerow(data)

    def get_music(self):
        """
            提取数据
        """
        # print(response)
        # 获取数据
        for urls in self.url_list:
            self.music_info = []
            url = urls[0]
            csv_name = urls[1]
            dt = datetime.datetime.now().strftime("%Y-%m-%d")
            response = spider.get_response_1(url)
            # 判断代理请求的结果，若无数据则走本地请求
            if response is None:
                response = spider.get_response_0(url)
            # 处理数据
            infos = re.findall('"filename":"(.*?)"', response)
            privilege = re.findall('"privilege":(\d+)', response)
            sort = re.findall('"sort":(\d+)', response)
            last_sort = re.findall('"last_sort":(\d+)', response)
            for i, j, m, n in zip(infos, privilege, sort, last_sort):
                song = i.split("-", 2)[1].strip()
                singer = i.split("-", 2)[0].strip()
                self.music_info.append([m, n, song, singer, j, csv_name, dt])
                self.music_info_csv.append([m, n, song, singer, j, csv_name, dt])
            spider.insert_mysql()
            print(csv_name, "SQL存储已完成")
            time.sleep(3)
        spider.csv()
        print("CSV存储已完成")


if __name__ == '__main__':
    spider = KugouSpider()
    spider.get_music()
