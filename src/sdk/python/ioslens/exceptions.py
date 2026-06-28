"""iOSLENS SDK exceptions."""


class IOSLensError(Exception):
    """Base exception for all iOSLENS SDK errors."""


class AuthenticationError(IOSLensError):
    """Raised when authentication fails."""


class PolicyDeniedError(IOSLensError):
    """Raised when a governance policy denies access."""

    def __init__(self, resource_type: str, action: str, reason: str = "") -> None:
        self.resource_type = resource_type
        self.action = action
        super().__init__(
            f"Policy denied: {action} on {resource_type}"
            + (f" ({reason})" if reason else "")
        )


class RateLimitError(IOSLensError):
    """Raised when the API rate limit is exceeded."""


class ValidationError(IOSLensError):
    """Raised when request validation fails."""
