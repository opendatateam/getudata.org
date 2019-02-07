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
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

CATEGORY_URL = 'blog/category/{slug}/'
CATEGORY_SAVE_AS = 'blog/category/{slug}/index.html'

TAG_URL = 'blog/tag/{slug}/'
TAG_SAVE_AS = 'blog/tag/{slug}/index.html'

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'


DELETE_OUTPUT_DIRECTORY = True

PLUGINS += (
    # 'image_optimizer',
    'gzip_cache',
)

PIWIK_URL = 'stats.data.gouv.fr'
PIWIK_SITE_ID = 60

DISPLAY_PAGES_ON_MENU = False
