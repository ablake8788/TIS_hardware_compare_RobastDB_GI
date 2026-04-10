class ValidationError(Exception):
    """Raised for recoverable input/config issues."""
    pass


class FatalError(Exception):
    """Raised for unrecoverable failures."""
    pass


class LLMError(Exception):
    """Raised when LLM call fails."""
    pass
