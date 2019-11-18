#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _copyB, fact

def _tagReplace(soup):
	wrap_with_p = [
		soup.find_all("div", class_="article-paragraph"),
		soup.find_all("section"),
	]
	for l in wrap_with_p:
		for item in l:
			wrapper = fact().new_tag("p")
			wrapper.append(_copyB(item))
			item.replace_with(wrapper)
	to_remove_tags = [
		soup.find_all("li"),
		soup.find_all("ul")
	]
	for l in to_remove_tags:
		for item in l:
			new_item = fact().new_tag("p")
			for x in item.find_all(recursive=False):
				new_item.append(x)
			item.replace_with(new_item)
	return soup