# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AuartItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field();
    url = scrapy.Field();
    uptime = scrapy.Field();
    hot = scrapy.Field();
    author = scrapy.Field();
    pass

class ArtItem(scrapy.Item):
    url = scrapy.Field();
    text = scrapy.Field();
    pass;

class BbscatspiderItem(scrapy.Item):
    cat = scrapy.Field();
    name = scrapy.Field();
    pass;
