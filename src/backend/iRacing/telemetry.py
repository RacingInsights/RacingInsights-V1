"""Python iRacing sdk for providing the data from the sim"""
from irsdk import IRSDK

from src.backend.AWS.resources import DynamoDB
from src.backend.iRacing.ir_state import IRState
from src.backend.iRacing.overlay_telemetries.fuel_telemetry import FuelTelemetry
from src.backend.iRacing.overlay_telemetries.relative_telemetry import RelativeTelemetry
from src.backend.iRacing.overlay_telemetries.timing_telemetry import TimingTelemetry


class RITelemetry:
    """Provides all telemetry needed for the overlays"""

    def __init__(self, dynamo_db_resource: DynamoDB):
        self.ir_sdk = IRSDK()
        self.ir_state = IRState()

        self.timing_telemetry = TimingTelemetry(ir_sdk=self.ir_sdk)
        self.fuel_telemetry = FuelTelemetry(ir_sdk=self.ir_sdk, timing_telemetry=self.timing_telemetry)
        self.relative_telemetry = RelativeTelemetry(ir_sdk=self.ir_sdk, dynamo_db_resource=dynamo_db_resource)
        # self.standings_telemetry = StandingsTelemetry()

    def update(self):
        """Method that will (attempt to) update all the telemetry data when possible"""
        # Check if still connected to iRacing
        self.ir_state.update_state(ir_sdk=self.ir_sdk)
        if not self.ir_state.ir_connected:
            return

        # Freeze the data coming from the sim, to avoid it being updated while calculating something
        self.ir_sdk.freeze_var_buffer_latest()

        # Update all telemetry
        self.timing_telemetry.update()
        self.fuel_telemetry.update()
        self.relative_telemetry.update()
