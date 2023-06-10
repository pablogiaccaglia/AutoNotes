import os

import requests, zipfile
from io import BytesIO
import re

def unzip_from_url(url, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    req = requests.get(url, headers = headers)
    zf = zipfile.ZipFile(BytesIO(req.content))
    zf.extractall(directory)

def format_notion_id(id):
    pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    if pattern.match(id):
        return id
    else:
        assert len(id) == 32
        return f"{id[:8]}-{id[8:12]}-{id[12:16]}-{id[16:20]}-{id[20:]}"
