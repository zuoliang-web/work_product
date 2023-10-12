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
    company = scrapy.Field()
    isExist = scrapy.Field()

class articlesItem(scrapy.Item):
    pageno = scrapy.Field()     # 页码
    doi = scrapy.Field()        # doi
    collection = scrapy.Field() # 专辑
    topic = scrapy.Field()      # 专题
    type_code = scrapy.Field()  # 类别code
    keywords = scrapy.Field()   # 关键词
    size = scrapy.Field()        # 大小
    subject = scrapy.Field()     # 学科
    next_subject = scrapy.Field()     # 下属学科
    title = scrapy.Field()       # 标题   
    author = scrapy.Field()     # 作者
    company = scrapy.Field()      # 作者所属单位
    summary = scrapy.Field()    # 摘要
    download_count = scrapy.Field()    # 下载数
    mentor =  scrapy.Field()    # 导师
    degree_type = scrapy.Field()  # 论文级别
    degree_year = scrapy.Field() # 学位授予年度
    source_type = scrapy.Field() # 文献来源
    page_link = scrapy.Field()      # 文献链接
    create_time = scrapy.Field()        # 创建日期
    
    funds = scrapy.Field()
    update_time = scrapy.Field()
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
    public_time = scrapy.Field()
    publish_company = scrapy.Field()
    journal_cn = scrapy.Field()
    journal_issn = scrapy.Field()
    journal_impact_syn = scrapy.Field()
    journal_impact = scrapy.Field()
    journal_img = scrapy.Field()
    