# -*- coding:utf-8 -*-
import sys
import requests
from lxml import etree
import random
import ip_pool
import re
import json
from optparse import OptionParser
import traceback

reload(sys)
sys.setdefaultencoding('utf-8')

"""
================================================
 Extract text from the result of BaiDu search
================================================
"""

user_agent_pool = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6',
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Mobile Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0'
    'Mozilla/5.0 (Macintosh;U;IntelMacOSX10_6_8;en-us) AppleWebKit/534.50 (KHTML,likeGecko) Version/5.1 Safari/534.50'
    'Mozilla/5.0 (Macintosh;IntelMacOSX10.6;rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
]


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
    # 抓取参数 https://www.baidu.com/s?wd=testRequest
    key = {'wd': keywords, 'pn': (page - 1) * 10}

    # 请求Header
    headers = {
        'User-Agent': random.choice(user_agent_pool)}

    proxies = {'http': 'http://' + proxy}
    # 抓取数据内容
    web_content = requests.get("https://www.baidu.com/s?", params=key, headers=headers, proxies=proxies, timeout=4)

    return web_content.text


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
        'User-Agent': random.choice(user_agent_pool)}

    web_content = requests.get(url, headers=headers, timeout=4, allow_redirects=False)
    return web_content.headers['Location']


def html_parser(html):
    tree = etree.HTML(html)
    items = tree.xpath("//div[@id='content_left']//div[contains(@class,'c-container')]")
    parse_result_list = []
    for item in items:
        content = ''
        date = ''
        url = ''
        title = ''

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
            try:
                url = url_parser(href.get('href'), proxy)
            except:
                url = href.get('href')

        title_eles = item.xpath(".//h3[contains(@class,'t')]")
        for title_ele in title_eles:
            for child in title_ele.xpath(".//text()"):
                title += child

        if len(content) <= 0:
            continue

        parse_result = {'content': content, 'date': date, 'url': url, 'title': title}

        parse_result_list.append(parse_result)
    return parse_result_list


def extract_all_text(keyword, page, result_text, ip_factory):
    useful_proxies = {}
    max_failure_times = 3
    try:
        # 获取代理IP数据
        for ip in ip_factory.get_proxies():
            useful_proxies[ip] = 0
        print "总共：" + str(len(useful_proxies)) + 'IP可用'
    except OSError:
        print "获取代理ip时出错！"

    with open(result_text, 'w') as rt:

        current_page = 1
        while current_page < page:

            # 设置随机代理
            proxy = random.choice(useful_proxies.keys())
            print "change proxies: " + proxy
            try:
                content = download_html(keyword, proxy, current_page)
            except:
                # 超过3次则删除此proxy
                useful_proxies[proxy] += 1
                if useful_proxies[proxy] > max_failure_times:
                    useful_proxies.remove(proxy)
                continue

            if content is None:
                continue

            results = html_parser(content)

            current_page += 1

            for result in results:
                print json.dumps(result)
                rt.write(
                    result['title'] + '\t' + result['content'] + '\t' + result['date'] + '\t' + result['url'] + '\n')


def main():
    parser = OptionParser()
    parser.add_option("-o", "--output", action="store",
                      dest="output",
                      default="results.csv",
                      help="the destination of crawler results")
    parser.add_option("-k", "--key", action="store",
                      dest="key",
                      help="thr keyword to be searched(REQUIRED)")
    parser.add_option("-p", "--page", action="store",
                      dest="page",
                      default=10,
                      type="int",
                      help="the number of page to crawl")

    (options, args) = parser.parse_args()
    if not options.key:
        parser.error('Keyword not given')
    result_text = options.output
    extract_all_text(options.key, options.page, result_text, ip_pool.ip_factory)


if __name__ == '__main__':
    main()
