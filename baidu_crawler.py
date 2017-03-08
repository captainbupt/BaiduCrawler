# -*- coding:utf-8 -*-
import sys
import requests
from lxml import etree
import random
import ip_pool
import re
import json
from optparse import OptionParser

reload(sys)
sys.setdefaultencoding('utf-8')

"""
================================================
 Extract text from the result of BaiDu search
================================================
"""


def download_html(keywords, proxy=None, page=1):
    """
    download html

    Parameters
    ---------
    page: the page number
    keywords: keywords need to be search.
    proxy: an ip with port.

    Returns
    ------
    utf8_content: the web content encode in utf-8.

    """
    key = {'wd': keywords, 'pn': (page - 1) * 10}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'}
    web_content = requests.get("http://www.baidu.com/s?", params=key, headers=headers, proxies=proxy, timeout=4)
    content = web_content.text
    return content


def url_parser(url, proxy=None):
    """
    transfer baidu's url to real url

    Parameters
    ---------
    url: baidu's url(http://www.baidu.com/link?url=***)
    proxy: an ip with port.

    Returns
    ------
    real_url: The real url.

    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'}
    web_content = requests.get(url, headers=headers, proxies=proxy, timeout=4)
    return web_content.url


def html_parser(html, proxy=None):
    """
    web parser

    Parameters
    ----------
    html: the web html.

    Returns
    -------
    text: the whole text of the search results.
    times: the times that key word hits.

    """
    tree = etree.HTML(html)
    items = tree.xpath("//div[@id='content_left']//div[contains(@class,'c-container')]")
    parse_result_list = []
    for item in items:
        content = ''
        date = ''
        url = ''

        abstracts = item.xpath(".//div[@class='c-abstract']")
        for abstract in abstracts:
            for child in abstract.xpath(".//text()"):
                pattern = re.compile(r'^([\d]{1,4}年[\d]{1,2}月[\d]{1,2}日).*-.*$')
                match = pattern.match(str(child))
                if match:
                    date = match.group(1)
                    continue
                content += child

        hrefs = item.xpath(".//a[@class='c-showurl']")
        for href in hrefs:
            url = url_parser(href.get('href'), proxy)

        if len(content) <= 0:
            continue

        parse_result = {'content': content, 'date': date, 'url': url}

        parse_result_list.append(parse_result)
    return parse_result_list


def extract_all_text(keyword, page, result_text):
    """
    ========================================================
    Extract all text of elements in company dict
    There are 3 strategies:
        1. Every time appears "download timeout", I will choose another proxy.
        2. Every 200 times after I crawl, change a proxy.
        3. Every 2000,0 times after I crawl, Re-construct an ip_pool.

    ========================================================
    Parameters
    ---------
    keyword: the keyword name dict.
    page: the max page to search
    result_text: file that save all text.

    Return
    ------
    """

    with open(result_text, 'w') as rt:
        flag = 0  # Change ip
        switch = 0  # Change the proxies list
        useful_proxies = []
        new_ip = ''
        for i in range(1, page):
            if switch % 20000 == 0:
                switch = 1
                ip_list = ip_pool.get_all_ip(1)
                useful_proxies = ip_pool.get_the_best(1, ip_list, 1.5, 20)
            switch += 1
            try:
                if flag % 200 == 0 and len(useful_proxies) != 0:
                    flag = 1
                    rd = random.randint(0, len(useful_proxies) - 1)
                    new_ip = useful_proxies[rd]
                    print(new_ip)
                flag += 1
                proxy = {'http': 'http://' + new_ip}
                content = download_html(keyword, proxy, i)
                results = html_parser(content, proxy)
                for result in results:
                    print json.dumps(result)
                    rt.write(result['content'] + ',' + result['date'] + ',' + result['url'] + '\n')
            except Exception as e:
                rd = random.randint(0, len(useful_proxies) - 1)
                new_ip = useful_proxies[rd]
                print 'download error: ', e


def main():
    result_text = 'data/results.txt'
    extract_all_text('e袋洗', 10, result_text)


if __name__ == '__main__':
    main()
