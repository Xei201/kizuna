
from django.core.exceptions import ImproperlyConfigured, PermissionDenied, ValidationError


class NoModelFoundException(ImproperlyConfigured):
    """Exception raised when required model attribute is None"""
    pass


class NoCorrectPermission(PermissionDenied):
    """No permission"""
    pass


class NoValidTokenService(ValidationError):
    """Not valid token Service"""
    pass


class NoSpecifiedTokenService(ValidationError):
    """Not entered token Service"""
    pass

