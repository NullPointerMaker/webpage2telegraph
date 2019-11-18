def _findRawContent(item):
	if item.has_attr('content'):
		title = item['content'].strip()
		if title:
			return title
	return item.text.strip()