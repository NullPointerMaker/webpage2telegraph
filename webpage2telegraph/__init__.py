#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'webpage2telegraph'
token = ''

from html_telegraph_poster import TelegraphPoster

from .article import get


def _get_poster():
    global token
    if token:
        return TelegraphPoster(access_token=token)
    p = TelegraphPoster()
    r = p.create_api_token('webpage2telegraph', 'webpage2telegraph')
    token = r['access_token']
    return p


def _trim_url(url):
    if '://' not in url:
        return url
    loc = url.find('://')
    return url[loc + 3:]


def _format_url(url):
    if '://' not in url:
        return "http://" + url
    return url


def _get_article(url, throw_exception=False, simplify=False, force_cache=False, no_auto_convert=False):
    try:
        return article.get(_format_url(url), simplify=simplify, force_cache=force_cache,
                           no_auto_convert=no_auto_convert)
    except Exception as e:
        if throw_exception:
            raise e


def get_author_url(article, url, source):
    if not source:
        return ''
    return _format_url(article.url or url)


def get_author_field(author, source):
    if author == '原文' and not source:
        return ''
    return author


def transfer(url, throw_exception=False, source=False, simplify=False, force_cache=False, no_auto_convert=False):
    try:
        p = _get_poster()
        article = _get_article(url, throw_exception=throw_exception, simplify=simplify, force_cache=force_cache,
                               no_auto_convert=no_auto_convert)
        if not article.text or not article.text.text.strip():  # content is empty
            article.text = '<div>需要手动编辑</div>'
        try:
            r = p.post(
                title=article.title,
                author=get_author_field(article.author, source),
                author_url=get_author_url(article, url, source),
                text=str(article.text))
        except Exception as e:
            if 'CONTENT_TEXT_REQUIRED' in str(e):
                r = p.post(
                    title=article.title,
                    author=get_author_field(article.author, source),
                    author_url=get_author_url(article, url, source),
                    text='<div>TO BE ADDED</div>')
            elif 'ACCESS_TOKEN_INVALID' in str(e):
                r = TelegraphPoster().post(
                    title=article.title,
                    author=get_author_field(article.author, source),
                    author_url=get_author_url(article, url, source),
                    text=str(article.text))
            else:
                raise e
        return _trim_url(r['url'])
    except Exception as e:
        if throw_exception:
            raise e
