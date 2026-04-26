"""Custom errors used by reporting package."""


class TemplateError(Exception):
    """Raised when template compilation fails.

    Example:
        >>> raise TemplateError("Missing variable")
        Traceback (most recent call last):
        ...
        TemplateError: Missing variable
    """

