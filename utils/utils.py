from urllib.parse import urlparse

def shortkey(url):
    parse = urlparse(url)
    if parse.path.startswith('/s/'):
        return parse.path.replace('/s/', '')