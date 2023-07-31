import math
import statistics
from typing import List, Optional

from irsdk import IRSDK

from src.backend.iRacing.overlay_telemetries.timing_telemetry import TimingTelemetry
from src.backend.iRacing.overlay_telemetry import OverlayTelemetry
from src.backend.iRacing.utils.zero_div import zero_div

FUEL_BUFFER_L = 0.3


class TelemetryValue:
    """Test"""

    def __init__(self, value):
        self.value: int | float = value


class FuelTelemetry(OverlayTelemetry):
    """Implements all the relevant telemetry needed for the fuel overlay"""

    def __init__(self, ir_sdk: IRSDK, timing_telemetry: TimingTelemetry):
        self.ir_sdk = ir_sdk
        self.timing = timing_telemetry

        # Values - Measured
        self.fuel = TelemetryValue(0.00)

        # Determined by calculation
        self.previous_lap_fuel_count: float = 0.00
        self.consumptions: List[Optional[float]] = []
        self.last_consumption = TelemetryValue(0.00)

        self.average_consumption = TelemetryValue(0.00)
        self.range_laps = TelemetryValue(0)
        self.range_laps_extra = TelemetryValue(1)
        self.target_consumption = TelemetryValue(0.00)
        self.target_consumption_extra = TelemetryValue(0.00)
        self.target_consumption_finish = TelemetryValue(0.00)
        self.refuel_amount = TelemetryValue(0.00)

    def update(self) -> None:
        """Updates the attribute values of the fuel telemetry"""
        self.fuel.value = self.ir_sdk['FuelLevel']

        if not self.timing.new_lap:
            return

        if self.previous_lap_fuel_count - self.fuel.value < 0:  # Refueled
            self.consumptions = []
        else:
            self.last_consumption.value = self.previous_lap_fuel_count - self.fuel.value
            self.consumptions.append(self.last_consumption.value)
        self.previous_lap_fuel_count = self.fuel.value

        if 0.0 in self.consumptions:
            self.consumptions = [num for num in self.consumptions if num != 0]  # Filter out bad data

        if len(self.consumptions) > 0:
            self.average_consumption.value = statistics.median(self.consumptions)
            print(self.consumptions, self.average_consumption.value)
        else:
            self.average_consumption.value = 0.00

        self.range_laps.value = math.floor(zero_div(x=self.fuel.value, y=self.average_consumption.value))
        self.range_laps_extra.value = self.range_laps.value + 1
        self.target_consumption.value = zero_div(x=self.fuel.value - FUEL_BUFFER_L, y=self.range_laps.value)
        self.target_consumption_extra.value = zero_div(x=self.fuel.value - FUEL_BUFFER_L, y=self.range_laps_extra.value)
        self.target_consumption_finish.value = zero_div(x=self.fuel.value - FUEL_BUFFER_L,
                                                  y=self.timing.laps_to_finish_player)
        laps_of_fuel = max(self.timing.laps_to_finish_player - self.range_laps.value + 0.15, 0)
        self.refuel_amount.value = laps_of_fuel * self.average_consumption.value
