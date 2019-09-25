from scrapy_redis.spiders import RedisSpider
from scrapy import Request, FormRequest
from scrapy.http.cookies import CookieJar
from spider.items import FileItem, UserItem
from utils.logger import logger
from utils.utils import shortkey
import json
import time
import re

class BaiduSpider(RedisSpider):
    name = "baiduspider"
    has_key = True
    cookies = {}

    def make_request_from_data(self, data):
        """
        从输入数据构造Request请求
        :param data:
        :return:
        """
        try:
            req_data = json.loads(data.decode('utf8'))
            url = req_data['url']
            key = shortkey(url=url)
            if req_data['pwd']:
                self.pwd = req_data['pwd']
                headers = {
                    'Host': 'pan.baidu.com',
                    'Origin': 'https://pan.baidu.com',
                    'Referer': 'https://pan.baidu.com/share/init?surl=t0pAkMLduMqwHGUho_S5WQ',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
                }
                data = {
                    'pwd': req_data['pwd']
                }
                now = int(time.time() * 1000)
                url = 'https://pan.baidu.com/share/verify?surl={}&t={}&channel=chunlei&web=1&app_id=250528&clienttype=0'.format(key[1:], str(now))
                logger.info('parse has-key input data succ, url:{}, key:{}'.format(url, self.pwd))
                return FormRequest(url=url, formdata=data, method='POST', headers=headers, dont_filter=True, meta={"key": key})
            else:
                self.has_key = False
                url = 'https://pan.baidu.com/api/shorturlinfo?web=5&app_id=250528&clienttype=5&shorturl={}'.format(key)
                logger.info('parse no-key input data succ, url:{}'.format(url))
                return Request(url=url, dont_filter=True, meta={"key": key})
        except Exception as e:
            logger.error('parse input data fail, data:{}, err_msg:{}'.format(data, e))

    def parse(self, response):
        """
        解析入口
        :param response:
        :return:
        """
        # 有提取码
        if self.has_key:
            try:
                data = json.loads(response.text)
                if data['errno'] != 0:
                    logger.error('parse has-key fail, url:{}, pwd:{}, errno:{}'.format(response.url, self.pwd, str(data['errno'])))
                    return
                cookie_jar = CookieJar()
                cookie_jar.extract_cookies(response, response.request)
                self.save_cookie(cookie_jar)
                url = 'https://pan.baidu.com/s/{}'.format(response.meta['key'])
                meta = {
                    'shorturl': response.meta['key']
                }
                logger.info('parse has-key succ, url:{}, key:{}'.format(url, self.pwd))
                yield Request(url, cookies=self.cookies, callback=self.parse_data_key, dont_filter=True, meta=meta)
            except Exception as e:
                logger.error('parse has-key fail: exception, url:{}, pwd:{}, err_msg:{}'.format(response.url, self.pwd, e))
        # 无提取码
        else:
            try:
                data = json.loads(response.text)
                if data['errno'] == -3:
                    url = 'https://pan.baidu.com/share/list?web=5&app_id=250528&channel=chunlei&clienttype=5&desc=1' \
                          '&showempty=0&order=time&root=1&shorturl={}'.format(response.meta['key'][1:])
                    meta = {
                        'share_username': data['share_username'],
                        'share_photo': data['share_photo'],
                        'ctime': data['ctime'],
                        'shorturl': data['shorturl'],
                        'expiredtype': data['expiredtype']
                    }
                    logger.info('parse no-key succ, url:{}, key:{}'.format(url, self.pwd))
                    yield Request(url, dont_filter=True, callback=self.parse_data_nokey, meta=meta)
                elif data['errno'] == -21:
                    logger.error('parse no-key fail: share cancel, url:{}'.format(response.url))
                elif data['errno'] == -105 or data['errno'] == 2:
                    logger.error('parse no-key fail: link error, url:{}'.format(response.url))
                else:
                    logger.error('parse no-key fail: unknown error, url:{}'.format(response.url))
            except Exception as e:
                logger.error('parse no-key fail: exception, url:{}, err_msg:{}'.format(response.url, e))

    def save_cookie(self, cookie_jar):
        """
        保存cookie
        :param cookie_jar:
        :return:
        """
        for cookie in cookie_jar:
            pattern = re.compile('<Cookie (.*?) for .*?>')
            cookies = re.findall(pattern, str(cookie))
            item = cookies[0].split('=', 1)
            self.cookies[item[0]] = item[1]

    def parse_data_key(self, response):
        """
        解析并保存有提取码类型的第一级目录/文件
        :param data:
        :return:
        """
        try:
            res = re.search(r'yunData.setData\((.*?)\);', response.text)
            if not res:
                logger.error('parse has-key first data fail, url:{}, pwd:{}'.format(response.url, self.pwd))
                return

            data = json.loads(res.group(1))
            if data and data['file_list']['errno'] != 0:
                logger.error('parse data fail, url:{}, pwd:{}, errno:{}'.format(response.url, self.pwd, data['file_list']['errno']))
                return

            for file in data['file_list']['list']:
                yield FileItem(
                    url=response.meta['shorturl'],
                    pwd=self.pwd,
                    expiredtype=data['expiredType'],
                    fs_id=file['fs_id'],
                    parent_id=0,
                    size=file['size'],
                    isdir=int(file['isdir']),
                    local_ctime=file['local_ctime'],
                    local_mtime=file['local_mtime'],
                    md5=file['md5'],
                    path=file['path'],
                    server_ctime=file['server_ctime'],
                    server_filename=file['server_filename'],
                    share_id=data['shareid'],
                    uk=data['uk']
                )

                if int(file['isdir']) == 1:
                    url = 'https://pan.baidu.com/share/list?uk={}&shareid={}&order=other&desc=1&showempty=0&web=1&' \
                          'dir=/sharelink{}-{}/{}&channel=chunlei&web=1&app_id=250528'.format(data['uk'], data['shareid'],
                                data['uk'], file['fs_id'], file['server_filename'])
                    meta = {
                        'uk': data['uk'],
                        'share_id': data['shareid'],
                        'fs_id': file['fs_id'],
                        'parent_id': file['fs_id'],
                        'filepath': file['server_filename']
                    }
                    yield Request(url=url, cookies=self.cookies, dont_filter=True, callback=self.parse_dir, meta=meta)

            yield UserItem(
                share_username=data['linkusername'],
                share_photo=data['photo'],
                ctime=data['ctime']
            )
            logger.info('parse has-key first data succ, url:{}, key:{}, share_id:{}, uk:{}'.format(response.url, self.pwd, data['shareid'], data['uk']))
        except Exception as e:
            logger.error('parse has-key first data fail: exception, url:{}, err_msg:{}'.format(response.url, e))

    def parse_data_nokey(self, response):
        """
        解析并保存无提取码类型的第一级目录/文件
        :param response:
        :return:
        """
        try:
            data = json.loads(response.text)
            if data['errno'] != 0:
                logger.error('parse no-key data fail, url:{}, errno:{}'.format(response.url, str(data['errno'])))
                return

            for file in data['list']:
                yield FileItem(
                    url=response.meta['shorturl'],
                    pwd=None,
                    expiredtype=response.meta['expiredtype'],
                    fs_id=file['fs_id'],
                    parent_id=0,
                    size=file['size'],
                    isdir=int(file['isdir']),
                    local_ctime=file['local_ctime'],
                    local_mtime=file['local_mtime'],
                    md5=file['md5'],
                    path=file['path'],
                    server_ctime=file['server_ctime'],
                    server_filename=file['server_filename'],
                    share_id=data['share_id'],
                    uk=data['uk']
                )

                if int(file['isdir']) == 1:
                    url = 'https://pan.baidu.com/share/list?uk={}&shareid={}&order=other&desc=1&showempty=0&web=1&' \
                            'dir=/sharelink{}-{}/{}&channel=chunlei&web=1&app_id=250528'.format(data['uk'], data['share_id'],
                                data['uk'], file['fs_id'], file['server_filename'])
                    meta = {
                        'uk': data['uk'],
                        'share_id': data['share_id'],
                        'fs_id': file['fs_id'],
                        'parent_id': file['fs_id'],
                        'filepath': file['server_filename']
                    }
                    yield Request(url=url, dont_filter=True, callback=self.parse_dir, meta=meta)

            yield UserItem(
                share_username=response.meta['share_username'],
                share_photo=response.meta['share_photo'],
                ctime=response.meta['ctime']
            )
            logger.info('parse no-key first data succ, url:{}, key:{}, share_id:{}, uk:{}'.format(response.url, self.pwd, data['share_id'], data['uk']))
        except Exception as e:
            logger.error('parse no-key first data fail: exception, url:{}, err_msg:{}'.format(response.url, e))

    def parse_dir(self, response):
        """
        解析目录
        :param response:
        :return:
        """
        try:
            data = json.loads(response.text)
            if data['errno'] != 0:
                logger.error('parse dir data fail, url: %s, errno:%s' % (response.url, str(data['errno'])))
            for file in data['list']:
                yield FileItem(
                    url=None,
                    pwd=None,
                    expiredtype=None,
                    fs_id=file['fs_id'],
                    parent_id=response.meta['parent_id'],
                    size=file['size'],
                    isdir=int(file['isdir']),
                    local_ctime=file['local_ctime'],
                    local_mtime=file['local_mtime'],
                    md5=file['md5'] if 'md5' in file else None,
                    path=file['path'],
                    server_ctime=file['server_ctime'],
                    server_filename=file['server_filename'],
                    share_id=None,
                    uk=None
                )
                logger.info('parse data succ, fs_id:{}, parent_id:{}'.format(file['fs_id'], response.meta['parent_id']))
                if int(file['isdir']) == 1:
                    url = 'https://pan.baidu.com/share/list?uk={}&shareid={}&order=other&desc=1&showempty=0&web=1&' \
                          'dir=/sharelink{}-{}/{}&channel=chunlei&web=1&app_id=250528'.format(response.meta['uk'], response.meta['share_id'],
                                response.meta['uk'], response.meta['fs_id'], response.meta['filepath'] + '/' + file['server_filename'])
                    meta = {
                        'uk': response.meta['uk'],
                        'share_id': response.meta['share_id'],
                        'fs_id': response.meta['fs_id'],
                        'parent_id': file['fs_id'],
                        'filepath': response.meta['filepath'] + '/' + file['server_filename']

                    }
                    yield Request(url=url, cookies=self.cookies, dont_filter=True, callback=self.parse_dir, meta=meta)
        except Exception as e:
            logger.error('parse dir data fail: exception, url:{}, err_msg:{}'.format(response.url, e))