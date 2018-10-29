import re
import urllib.parse
from bs4 import BeautifulSoup


class HtmlParser(object):
    def parser(self, new_url, html_cont):
        if new_url is None or html_cont is None:
            return
        # soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        soup = BeautifulSoup(html_cont, 'html.parser')
        new_data = self._get_new_data(new_url, soup)

        return new_data

    def _get_new_urls(self, new_url, soup):
        new_urls = set()
        # links = soup.find_all('a', href=re.compile(r"/item/\S"))
        # links = soup.find_all('a', href=re.compile(r"/item/\."))
        links = soup.find_all('a', href=re.compile(r'/item/*?'))  # 获得新网页内所有RUL
        for link in links:
            new_link = link['href']
            new_full_link = urllib.parse.urljoin(new_url, new_link)
            new_urls.add(new_full_link)
        return new_urls

    def _get_new_data(self, new_url, soup):
        res_data = {}
        res_data['link'] = new_url
        title_node = soup.find('div', class_="heading").find("h2")
        res_data['title'] = title_node.get_text()
        price = soup.find('strong', class_='sale_price')
        res_data['sale_price'] = price.get_text()
        work_boxs = soup.find(class_='prdc_workbox').find_all('strong')
        if len(work_boxs) == 4:
            res_data['mark'] = work_boxs[0].get_text()
            describe_num = ''.join(work_boxs[1].get_text().split())
            res_data['describe_num'] = describe_num
            res_data['collection_num'] = work_boxs[2].get_text()
        else:
            res_data['mark'] = ''
            describe_num = ''.join(work_boxs[0].get_text().split())
            res_data['describe_num'] = describe_num
            res_data['collection_num'] = work_boxs[1].get_text()
        qa_node = soup.find_all('a', class_='product_tab_item')[2].find('em')
        res_data['qa_num'] = qa_node.get_text()

        return res_data


if __name__ == '__main__':
    soup = BeautifulSoup(open('html/test.html'))
    head = soup.select('.heading h2')
    p = soup.find('strong', class_='sale_price').get_text()
    s = soup.find_all('a', class_='product_tab_item')
    print(s[2].find('em'))
