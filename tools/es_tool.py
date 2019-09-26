from elasticsearch import Elasticsearch
from config import config

es = Elasticsearch([{'host': config.ES_HOST, 'port': config.ES_PORT}])

def create_file_index(index=None, doc_type=None):
    """
    创建文件ES索引
    :param index:
    :param doc_type:
    :return:
    """
    if es.indices.exists(index):
        es.indices.delete(index)

    idx_mapping = {
        "properties": {
            "url": {
                "type": "keyword",
                "index": True
            },
            "pwd": {
                "type": "keyword",
                "index": False
            },
            "expiredtype": {
                "type": "long",
                "index": False
            },
            "fs_id": {
                "type": "keyword",
                "index": False
            },
            "parent_id": {
                "type": "keyword",
                "index": False
            },
            "size": {
                "type": "keyword",
                "index": False
            },
            "isdir": {
                "type": "boolean",
                "index": False
            },
            "local_ctime": {
                "type": "long",
                "index": True
            },
            "local_mtime": {
                "type": "long",
                "index": True
            },
            "md5": {
                "type": "keyword",
                "index": False
            },
            "path": {
                "type": "keyword",
                "index": False
            },
            "server_ctime": {
                "type": "long",
                "index": True
            },
            'server_filename': {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            'share_id': {
                "type": "keyword",
                "index": False
            },
            'uk': {
                "type": "keyword",
                "index": False
            }
        }
    }

    es.indices.create(index=index)
    es.indices.put_mapping(index=index, doc_type=doc_type, body=idx_mapping)

def create_user_index(index=None, doc_type=None):
    """
    创建用户ES索引
    :param index:
    :param doc_type:
    :return:
    """
    if es.indices.exists(index):
        es.indices.delete(index)

    idx_mapping = {
        "properties": {
            "url": {
                "type": "keyword",
                "index": True
            },
            "pwd": {
                "type": "keyword",
                "index": False
            },
            "share_username": {
                "type": "keyword",
                "index": True
            },
            "share_photo": {
                "type": "keyword",
                "index": False
            },
            "ctime": {
                "type": "long",
                "index": True
            }
        }
    }
    es.indices.create(index=index)
    es.indices.put_mapping(index=index, doc_type=doc_type, body=idx_mapping)

if __name__ == '__main__':
    create_file_index(index=config.FILE_INDEX, doc_type=config.SEARCH_TYPE)
    create_file_index(index=config.FILE_INDEX, doc_type=config.FILE_TYPE)
    create_user_index(index=config.USER_INDEX, doc_type=config.USER_TYPE)
