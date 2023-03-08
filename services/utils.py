import os

import requests, zipfile
from io import BytesIO


def unzip_from_url(url, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    req = requests.get(url)
    zf = zipfile.ZipFile(BytesIO(req.content))
    zf.extractall(directory)



