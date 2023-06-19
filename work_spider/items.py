# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WorkSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class SchoolUnitItem(scrapy.Item) :
    
    name = scrapy.Field()
    area = scrapy.Field()
    artical_counts =  scrapy.Field()
    citel_counts =  scrapy.Field()
    download_counts =  scrapy.Field()
    tags =  scrapy.Field()
    source =  scrapy.Field()
    baseid =  scrapy.Field()
    img_path =  scrapy.Field()
    create_time =  scrapy.Field()
    path = scrapy.Field()
