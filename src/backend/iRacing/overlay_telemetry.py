import abc


class OverlayTelemetry(metaclass=abc.ABCMeta):
    """Abstract base class that defines the minimum implementation requirements for an overlay telemetry class"""

    @abc.abstractmethod
    def update(self) -> None:
        """Method to update the telemetry attribute values"""
