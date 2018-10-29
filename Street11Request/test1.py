import url_manager
import html_parser
import html_downloader
import html_outputer
from urllib.parse import quote, urlencode
import requests, json, re
from bs4 import BeautifulSoup
import traceback
import time
import threading


class Spider(object):
    def __init__(self):
        self.urls = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()

    # 爬取产品信息
    def crwal_list(self, keyword, pagenum):
        url = self.get_url(keyword, pagenum)
        data = requests.get(url).content.decode('utf-8')
        jsondata = json.loads(data)
        soup = BeautifulSoup(jsondata['template'])
        links = soup.find_all('a', href=re.compile(r'/product/*?'))  # 获得新网页内所有RUL
        for link in links:
            new_link = link['href']
            self.urls.add_new_url(new_link)

    def craw_detail(self):
        threads = []
        all_urls = self.urls.get_all_url()
        url_t = []
        for index, url in enumerate(all_urls):
            url_t.append(url)
            if (index + 1) % 2 == 0:
                t = DownloadParse(index, url_t)
                threads.append(t)
                t.start()
                time.sleep(0.1)
                url_t.clear()

        # 等待所有线程完成
        for t in threads:
            t.join()
            # self.outputer.output_html()


class DownPageUrl(threading.Thread):
    def __init__(self, pagenum, keyword):
        threading.Thread.__init__(self)
        self.pagenum = pagenum
        self.keyword = keyword
        self.urls = url_manager.UrlManager()

    def run(self):
        url = self.get_url(self.pagenum, self.keyword)
        data = requests.get(url).content.decode('utf-8')
        jsondata = json.loads(data)
        soup = BeautifulSoup(jsondata['template'])
        links = soup.find_all('a', href=re.compile(r'/product/*?'))  # 获得新网页内所有RUL
        for link in links:
            new_link = link['href']
            self.urls.add_new_url(new_link)

    # offset页数 category关键词
    def get_url(self, offset, category):
        params = {
            'method': 'getSearchFilterAjax',
            'filterSearch': 'Y',
            'pageLoadType': 'ajax',
            'selectedFilterYn': 'Y',
            'ab': 'B',
            'version': 1.2,
            'sellerNos': '',
            'pageNo': 2,
            'dispCtgrLevel': 0,
            'brandNm': '',
            'fromPrice': 0,
            'toPrice': 0,
            'reSearchYN': 'N',
            'kwd': quote(category),
            'excptKwd': '',
            'pageNum': offset,
            'pageSize': 60,
            'researchFlag': 'false',
            'lCtgrNo': 0,
            'mCtgrNo': 0,
            'sCtgrNo': 0,
            'dCtgrNo': 0,
            'prdType': 'S',
            'prdTab': 'T',
            'selMthdCd': '',
            'targetTab': 'T',
            'viewType': 'L',
            'minPrice': 0,
            'maxPrice': 0,
            'custBenefit': '',
            'dlvType': '',
            'previousKwd': '',
            'previousExcptKwd': '',
            'goodsType': '',
            'buySatisfy': '',
            'sortCd': 'NP',
            'version': 1.2,
            'selectedCtgrNoList': '',
            'ctgrNoDepth': '',
            'myPrdViewYN': 'Y',
            'sellerCreditGradeType': [],
            'totalCount': 35516,
            'kwdInCondition': '',
            'isPremiumItem': '',
            'partnerSellerNos': '',
            'partnerFilterYN': '',
            'dealPrdYN': '',
            'brdParam': '',
            'version': 1.2,
            'catalogYN': 'N',
            'brandCd': '',
            'attributes': '',
            'imgAttributes': '',
            'benefits': '',
            'verticalType': '',
            'dispCtgrNo': '',
            'dispCtgrType': '',
            'engineRequestUrl': ''
        }
        base_url = 'http://search.11st.co.kr/Search.tmall?' + urlencode(
            params) + '&method=getTotalSearchSeller'  # 字典key不能重复 这里拼接下
        return base_url


class DownloadParse(threading.Thread):
    def __init__(self, count, urls):
        threading.Thread.__init__(self)
        self.count = count
        self.urls = urls
        self.downloader = html_downloader.HtmlDownloader()
        self.parser = html_parser.HtmlParser()
        self.outputer = html_outputer.HtmlOutputer()

    def run(self):
        try:
            c_urls = []
            for u in self.urls:
                c_urls.append(u)
            threadLock = threading.Lock()
            # 获得锁，成功获得锁定后返回True
            # 可选的timeout参数不填时将一直阻塞直到获得锁定
            # 否则超时后将返回False
            threadLock.acquire()
            for index, url in enumerate(c_urls):
                print('craw %s : %s' % (str(self.count) + '_' + str(index), url))
                html_cont = self.downloader.download(url)
                new_data = self.parser.parser(url, html_cont)
                print(new_data)
                self.outputer.write_txt(str(new_data))
                # self.outputer.collect_data(new_data)
            # 释放锁
            threadLock.release()
        except:
            print(traceback.print_exc())
            print('craw failed')


if __name__ == "__main__":
    # root_url = "http://baike.baidu.com/item/Python"
    start = time.time()
    obj_spider = Spider()
    obj_spider.crwal_list('가습기', 2)
    # obj_spider.craw_detail()
    obj_spider.craw_detail2()
    end = time.time()
    print(end - start)
