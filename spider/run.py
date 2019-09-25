from scrapy import cmdline

# 启动爬虫
name = "baiduspider"
cmd = "scrapy crawl %s" % name
cmdline.execute(cmd.split())