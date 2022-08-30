class ScraperException(Exception):
    pass


class LogicError(ScraperException):
    pass


class RollBack(Exception):
    pass


class ParseError(Exception):
    pass
