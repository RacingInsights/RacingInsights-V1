from src.backend.iRacing.telemetry import RITelemetry
from src.frontend.overlays.fuel_overlay import FuelOverlay
from src.frontend.overlays.relative_overlay import RelativeOverlay
from src.startup.my_configuration import CompleteConfig


class OverlaysContainer:
    """Container for all the overlay screens"""

    def __init__(self, root, configuration: CompleteConfig, ri_telemetry: RITelemetry):
        self.fuel_overlay = FuelOverlay(root, configuration, ri_telemetry.fuel_telemetry)
        self.relative_overlay = RelativeOverlay(root, configuration, ri_telemetry.relative_telemetry)

    def update(self):
        self.fuel_overlay.update()
        self.relative_overlay.update()
