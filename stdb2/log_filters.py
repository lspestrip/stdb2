# -*- encoding: utf-8 -*-

from logging import Filter
from pprint import pprint


class ManagementFilter(Filter):
    'Filter to avoid logging raw SQL commands'

    def filter(self, record):
        if hasattr(record, 'funcName') and (record.funcName == 'execute'):
            return False
        else:
            return True
