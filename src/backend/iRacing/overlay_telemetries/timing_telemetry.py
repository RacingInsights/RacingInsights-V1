import math
import statistics
from typing import List, Optional

from irsdk import IRSDK

from src.backend.iRacing.overlay_telemetry import OverlayTelemetry
from src.backend.iRacing.utils.zero_div import zero_div


class TimingTelemetry(OverlayTelemetry):
    """Implements all the relevant telemetry related to timing"""

    def __init__(self, ir_sdk: IRSDK):
        self.ir_sdk = ir_sdk

        self.time_left: float = 0.00
        self.last_lap_time: float = 0.00
        self.lap_time_list: List[Optional[float]] = []

        self.lap_count: int = 0
        self.new_lap: bool = False

    def update(self) -> None:
        """Updates the attribute values of the timing telemetry"""
        self.time_left = self.ir_sdk['SessionTimeRemain']
        self.new_lap = self.lap_count != self.ir_sdk['LapCompleted']  # Only true the first sample per lap

        if self.new_lap:
            self.last_lap_time = self.ir_sdk['LapLastLapTime']
            self.lap_time_list.append(self.last_lap_time)
            self.lap_count = self.ir_sdk['LapCompleted']

    @property
    def avg_lap_time(self) -> float:
        """Average lap time of the player"""
        return statistics.median(self.lap_time_list)

    @property
    def laps_to_finish_player(self) -> float:
        """Returns the predicted amount of laps that the player will do until the finish"""
        session_id = self.find_last_session_id()
        if not self.ir_sdk['SessionInfo']['Sessions'][session_id]['ResultsPositions']:
            return 0.0

        leader_car_idx = self.ir_sdk['SessionInfo']['Sessions'][session_id]['ResultsPositions'][0]['CarIdx']
        fastest_lap_leader = self.ir_sdk['SessionInfo']['Sessions'][session_id]['ResultsPositions'][0]['FastestTime']
        estimate_to_pos_leader = self.ir_sdk['CarIdxEstTime'][leader_car_idx]
        estimate_lap_time_leader = self.calculate_estimate_lap_time_leader(leader_car_idx=leader_car_idx)
        lap_progress_pct_leader = zero_div(estimate_to_pos_leader, estimate_lap_time_leader)
        live_laps_to_finish_leader = math.ceil(zero_div(self.time_left, fastest_lap_leader)) - lap_progress_pct_leader
        time_to_finish_leader = live_laps_to_finish_leader * estimate_lap_time_leader
        complete_laps_left_in_race = math.ceil(zero_div(time_to_finish_leader, self.avg_lap_time))
        return complete_laps_left_in_race - self.ir_sdk['CarIdxLapDistPct'][self.ir_sdk['DriverInfo']['DriverCarIdx']]

    def find_last_session_id(self) -> int:
        """
        Finds the last session id by checking for valid data starting from the last session until valid data is found
        Cannot simply take the last as iRacing already pre-populates these in case of officials
        """
        session_id = -1
        while True:
            if not self.ir_sdk['SessionInfo']['Sessions'][session_id]['ResultsPositions']:
                if abs(session_id) >= len(self.ir_sdk['SessionInfo']['Sessions']):
                    return session_id
                else:
                    session_id -= 1
            else:
                return session_id

    def calculate_estimate_lap_time_leader(self, leader_car_idx: int) -> float:
        """Returns the lap time of the session leader"""
        for driver in self.ir_sdk['DriverInfo']['Drivers']:
            if driver['CarIdx'] == leader_car_idx:
                return driver['CarClassEstLapTime']
