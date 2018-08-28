#!/usr/bin/env python

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'https://getudata.org'
RELATIVE_URLS = False

FEED_DOMAIN = SITEURL
FEED_ALL_ATOM = 'feeds/all.atom'
CATEGORY_FEED_ATOM = 'feeds/%s.atom'

ARTICLE_URL = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
CATEGORY_URL = 'blog/category/{slug}/'
TAG_URL = 'blog/tag/{slug}/'
PAGE_URL = '{slug}/'


DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing

#DISQUS_SITENAME = ""
#GOOGLE_ANALYTICS = ""

PLUGINS += (
    'image_optimizer',
    'gzip_cache',
)
