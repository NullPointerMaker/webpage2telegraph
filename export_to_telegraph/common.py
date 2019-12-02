#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

def _findRawContent(item):
	if item.has_attr('content'):
		title = item['content'].strip()
		if title:
			return title
	return item.text.strip()

def fact():
	return BeautifulSoup("<div></div>", features="lxml")

def _copyB(soup):
	return BeautifulSoup(str(soup), features="lxml")

def _seemsValidText(soup, limit=500):
	if not soup:
		return False
	return soup.text and len(soup.text) > limit

def _wrap(name, *children):
	r = fact().new_tag(name)
	for child in children:
		r.append(child)
	return r