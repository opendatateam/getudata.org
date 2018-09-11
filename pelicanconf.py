#!/usr/bin/env python
import os

AUTHOR = 'Open Data Team'
SITENAME = 'udata'

SITEDESCRIPTION = 'Bla bla bla'

TAGS = ('opendata', 'data')

# PATH = 'articles'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'

THEME = 'theme'

PATH = os.path.dirname(__file__)
OUTPUT_PATH = os.path.join(PATH, 'output')
ARTICLE_PATHS = [
    'articles',
]

CONTACT_EMAIL = 'contact@opendata.team'

# PAGE_PATHS = [
#     'pages',
# ]


# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_PATHS = [
    'images',
]

PLUGIN_PATHS = [
    'plugins',
]

PLUGINS = [
    'sitemap',
    'frontmark',
    'data',
    'related_posts',
    'jinja_tools',
]

DATA_PATHS = [
    'data',
]

DATA = [
    'identity.yml',
    'showcase',
    'plugins',
]

TEMPLATE_PAGES = {
    # 'templates/index.html': 'index.html'
}

# Serve the blog on /blog/
# INDEX_URL = 'blog.html'
# INDEX_SAVE_AS = 'blog.html'

ARTICLE_URL = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{date:%m}/{date:%d}/{slug}.html'

CATEGORY_URL = 'blog/category/{slug}.html'
CATEGORY_SAVE_AS = 'blog/category/{slug}.html'

TAG_URL = 'blog/tag/{slug}.html'
TAG_SAVE_AS = 'blog/tag/{slug}.html'

PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'


SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'daily',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

RELATED_POSTS_MAX = 3

SOCIAL = (
    ('github', 'https://github.com/opendatateam'),
    ('twitter', 'https://twitter.com/udata_project'),
    ('gitter', 'https://gitter.im/opendatateam/udata'),
)
