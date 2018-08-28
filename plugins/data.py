# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import collections
import json
import logging
import os
import yaml

from blinker import signal

from pelican import signals
from pelican.contents import Content, Page
from pelican.generators import CachingGenerator
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import (slugify, DateFormatter, copy, mkdir_p, posixize_path,
                           process_translations, python_2_unicode_compatible)


logger = logging.getLogger(__name__)


data_generator_init = signal('data_generator_init')
data_generator_finalized = signal('data_generator_finalized')
data_writer_finalized = signal('data_writer_finalized')

data_generator_preread = signal('data_generator_preread')
data_generator_context = signal('data_generator_context')

SUPPORTED_FORMATS = 'json yaml yml'.split()


def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))


yaml.add_representer(collections.OrderedDict, dict_representer)
yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, dict_constructor)


@python_2_unicode_compatible
class Data(object):
    '''
    Represents a single data item from a collection.

    :param content: the string to parse, containing the original content.
    :param metadata: the metadata associated to this page (optional).
    :param settings: the settings dictionary (optional).
    :param source_path: The location of the source of this content (if any).
    :param context: The shared context between generators.
    '''

    def __init__(self, content, metadata=None, settings=None,
                 source_path=None, context=None):

        if metadata is None:
            metadata = {}
        if settings is None:
            settings = copy.deepcopy(DEFAULT_CONFIG)

        self.settings = settings
        self.content = content
        if context is None:
            context = {}
        self._context = context
        self.translations = []

        local_metadata = dict()
        local_metadata.update(metadata)

        # set metadata as attributes
        for key, value in local_metadata.items():
            # if key in ('save_as', 'url'):
            #     key = 'override_' + key
            setattr(self, key.lower(), value)

        # also keep track of the metadata attributes available
        self.metadata = local_metadata

        #default template if it's not defined in page
        # self.template = self._get_template()

        # First, read the authors from "authors", if not, fallback to "author"
        # and if not use the settings defined one, if any.
        # if not hasattr(self, 'author'):
        #     if hasattr(self, 'authors'):
        #         self.author = self.authors[0]
        #     elif 'AUTHOR' in settings:
        #         self.author = Author(settings['AUTHOR'], settings)
        #
        # if not hasattr(self, 'authors') and hasattr(self, 'author'):
        #     self.authors = [self.author]

        # XXX Split all the following code into pieces, there is too much here.

        # manage languages
        # self.in_default_lang = True
        # if 'DEFAULT_LANG' in settings:
        #     default_lang = settings['DEFAULT_LANG'].lower()
        #     if not hasattr(self, 'lang'):
        #         self.lang = default_lang
        #
        #     self.in_default_lang = (self.lang == default_lang)

        # create the slug if not existing,
        # generate slug according to the filename
        if not hasattr(self, 'slug'):
            basename = os.path.basename(os.path.splitext(source_path)[0])
            self.slug = slugify(basename, settings.get('SLUG_SUBSTITUTIONS', ()))

        self.source_path = source_path

        # manage the date format
        # if not hasattr(self, 'date_format'):
        #     if hasattr(self, 'lang') and self.lang in settings['DATE_FORMATS']:
        #         self.date_format = settings['DATE_FORMATS'][self.lang]
        #     else:
        #         self.date_format = settings['DEFAULT_DATE_FORMAT']
        #
        # if isinstance(self.date_format, tuple):
        #     locale_string = self.date_format[0]
        #     if sys.version_info < (3, ) and isinstance(locale_string,
        #                                                six.text_type):
        #         locale_string = locale_string.encode('ascii')
        #     locale.setlocale(locale.LC_ALL, locale_string)
        #     self.date_format = self.date_format[1]
        #
        # # manage timezone
        # default_timezone = settings.get('TIMEZONE', 'UTC')
        # timezone = getattr(self, 'timezone', default_timezone)
        #
        # if hasattr(self, 'date'):
        #     self.date = set_date_tzinfo(self.date, timezone)
        #     self.locale_date = strftime(self.date, self.date_format)
        #
        # if hasattr(self, 'modified'):
        #     self.modified = set_date_tzinfo(self.modified, timezone)
        #     self.locale_modified = strftime(self.modified, self.date_format)
        #
        # # manage status
        # if not hasattr(self, 'status'):
        #     self.status = settings['DEFAULT_STATUS']
        #     if not settings['WITH_FUTURE_DATES'] and hasattr(self, 'date'):
        #         if self.date.tzinfo is None:
        #             now = SafeDatetime.now()
        #         else:
        #             now = SafeDatetime.utcnow().replace(tzinfo=pytz.utc)
        #         if self.date > now:
        #             self.status = 'draft'
        #
        # # store the summary metadata if it is set
        # if 'summary' in metadata:
        #     self._summary = metadata['summary']

        signals.content_object_init.send(self)

    def __str__(self):
        return self.source_path or repr(self)

    # def __getattr__(self, name):


    def get_relative_source_path(self, source_path=None):
        """Return the relative path (from the content path) to the given
        source_path.

        If no source path is specified, use the source path of this
        content object.
        """
        if not source_path:
            source_path = self.source_path
        if source_path is None:
            return None

        return posixize_path(
            os.path.relpath(
                os.path.abspath(os.path.join(self.settings['PATH'], source_path)),
                os.path.abspath(self.settings['PATH'])
            ))


class Collection(list):
    '''An augmented list to act as Data storage'''
    def __init__(self, name, path, *args):
        self.name = name
        self.path = path
        super(Collection, self).__init__(*args)


class DataGenerator(CachingGenerator):
    '''
    Load data into context and optionnaly render pages for them
    '''

    def __init__(self, *args, **kwargs):
        self.data = {}
        super(DataGenerator, self).__init__(*args, **kwargs)
        data_generator_init.send(self)

    def is_supported(self, name):
        paths = self.settings.setdefault('DATA_PATHS', [])
        paths = [os.path.join(p, name) for p in paths]
        extensions = SUPPORTED_FORMATS + list(self.readers.extensions)
        return any(map(os.path.isdir, paths)) or any(name.endswith(ext) for ext in extensions)

    def generate_context(self):
        for name in self.settings['DATA']:
            if not self.is_supported(name):
                logger.warning('Unsupported file format: %s', name)
                continue
            data = None
            for root in self.settings.setdefault('DATA_PATHS', []):
                path = os.path.join(root, name)
                if os.path.isdir(path):
                    data = self.context_for_dir(name, path)
                elif os.path.exists(path):
                    name, ext = os.path.splitext(name)
                    if ext in ('.yaml', '.yml'):
                        data = self.context_for_yaml(name, path)
                    elif ext == '.json':
                        data = self.context_for_json(name, path)
                    else:
                        data = self.context_for_reader(name, path)
                    break
                else:
                    continue

            if not data:
                logger.warning('Missing data: %s', name)
                continue

            self.data[name] = data

        self.context['data'] = self.data

        self.save_cache()
        self.readers.save_cache()
        data_generator_finalized.send(self)

    def context_for_dir(self, name, path):
        collection = Collection(name, path)

        for f in self.get_files(collection.path):
            item = self.get_cached_data(f, None)
            if item is None:
                try:
                    item = self.readers.read_file(
                        base_path=self.path, path=f, content_class=Data,
                        context=self.context,
                        preread_signal=data_generator_preread,
                        preread_sender=self,
                        context_signal=data_generator_context,
                        context_sender=self)
                except Exception as e:
                    logger.error('Could not process %s\n%s', f, e,
                                 exc_info=self.settings.get('DEBUG', False))
                    self._add_failed_source_path(f)
                    continue

                self.cache_data(f, item)

            self.add_source_path(item)
            collection.append(item)
        return collection

    def context_for_yaml(self, name, path):
        data = self.get_cached_data(path, None)
        if data is None:
            try:
                with open(path) as f:
                    data = yaml.load(f)
            except Exception as e:
                logger.error('Could not process %s\n%s', path, e,
                             exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(path)
                return

            self.cache_data(path, data)
        return data

    def context_for_json(self, name, path):
        data = self.get_cached_data(path, None)
        if data is None:
            try:
                with open(path) as f:
                    data = json.load(f)
            except Exception as e:
                logger.error('Could not process %s\n%s', path, e,
                             exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(path)
                return

            self.cache_data(path, data)
        return data

    def context_for_reader(self, name, path):
        data = self.get_cached_data(path, None)
        if data is None:
            try:
                data = self.readers.read_file(
                    base_path=self.path, path=path, content_class=Data,
                    context=self.context,
                    preread_signal=data_generator_preread,
                    preread_sender=self,
                    context_signal=data_generator_context,
                    context_sender=self)
            except Exception as e:
                logger.error('Could not process %s\n%s', path, e,
                             exc_info=self.settings.get('DEBUG', False))
                self._add_failed_source_path(path)
                return

            self.cache_data(path, data)

        self.add_source_path(data)
        return data

    #
    # def generate_output(self, writer):
    #     for page in chain(self.translations, self.pages,
    #                       self.hidden_translations, self.hidden_pages):
    #         writer.write_file(
    #             page.save_as, self.get_template(page.template),
    #             self.context, page=page,
    #             relative_urls=self.settings['RELATIVE_URLS'],
    #             override_output=hasattr(page, 'override_save_as'))
    #     data_writer_finalized.send(self, writer=writer)


def get_generators(sender, **kwargs):
    return DataGenerator


def register():
    signals.get_generators.connect(get_generators)
