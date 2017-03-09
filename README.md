# BaiduCrawler
A crawler crawling baidu searching results by means of constantly changing proxies.

Usage: baidu_crawler.py [options]

Options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output=OUTPUT
                        the destination of crawler results
  -k KEY, --key=KEY     thr keyword to be searched(REQUIRED)
  -p PAGE, --page=PAGE  the number of page to crawl

爬取百度搜索结果中c-container里的数据，并使用不断更换代理ip的方式绕过百度反爬虫策略，从而实现对数以10w计的词条的百度搜索结果进行连续爬取。

![](https://github.com/fancoo/BaiduCrawler/blob/master/images/git.png)

###获取代理ip策略

* 1. 抓取页面上全部[ip:port]对，并检测可用性（有的代理ip是连不通的）。
* 2. 使用"多轮检测"策略，即每个ip要经历N轮，间隔为duration连接测试，每轮都会丢弃连接时间超过timeout的ip。N轮下来，存活的ip都是每次都在timeout范围以内连通的，从而避免了"辉煌的15分钟"效应。

###爬取策略

有3个策略：
   * 1. 每当出现download_error，更换一个IP
   * 2. 每爬取200条文本，更换一个IP
   * 3. 每爬取20,000次，更新一次IP资源池
  
上述参数均可手动调整。
目前ip池的使用都是一次性的，如果想进一步建设、保存优质ip，可参考我的另一个项目[Proxy](https://github.com/fancoo/Proxy),它是一个代理ip抓取测试评估存储一体化工具，也许可以帮到你。

