# -*- coding:utf-8 -*-

__all__ = [
    'publish_to_stream'
]

import sys


def publish_to_stream(*iterators, **ctx):
    stream = ctx.pop('stream', sys.stdout)
    record_delimiter = ctx.pop('record_delimiter', '\n')
    record_converter = ctx.pop('record_converter', lambda s: s)
    for iterator in iterators:
        for record in iterator:
            stream.write(record_converter(record) + record_delimiter)
