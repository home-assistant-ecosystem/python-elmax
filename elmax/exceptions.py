"""Exceptions for the Elmax Cloud services client."""


class ElmaxError(Exception):
    """General ElmxError exception occurred."""

    pass


class ElmaxConnectionError(ElmaxError):
    """When a connection error is encountered."""

    pass


class ElmaxNoDataAvailable(ElmaxError):
    """When no data is available."""

    pass
