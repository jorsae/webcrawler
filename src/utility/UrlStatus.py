from enum import Enum

class UrlStatus(Enum):
    OK = 1
    SSL_VERIFICATION_FAILED = 3
    ERROR = 3