"""Domain errors raised by pure financial calculations."""


class AnalysisError(ValueError):
    """Base class for invalid analysis inputs."""


class InsufficientObservationsError(AnalysisError):
    """Raised when a calculation does not have enough price observations."""


class InvalidPriceError(AnalysisError):
    """Raised when a price is non-positive or non-finite."""
