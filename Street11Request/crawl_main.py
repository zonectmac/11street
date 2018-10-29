import threading
import requests
import json
from bs4 import BeautifulSoup
import html_outputer
import html_parser
import html_downloader
import re
from urllib.parse import quote, urlencode
import time
import traceback
import queue
import os, sys
# import pandas as pd
from xlwt import Workbook, XFStyle, Font

detail_urls = set()


class DownPageUrl(threading.Thread):
    def __init__(self, keyword, page_num):
        threading.Thread.__init__(self)
        self.page_num = page_num
        self.keyword = keyword

    def run(self):
        p_url = self.get_url(self.page_num, self.keyword)
        data = requests.get(p_url).content.decode('utf-8')
        json_data = json.loads(data)
        soup = BeautifulSoup(json_data['template'])
        links = soup.find_all('a', href=re.compile(r'/product/*?'))  # 获得新网页内所有RUL
        for link in links:
            new_link = link['href']
            if new_link is None:
                return
            if new_link not in detail_urls:
                detail_urls.add(new_link)

    # offset页数 category关键词
    def get_url(self, offset, category):
        if '%' in category:
            category = category
        else:
            category = quote(category)
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
            'kwd': category,
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
        print(base_url)
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
            for i_index, n_url in enumerate(c_urls):
                print('craw %s : %s' % (str(self.count) + '_' + str(i_index), n_url))
                html_cont = self.downloader.download(n_url)
                new_data = self.parser.parser(n_url, html_cont)
                # print(new_data)
                self.outputer.write_txt(str(new_data))
                # self.outputer.collect_data(new_data)
            # 释放锁
            threadLock.release()
        except:
            print(traceback.print_exc())
            print('craw failed')


class Spider(object):
    def __init__(self, keyword, pages):
        self.keyword = keyword
        self.pages = pages

    def crawl(self):
        threads_1 = []
        for i in range(self.pages):
            t = DownPageUrl(self.keyword, i + 1)
            t.start()
            threads_1.append(t)
            time.sleep(0.1)
        for tt in threads_1:
            tt.join()
        print(len(detail_urls), detail_urls)
        threads_2 = []
        url_t = []
        for index, url in enumerate(detail_urls):
            url_t.append(url)
            if (index + 1) % 2 == 0:
                t = DownloadParse(index, url_t)
                threads_2.append(t)
                t.start()
                time.sleep(0.1)
                url_t.clear()
        # 等待所有线程完成
        for t_2 in threads_2:
            t_2.join()


class WriteCSV(object):
    def get_ags_run(self):
        # 获取当前文件夹
        dir_path = os.path.split(os.path.realpath(__file__))[0]
        print(dir_path)
        files = os.listdir(dir_path)
        file = ''
        args = []
        for tmp in files:
            if os.path.exists(dir_path + "\\" + tmp) and os.path.isfile(dir_path + "\\" + tmp):
                if os.path.splitext(tmp)[1] == '.txt':
                    file = tmp
                    if '_' in tmp:
                        inde = tmp.index('.')
                        args = tmp[:inde].split('_')
                    else:
                        with open(file) as f:
                            for line in f.readlines():
                                print(line.strip('\n'))
                                args.append(line.strip('\n'))
                    break
        u_link = args[0]
        if 'http' in u_link:
            Spider(u_link[u_link.index('=') + 1:].replace('25', ''), int(args[1])).crawl()
        else:
            Spider(args[0], int(args[1])).crawl()
        os.remove(file)

    def write_csv(self):

        title = []
        sale_price = []
        describe_num = []
        link = []
        collection_num = []
        qa_num = []
        mark = []
        all_clonum = []
        with open('output.txt', 'rb') as f:
            for line in f.readlines():
                line = line.decode('utf-8').strip('\n')
                json_data = eval(line)
                title.append(json_data['title'])
                sale_price.append(json_data['sale_price'])
                describe_num.append(json_data['describe_num'])
                link.append(json_data['link'])
                collection_num.append(json_data['collection_num'])
                qa_num.append(json_data['qa_num'])
                mark.append(json_data['mark'])

        # # 任意的多组列表
        # # 字典中的key值即为csv中列名
        # dataframe = pd.DataFrame({'title': title, 'sale_price': sale_price, 'describe_num': describe_num,
        #                           'collection_num': collection_num, 'qa_num': qa_num, 'mark': mark, 'link': link})
        #
        # # 将DataFrame存储为csv,index表示是否显示行名，default=True
        # dataframe.to_csv("test.csv", index=False, sep=',', encoding="utf_8_sig")

        all_clonum.append(title)
        all_clonum.append(sale_price)
        all_clonum.append(describe_num)
        all_clonum.append(collection_num)
        all_clonum.append(qa_num)
        all_clonum.append(mark)
        all_clonum.append(link)
        ti = ['Title', 'Sale_price', 'Describe_num', 'Collection_num', 'Qa_num', 'Mark', 'Link']
        book = Workbook()
        sheet1 = book.add_sheet('Sheet 1')
        row0 = sheet1.row(0)
        for i in range(7):
            sheet1.col(i).width = 3000 * 3
            row0.write(i, ti[i], self.set_style(True))
        for index, clonum in enumerate(all_clonum):
            for index2, c in enumerate(clonum):
                row = sheet1.row(index2 + 1)
                row.write(index, c)

        book.save('output.csv')

        os.remove('output.txt')

    def set_style(self, isblod):
        style = XFStyle()
        fnt = Font()  # 创建一个文本格式，包括字体、字号和颜色样式特性
        fnt.name = u'微软雅黑'  # 设置其字体为微软雅黑
        fnt.bold = isblod
        style.font = fnt
        return style


if __name__ == '__main__':
    start = time.time()
    wc = WriteCSV()
    wc.get_ags_run()
    wc.write_csv()
    # Spider('가습기', 5).crawl()
    end = time.time()
    print(end - start)
