#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import matchKey

from .common import _find_raw_content


def _get_attr_string(attrs):
    if not attrs:
        return ''
    r = []
    for k, v in attrs.items():
        if k in ['content']:
            continue
        r.append(k + ': ' + str(v))
    return '\n'.join(r)


def _yield_possible_author_item(soup):
    yield soup.find("meta", {"name": "byl"})
    yield soup.find("span", {"class": "byline__name"})
    for item in soup.find_all('meta'):
        if 'author' in _get_attr_string(item.attrs):
            yield item
    for item in soup.find_all('div', class_='news_about'):
        yield item.find('p')
    yield soup.find("a", {"id": "js_name"})
    yield soup.find('a', class_='author-url')
    yield soup.find('span', class_='posted-date')
    yield soup.find('a', class_='name')
    yield soup.find('div', class_='article-author')
    yield soup.find("meta", {"name": "application-name"})
    for item in soup.find_all('a'):
        if matchKey(_get_attr_string(item.attrs), ['author']):
            yield item
    for item in soup.find_all('a'):
        if matchKey(_get_attr_string(item.attrs), ['/people/']):
            yield item


def _yield_possible_org_item(soup):
    yield soup.find("meta", {"property": "twitter:site"})
    yield soup.find("meta", {"property": "twitter:domain"})
    yield soup.find("meta", {"property": "og:site_name"})


def _find_possible_raw_content(item_iterator, words_to_ignore=None):
    if words_to_ignore is None:
        words_to_ignore = []
    for item in item_iterator:
        if not item:
            continue
        r = _find_raw_content(item)
        if r and not matchKey(r, words_to_ignore):
            index = r.find(' - ')
            if index == -1:
                return r
            else:
                return r[:index]


def _find_org_name(soup):
    head = str(soup.find('head'))
    if matchKey(head, ['bbc.com']):
        return 'BBC', True
    if matchKey(head, ['nyt.com', 'new york times']):
        return 'NYT', True
    if matchKey(head, ['stackoverflow']):
        return 'StackOverflow', False
    if matchKey(head, ['medium.com']):
        return 'Medium', False
    if matchKey(head, ['dw.come']):
        return 'DW', True
    r = _find_possible_raw_content(_yield_possible_org_item(soup))
    if r:
        return r, False
    return '原文', False


def _find_author(soup):
    author_name = _find_possible_raw_content(
        _yield_possible_author_item(soup),
        ['://', 'http', 'www'])
    org, required = _find_org_name(soup)
    if not author_name:
        return org
    if not required or '-' in author_name:
        return author_name
    return author_name + ' - ' + org
