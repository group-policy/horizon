import logging

LOG = logging.getLogger(__name__)


def list_column_filter(items):
	if len(items) == 0:
		return ""
	return items
