# -*- coding: utf-8 -*-
BOT_NAME = 'spider'

SPIDER_MODULES = ['spider.spiders']
NEWSPIDER_MODULE = 'spider.spiders'

ROBOTSTXT_OBEY=False

# Crawl responsibly by identifying yourself (and your website) on the user-age
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Redis config
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 400,
}
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_ENCODING = 'utf-8'
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"