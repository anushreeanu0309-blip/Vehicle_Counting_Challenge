class VehicleCountingError(Exception):
    """Base application exception."""


class ConfigurationError(VehicleCountingError):
    """Raised when configuration is invalid."""


class VideoOpenError(VehicleCountingError):
    """Raised when input video cannot be opened."""


class ProcessingError(VehicleCountingError):
    """Raised when processing pipeline fails."""
