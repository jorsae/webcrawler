from enum import Enum


class UrlStatus(Enum):
    OK = 1
    SSL_VERIFICATION_FAILED = 2
    ERROR = 3
    NOT_CHECKED = 4
