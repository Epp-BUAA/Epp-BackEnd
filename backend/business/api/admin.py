"""
    数据管理模块API
    api/admin/...
"""
import json

from django.views.decorators.http import require_http_methods

from business.models import User
from business.models import SearchRecord
from business.models import SummaryReport
from business.utils import reply
