#!/usr/bin/python2.7
import os
from rest import app as rest_api
from pdfparser import _config

if __name__ == '__main__':
    host = _config.get('REST', 'HOST')
    port = _config.get('REST', 'PORT')
    rest_api.app.run(host=host, port=int(os.environ.get("PORT", port)), debug=False)
