"""iOSLENS Python SDK — exceptions."""


class IOSLensError(Exception):
    """Base exception for all iOSLENS SDK errors."""


class AuthenticationError(IOSLensError):
    """Raised when authentication fails (HTTP 401)."""


class AuthorizationError(IOSLensError):
    """Raised when authorization is denied (HTTP 403)."""


class RateLimitError(IOSLensError):
    """Raised when the rate limit is exceeded (HTTP 429)."""


class ValidationError(IOSLensError):
    """Raised on request validation errors (HTTP 422)."""


class MCPError(IOSLensError):
    """Raised on MCP JSON-RPC errors."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"MCP error {code}: {message}")
        self.code = code
        self.message = message
