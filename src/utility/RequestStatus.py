from enum import Enum

class RequestStatus(Enum):
    OK = 1
    TIMEOUT = 2
    CONNECTION_ERROR = 3
    ERROR = 4