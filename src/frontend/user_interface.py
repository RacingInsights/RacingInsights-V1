import tkinter

from src.backend.iRacing.telemetry import RITelemetry
from src.frontend.overlays.overlays_container import OverlaysContainer
from src.frontend.screens.fuel_settings import FuelSettings
from src.frontend.screens.main_screen import MainScreen
from src.frontend.screens.relative_settings import RelativeSettings
from src.startup.my_configuration import CompleteConfig


class UserInterface:
    """High-level class that contains all other UI elements"""

    def __init__(self, root: tkinter.Tk, configuration: CompleteConfig, ri_telemetry: RITelemetry):
        self.root = root

        # Overlay Screens - Use updates based on configuration-state for activation/visibility
        self.overlays_container = OverlaysContainer(root=self.root,
                                                    configuration=configuration,
                                                    ri_telemetry=ri_telemetry,
                                                    )

        # UI Screens - Use event handler for activation/visibility
        self.main_screen = MainScreen(root=self.root, configuration=configuration, title="RacingInsights")
        self.fuel_settings = FuelSettings(root=self.root,
                                          title="Fuel calculator settings",
                                          configuration=configuration)
        self.relative_settings = RelativeSettings(root=self.root,
                                                  title="Relative overlay settings",
                                                  configuration=configuration)

    def update(self):
        self.overlays_container.update()
        self.root.update()
