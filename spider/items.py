# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FileItem(scrapy.Item):
    url = scrapy.Field()
    pwd = scrapy.Field()
    expiredtype = scrapy.Field()
    fs_id = scrapy.Field()
    parent_id = scrapy.Field()
    size = scrapy.Field()
    isdir = scrapy.Field()
    local_ctime = scrapy.Field()
    local_mtime = scrapy.Field()
    md5 = scrapy.Field()
    path = scrapy.Field()
    server_ctime = scrapy.Field()
    server_filename = scrapy.Field()
    share_id = scrapy.Field()
    uk = scrapy.Field()

class UserItem(scrapy.Item):
    url = scrapy.Field()
    pwd = scrapy.Field()
    share_username = scrapy.Field()
    share_photo = scrapy.Field()
    ctime = scrapy.Field()