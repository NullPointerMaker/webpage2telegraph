#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def _find_raw_content(item):
    if item.has_attr('content'):
        title = item['content'].strip()
        if title:
            return title
    return item.text.strip()
