#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import matchKey

def _replaceOfftopicLink(soup):
	for link in soup.find_all("a"):
		if matchKey(link.text, ['英文版']):
			continue
		if link.find('figure'):
			link.replace_with(link.find('figure'))
			continue
		if link.text and link.text.strip():
			link.replace_with(link.text)
			continue
		link.decompose()
	return soup