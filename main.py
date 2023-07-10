import os
import sys
from scrapy.cmdline import execute


if __name__ == "__main__":

    # sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    execute(["scrapy", "crawl", "degree_paper"])
    
    
    