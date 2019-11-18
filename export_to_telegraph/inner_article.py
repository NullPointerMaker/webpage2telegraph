#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _seemsValidText

def _seemsValidRawArticle(soup):
	if not _seemsValidText(soup):
		return False
	return not not soup.find('img')

def _getInnerArticle(soup):	
	applicators = [
		lambda x: x.find("article"),
		lambda x: x.find("div", {"id" : "js_content"}),
		lambda x: x.find("div", class_ = "story-body__inner"),
		lambda x: x.find("div", class_ = "answercell"),
		lambda x: x.find("div", class_ = "post-text"),
		lambda x: x.find("div", {"id" : "bodyContent"}),
		lambda x: x.find("div", {"id" : "content_JS"}),
	]
	for applicator in applicators:
		candidate = applicator(soup)
		if _seemsValidRawArticle(candidate):
			soup = candidate
	return soup