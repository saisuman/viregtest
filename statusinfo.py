UNKNOWN = 0
OK = 1
RETRIABLE_ERROR = 2
PERMANENT_ERROR = 3
CONFIG_ERROR = 4
UNKNOWN_ERROR = 5

_NAMES = {
    UNKNOWN: "UNKNOWN",
    OK: "OK",
    RETRIABLE_ERROR: "RETRIABLE_ERROR",
    PERMANENT_ERROR: "PERMANENT_ERROR",
    CONFIG_ERROR: "CONFIG_ERROR"
}


class StatusInfo(object):
    """Holds the status of a request including any error / log messages."""
    def __init__(self, code=None, message=""):
        self.code = UNKNOWN if code is None else code
        self.message = message
    
    def ok(self):
        return self.code == OK
    
    def __str__(self):
        return "%s: %s" % (_NAMES[self.code], self.message)
    
    def to_dict(self):
        return {
            "code": _NAMES[self.code],
            "message": self.message
        }