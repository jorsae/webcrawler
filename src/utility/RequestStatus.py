from enum import Enum

class RequestStatus(Enum):
    OK = 1
    TIMEOUT = 2
    CONNECTION_ERROR = 3
    HTTP_ERROR = 4
    URL_ERROR = 5
    ERROR = 6
    NOT_ALLOWED = 7