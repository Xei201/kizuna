
from django.core.exceptions import ImproperlyConfigured


class NoModelFoundException(ImproperlyConfigured):
    """Exception raised when required model attribute is None"""
    pass


class NoCorrectPermission(PermissionError):
    """No permission"""
    pass
