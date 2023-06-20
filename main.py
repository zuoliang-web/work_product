import os
import sys
from scrapy.cmdline import execute


if __name__ == "__main__":

    # sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    execute(["scrapy", "crawl", "degreeArticles"])
    
    
    
# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings

# settings = get_project_settings()

# crawler = CrawlerProcess(settings)
# crawler.crawl('Nj')
# crawler.crawl('Yanc')
# crawler.crawl('Hzs')
# crawler.start()