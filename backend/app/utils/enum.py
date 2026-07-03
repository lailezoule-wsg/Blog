"""
枚举
"""
from enum import Enum

class CommonOrderBy(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class ArticleQuerySortBy(str, Enum):
    CREATED = "created_at"
    PUBLISHED = "published_at"
    VIEW = "view_count"
    LIKE = "like_count"