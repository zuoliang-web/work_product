# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WorkSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SchoolCheckItem(scrapy.Item):
    baseid =  scrapy.Field()
    isExist = scrapy.Field()

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
    degree_type = scrapy.Field()
    pcode = scrapy.Field()


class articleCheckItem(scrapy.Item):
    title = scrapy.Field()
    isExist = scrapy.Field()

class articlesItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    funds = scrapy.Field()
    company = scrapy.Field()
    pageno = scrapy.Field()
    summary = scrapy.Field()
    doi = scrapy.Field()
    collection = scrapy.Field()
    topic = scrapy.Field()
    type_code = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    page_link = scrapy.Field()
    status = scrapy.Field()
    journal_name = scrapy.Field()
    pubtype = scrapy.Field()
    pcode = scrapy.Field()
    baseid = scrapy.Field()
    journal_topic = scrapy.Field()
    journal_collection = scrapy.Field()
    enname = scrapy.Field()
    region = scrapy.Field()
    lang = scrapy.Field()
    source_type = scrapy.Field()
    publish_company = scrapy.Field()
    journal_cn = scrapy.Field()
    journal_issn = scrapy.Field()
    journal_impact_syn = scrapy.Field()
    journal_impact = scrapy.Field()
    journal_img = scrapy.Field()
    