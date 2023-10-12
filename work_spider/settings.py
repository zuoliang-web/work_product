
import configparser
import os
# Scrapy settings for work_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "work_spider"

SPIDER_MODULES = ["work_spider.spiders"]
NEWSPIDER_MODULE = "work_spider.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "work_spider (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "work_spider.middlewares.WorkSpiderSpiderMiddleware": 543,
    # "work_spider.middlewares.ProxyMiddleware": 543,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    # 'my_middlewares.MyAutoProxyDownloaderMiddleware': 601,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,   
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    "work_spider.middlewares.WorkSpiderDownloaderMiddleware": 543,
   "work_spider.middlewares.ProxyMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
#    "work_spider.pipelines.WorkSpiderPipeline": 300,
     "work_spider.pipelines.CnkiDegreePipeline":300
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# MONGO_USER = 'root'
# MONGO_PASSWD = 'abcd1234'
# MONGO_HOST = "192.168.0.120"
# MONGO_PORT = "27017"
# MONGO_DB = 'school_data'
# MONGO_COL = 'test_degree'

LOG_ENABLED = True #是否启动日志记录，默认True
LOG_ENCODING = 'UTF-8'
LOG_FILE = 'logs/cnkiSpider.log'#日志输出文件，如果为NONE，就打印到控制台
LOG_LEVEL = 'INFO'#日志级别，默认debugLOG_FORMAT #日志格式LOG_DATEFORMAT#日志日期格式LOG_STDOUT #日志标准输出，默认False，如果True所有标准输出都将写入日志中，比如代码中的print输出也会被写入到文件LOG_SHORT_NAMES#短日志名，默认为false，如果为True将不输出组件名


curpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
cfgpath = os.path.join(curpath, "config.ini")
print(cfgpath)  # c

 
# 创建管理对象
conf = configparser.ConfigParser()
 
# 读ini文件
conf.read(cfgpath, encoding="utf-8")  # python3
 

MONGO_INFOS = conf['mongodb']
PROXY_INFOS = conf['proxy']

proxyHost = PROXY_INFOS["proxyHost"]
proxyPort = PROXY_INFOS["proxyPort"]
proxyUser = PROXY_INFOS["proxyUser"]
proxyPass = PROXY_INFOS["proxyPass"]
proxyLoginUser = PROXY_INFOS["proxyLoginUser"]
proxyLoginPass = PROXY_INFOS["proxyLoginPass"]

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host" : proxyHost,
    "port" : proxyPort,
    "user" : proxyUser,
    "pass" : proxyPass,
}
proxies = {
    "http"  : proxyMeta,
    "https" : proxyMeta,
} 

switchProxyURL = "http://%s:%s@%s/simple/switch-ip?username=%s&password=%s" % (proxyLoginUser, proxyLoginPass, proxyHost, proxyUser, proxyPass)