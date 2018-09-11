from __future__ import unicode_literals

import logging
import os
import shutil
import slugify
import sys

from datetime import datetime

from invoke import task

from pelican import Pelican, log

from pelican.settings import read_settings
from jinja2 import Environment, FileSystemLoader

if sys.version_info[0] == 3:
    try:
        from importlib import reload
    except:
        from imp import reload


#: Project absolute root path
TASKS_ROOT = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(TASKS_ROOT, '..'))

CONF_FILE = os.path.join(ROOT, 'pelicanconf.py')

# Port for `serve`
PORT = 5000


class objdict(dict):
    def __getattr__(self, name):
        return self[name]


def get_settings():
    return objdict(read_settings(CONF_FILE))


jinja_env = Environment(loader=FileSystemLoader(TASKS_ROOT))


def jinja(template, filename, **ctx):
    template = jinja_env.get_template(template)
    with open(filename, 'wb') as out:
        data = template.render(**ctx)
        out.write(data.encode('utf-8'))


@task
def clean(ctx):
    '''Remove generated files'''
    settings = get_settings()
    if os.path.isdir(settings.OUTPUT_PATH):
        shutil.rmtree(settings.OUTPUT_PATH)
        os.makedirs(settings.OUTPUT_PATH)


@task()
def build(ctx, verbose=False, debug=False):
    '''Build local version of site'''
    cmd = 'pelican -s publishconf.py'
    if verbose:
        cmd += ' -v'
    if verbose:
        cmd += ' -D'
    ctx.run(cmd)


def draft(article=False):
    '''Create a draft page'''
    title = input('Title: ')
    slug = slugify.slugify(title, to_lower=True)
    slug = input('Slug ({0}): '.format(slug)) or slug
    summary = input('Summary: ')
    tags = [t for t in input('Tags: ').split(',') if t]
    category = input('Category: ') if article else None
    now = datetime.now()
    if article:
        filename = '{0}-{1}.md'.format(now.date().isoformat(), slug)
        filename = os.path.join('articles', filename)
    else:
        filename = os.path.join('pages', '{0}.md'.format(slug))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    jinja('draft.j2.md', filename,
          title=title,
          slug=slug,
          category=category,
          summary=summary,
          tags=tags,
          is_article=article,
          date=now)


@task
def page(ctx):
    '''Create a draft page'''
    draft(article=False)


@task
def article(ctx):
    '''Create a draft article'''
    draft(article=True)


def reload_and_compile():
    _sys_path = sys.path[:]
    settings = get_settings()
    for pluginpath in settings.PLUGIN_PATHS:
        sys.path.insert(0, pluginpath)
    for name, module in sys.modules.items():
        root_module = name.split('.', 1)[0]
        if root_module in settings.PLUGINS:
            reload(module)

    sys.path = _sys_path
    compile()


def compile():
    settings = get_settings()
    p = Pelican(settings)
    try:
        p.run()
    except SystemExit as e:
        pass


@task
def watch(ctx, verbose=False):
    '''Serve the blog and watch changes'''
    from livereload import Server

    settings = get_settings()

    log.init(logging.DEBUG if verbose else logging.INFO)
    logging.getLogger('livereload').propagate = False
    logging.getLogger('tornado').propagate = False

    compile()
    server = Server()
    server.watch(CONF_FILE, compile)

    DATA_PATHS = getattr(settings, 'DATA_PATHS', [])
    for root in set(DATA_PATHS):
        for data in getattr(settings, 'DATA', []):
            path = os.path.join(root, data)
            if os.path.exists(path):
                server.watch(path, compile)

    paths = settings.ARTICLE_PATHS + settings.PAGE_PATHS + settings.STATIC_PATHS
    for path in paths:
        server.watch(path, compile)

    server.serve(port=PORT, root=settings.OUTPUT_PATH)
