import requests
import random
import user_headers
from tomorrow import threads
from requests.adapters import HTTPAdapter
import queue
import traceback
import time


# python3中是用urllib.request.urlopen()
class HtmlDownloader(object):
    def download(self, new_url, retries=3):
        headers = {'user-agent': random.choice(user_headers.agents)}
        if new_url is None:
            return None
        s = requests.session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        try:
            response = s.get(new_url, headers=headers, timeout=10)
        except:
            print(traceback.print_exc())
            if retries > 0:
                time.sleep(0.5)
                return self.download(new_url, retries=retries - 1)
            else:
                print('download Failed')
                return None
        if response.status_code != 200:
            print('failed')
            return None
        data = response.text
        return data


if __name__ == '__main__':
    response = requests.get(
        'http://deal.11st.co.kr/product/SellerProductDetail.tmall?method=getSellerProductDetail&prdNo=1378635512&trTypeCd=20&trCtgrNo=585021')
    print(response.text)
