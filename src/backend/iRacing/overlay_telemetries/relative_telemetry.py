import logging
import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from irsdk import IRSDK

from src.backend.AWS.resources import DynamoDB, DynamoDBTable, TableNames
from src.backend.iRacing.overlay_telemetry import OverlayTelemetry
from src.frontend.utils.ri_event_handler import RIEventTypes, post_event, subscribe


class LappedState(Enum):
    BACKMARKER = auto()  # A car that is at least a lap down on the player
    LAPPING = auto()  # A car that is lapping the player
    SAMELAP = auto()  # Same lap as the player


class RelativeLocation(Enum):
    AHEAD = auto()
    BEHIND = auto()


@dataclass
class EstimationData:
    distance_normalized: List[float]
    estimate_time: List[float]
    resolution_normalized: float


@dataclass
class RelativeEntry:
    position: int
    car_nr: int
    driver_name: str
    license: str
    irating: int
    relative_time: float
    in_pits: bool  # Used to possibly filter out or indicate with grey
    is_player: bool
    lapped_state: LappedState  # Needed to indicate red, normal, blue colors in overlay
    car_id: int  # Just for finding player, not for displaying


class RelativeMode(Enum):
    NORMAL = auto()
    LITE = auto()


class RelativeDataLogger:
    """Class responsible for logging of the relative_time data in case it could not be received from DB"""
    km_to_m = 1000
    meters_per_sample = 50

    def __init__(self, ir_sdk: IRSDK):
        self.ir_sdk = ir_sdk
        self.data = EstimationData(
                distance_normalized=[(i + 1) * self.resolution_normalized for i in
                                     range(self.nr_estimation_samples)],
                estimate_time=[0.0] * self.nr_estimation_samples,
                resolution_normalized=self.resolution_normalized)

        # Normalized distances that were used as reference when storing previously
        self.reference_dist_normalized = [0.0] * self.nr_estimation_samples

    def log_relative_data(self):
        """Used when in LITE mode to gather the data that is to be sent to DB later to support NORMAL mode"""
        previous_dist_error = abs(self.reference_dist_normalized[self.index_in_estimation_list]
                                  - self.distance_normalized_here)

        current_dist_error = abs(self.player_distance_normalized
                                 - self.distance_normalized_here)

        # If current more accurate, overwrite the old data with new
        if current_dist_error < previous_dist_error:
            self.reference_dist_normalized[self.index_in_estimation_list] = self.player_distance_normalized
            self.data.estimate_time[self.index_in_estimation_list] = \
                (self.distance_normalized_here / self.player_distance_normalized) * self.player_estimate_time

        if self.logged_data_complete:
            # This notifies the listeners that the data has become available
            post_event(event_type=RIEventTypes.ESTIMATION_DATA_LOGGED, data=self.data)

    @property
    def logged_data_complete(self) -> bool:
        """
        Returns True if the logged data is complete, otherwise returns False
        :return:
        """
        if any(sample == 0 for sample in self.data.estimate_time):
            return False
        else:
            logging.info("Logged data is complete!")
            return True

    @property
    def distance_normalized_here(self) -> float:
        return self.data.distance_normalized[self.index_in_estimation_list]

    @property
    def player_distance_normalized(self) -> float:
        return self.ir_sdk["CarIdxLapDistPct"][self.player_car_id]

    @property
    def player_estimate_time(self) -> float:
        return self.ir_sdk["CarIdxEstTime"][self.player_car_id]

    @property
    def index_in_estimation_list(self) -> int:
        return max(round(self.player_distance_normalized / self.resolution_normalized) - 1, 0)

    @property
    def nr_estimation_samples(self) -> int:
        return math.ceil(self.track_length_m / self.meters_per_sample)

    @property
    def resolution_normalized(self) -> float:
        return 1 / self.nr_estimation_samples

    @property
    def track_length_m(self) -> float:
        return float(self.ir_sdk["WeekendInfo"]["TrackLengthOfficial"][0:-4]) * self.km_to_m

    @property
    def player_car_id(self) -> Optional[int]:
        return self.ir_sdk["DriverInfo"]["DriverCarIdx"]


class RelativeTelemetry(OverlayTelemetry):
    def __init__(self, ir_sdk: IRSDK, dynamo_db_resource: DynamoDB):
        self.ir_sdk = ir_sdk

        # The telemetry that serves as output
        self.sorted_relative_entries: List[Optional[RelativeEntry]] = []

        # Estimation data attributes
        self.estimation_data_checked = False  # Flag whether the DB was queried for the relevant data
        self.estimation_data: Optional[EstimationData] = None
        self.dynamo_db_table = DynamoDBTable(dynamo_db=dynamo_db_resource, name=TableNames.RELATIVE.value)
        self.relative_data_logger: Optional[RelativeDataLogger] = None
        # Event handling to receive estimation data from logger
        subscribe(event_type=RIEventTypes.ESTIMATION_DATA_LOGGED, fn=self.estimation_data_logged_event_handler)

    def update(self) -> None:
        """Updates the attribute values of the relative_time telemetry"""
        if not self.player_car_id:
            return
        if not self.player_car_class_id:
            return

        # The check is to be performed after car class is available!
        if not self.estimation_data_checked:
            self.check_estimation_data()
            self.estimation_data_checked = True

        if self.mode == RelativeMode.LITE:
            self.relative_data_logger.log_relative_data()

        self.sorted_relative_entries = self.get_sorted_relative_entries()

    def check_estimation_data(self) -> None:
        self.estimation_data = self.get_estimation_data()
        if not self.estimation_data:
            self.relative_data_logger = RelativeDataLogger(ir_sdk=self.ir_sdk)

    def get_estimation_data(self) -> Optional[EstimationData]:
        """
        Queries the AWS Dynamo DB Table for the estimate data of that track and car class combo.
        Example output:
            {
                "DistancePct": [],
                "EstimateTime": [],
                "ResolutionPct": 0.0024154589371980675
            }
        """
        data = self.dynamo_db_table.get_item(key={'track_id': self.track_id},
                                             projection_expression="EstimationData.#key_name,TrackVersion",
                                             expression_attr_name={'#key_name': str(self.player_car_class_id)})

        if self.is_data_valid(data=data):
            estimation_dict = data["EstimationData"][f"{self.player_car_class_id}"]
            estimation_data = EstimationData(distance_normalized=estimation_dict["DistancePct"],
                                             estimate_time=estimation_dict["EstimateTime"],
                                             resolution_normalized=estimation_dict["ResolutionPct"])
            return estimation_data

    def is_data_valid(self, data):
        """
        Validates whether the relative_time estimation data is available, valid and up-to-date. Returns False otherwise.
        """
        if not data:
            return False

        if data["TrackVersion"] != self.ir_sdk["WeekendInfo"]["TrackVersion"]:
            logging.warning("Data was returned from db but the 'Track Version' in the database is outdated")
            return False

        try:
            data["EstimationData"]
        except KeyError:
            logging.info("The estimation data was not provided for this car class")
            return False
        else:
            logging.info("The data that was returned from the db is checked and deemed valid.")
            return True

    def estimation_data_logged_event_handler(self, estimation_data: EstimationData):
        """This is tied to the ESTIMATION_DATA_LOGGED event, posted by the relative_data_logger"""
        self.estimation_data = estimation_data

    @property
    def mode(self) -> RelativeMode:
        if self.estimation_data:
            return RelativeMode.NORMAL
        else:
            return RelativeMode.LITE

    @property
    def track_id(self) -> int:
        return self.ir_sdk["WeekendInfo"]["TrackID"]

    @property
    def player_car_id(self) -> Optional[int]:
        return self.ir_sdk["DriverInfo"]["DriverCarIdx"]

    @property
    def player_car_class_id(self) -> Optional[int]:
        return self.ir_sdk["CarIdxClass"][self.player_car_id]

    @property
    def player_distance_normalized(self) -> float:
        return self.ir_sdk["CarIdxLapDistPct"][self.player_car_id]

    @property
    def player_lap_time(self) -> float:
        return self.ir_sdk['DriverInfo']['DriverCarEstLapTime']

    @property
    def player_laps(self) -> float:
        return self.ir_sdk['CarIdxLap'][self.player_car_id]

    @property
    def driver_results(self):
        return self.ir_sdk['DriverInfo']['Drivers']

    def get_sorted_relative_entries(self) -> List[RelativeEntry]:
        relative_entry_list = self.get_relative_entry_list()

        # Sort the relative_time list based on relative_time time
        sorted_relative_entries = sorted(relative_entry_list, key=lambda k: k.relative_time, reverse=True)

        return sorted_relative_entries

    def get_relative_entry_list(self) -> List[RelativeEntry]:
        """Creates the unsorted list of all the drivers and their data structured in the RelativeEntry format"""
        relative_entry_list: List[RelativeEntry] = []

        for idx in range(len(self.ir_sdk['CarIdxTireCompound'])):
            # Filter out ids that are not actually valid
            if self.ir_sdk['CarIdxLapDistPct'][idx] == -1 or self.ir_sdk['CarIdxTireCompound'][idx] == -1:
                continue

            # TODO: Check if the validation for list size is needed here as in original?
            # TODO: I think this filtered out actual drivers?
            # if i >= len(driver_results):
            #     # Exit if list index out of range of the results
            #     continue

            # Get the input data for relative entry
            distance_normalized = self.ir_sdk['CarIdxLapDistPct'][idx]
            driver_dict = self.get_driver_dict(car_id=idx)
            relative_time = self.get_relative_time(distance_normalized=distance_normalized,
                                                   lap_time_other=driver_dict["CarClassEstLapTime"])
            in_pits = self.ir_sdk['CarIdxOnPitRoad'][idx]
            lapped_state = self.get_lapped_state(laps_other=self.ir_sdk['CarIdxLap'][idx],
                                                 distance_normalized=distance_normalized)
            class_position = self.ir_sdk['CarIdxClassPosition'][idx]

            # Create a relative entry instance
            relative_entry = RelativeEntry(position=class_position,
                                           car_nr=driver_dict["CarNumberRaw"],
                                           driver_name=driver_dict["UserName"],
                                           license=driver_dict["LicString"],
                                           irating=driver_dict["IRating"],
                                           relative_time=relative_time,
                                           in_pits=in_pits,
                                           is_player=bool(idx == self.player_car_id),
                                           lapped_state=lapped_state,
                                           car_id=idx
                                           )

            relative_entry_list.append(relative_entry)
        return relative_entry_list

    @property
    def player_id_in_sorted(self) -> int:
        # Store the index for the player in this list, such that the UI can center itself around this index later
        for i, entry in enumerate(self.sorted_relative_entries):
            if entry.car_id == self.player_car_id:
                return i
        return 0

    def get_driver_dict(self, car_id: int) -> dict:
        for driver in self.driver_results:
            if driver["CarIdx"] == car_id:
                return driver

    def get_relative_time(self, distance_normalized: float, lap_time_other: float) -> float:
        if self.mode == RelativeMode.NORMAL:
            return self.calculate_relative_time_normal(distance_normalized=distance_normalized)
        if self.mode == RelativeMode.LITE:
            return self.calculate_relative_time_lite(distance_normalized=distance_normalized,
                                                     lap_time_other=lap_time_other)

    def calculate_relative_time_normal(self, distance_normalized: float) -> float:
        """
        Method that uses the estimation data to calculate the relative_time time between other(input) and the player
        NOTE: An assumption is made here that the relative_time time is based on the estimate time of the player
        """
        relative_location = self.get_relative_location(distance_normalized=distance_normalized)

        est_to_other = self.get_estimate_time_to_(distance_normalized)
        est_to_player = self.get_estimate_time_to_(self.player_distance_normalized)

        if relative_location == RelativeLocation.AHEAD:
            if distance_normalized < self.player_distance_normalized:  # Other <- SF <- Player
                time_player_to_sf = self.player_lap_time - est_to_player
                relative_time = time_player_to_sf + est_to_other
            else:  # Other <- Player <- SF
                relative_time = est_to_other - est_to_player

        else:  # relative_location == RelativeLocation.BEHIND:
            if self.player_distance_normalized < distance_normalized:  # Player <- SF <- Other
                time_other_to_sf = self.player_lap_time - est_to_other
                relative_time = est_to_player + time_other_to_sf
            else:  # Player <- Other <- SF
                relative_time = est_to_player - est_to_other
        return relative_time

    def calculate_relative_time_lite(self, distance_normalized: float, lap_time_other: float) -> float:
        """
        Method that doesn't rely on the estimation data for calculating the relative_time.
        This is used until the estimation data is available.
        """

        difference = abs(distance_normalized - self.player_distance_normalized)

        if difference > 0.5:
            relative_progress_diff = 1 - difference
            relative_time = - relative_progress_diff * self.player_lap_time
        else:
            relative_progress_diff = difference
            relative_time = relative_progress_diff * lap_time_other

        if distance_normalized < self.player_distance_normalized:
            relative_time = - relative_time
        return relative_time

    def get_relative_location(self, distance_normalized: float) -> RelativeLocation:
        """Determines whether the given (normalized distance) is AHEAD or BEHIND the player"""
        difference = distance_normalized - self.player_distance_normalized

        if difference > 0:
            if difference < 0.5:
                return RelativeLocation.AHEAD
            else:
                return RelativeLocation.BEHIND
        elif difference == 0:
            return RelativeLocation.AHEAD
        else:
            if abs(difference) > 0.5:
                return RelativeLocation.AHEAD
            else:
                return RelativeLocation.BEHIND

    def get_estimate_time_to_(self, distance_normalized: float) -> float:
        """
        Returns the value that represents the time it would take the PLAYER to reach that position
        on track (aka normalized distance), measured starting from the start finish line
        :return:
        """
        # Calculate the REAL index (float) that this location would have if possible to index with floats
        # -1 because 0 not included in data
        location_in_list = max((distance_normalized / self.estimation_data.resolution_normalized) - 1, 0)

        # Get the 2 int indices that bound this float index
        # # min to assure it doesn't go outside
        upper_id = min(math.ceil(location_in_list), len(self.estimation_data.estimate_time) - 1)
        lower_id = math.floor(location_in_list)

        # Calculate the values in these indices
        upper_value = self.estimation_data.estimate_time[upper_id]
        lower_value = self.estimation_data.estimate_time[lower_id]

        # Interpolate linearly inbetween these bounding values based on the float index offset
        offset = location_in_list % 1
        estimate_to_distance_normalized = lower_value + (upper_value - lower_value) * offset

        return estimate_to_distance_normalized

    def get_lapped_state(self, distance_normalized: float, laps_other: int) -> LappedState:
        relative_location = self.get_relative_location(distance_normalized)
        if relative_location == RelativeLocation.BEHIND:
            if laps_other > self.player_laps:
                return LappedState.LAPPING
            if laps_other == self.player_laps and distance_normalized < self.player_distance_normalized:
                return LappedState.LAPPING
            if laps_other < self.player_laps - 1:
                return LappedState.BACKMARKER
            if laps_other < self.player_laps and distance_normalized < self.player_distance_normalized:
                return LappedState.BACKMARKER
            else:
                return LappedState.SAMELAP
        else:
            if laps_other < self.player_laps:
                return LappedState.BACKMARKER
            if laps_other == self.player_laps and distance_normalized < self.player_distance_normalized:
                return LappedState.BACKMARKER
            if laps_other > self.player_laps + 1:
                return LappedState.LAPPING
            if laps_other > self.player_laps and distance_normalized < self.player_distance_normalized:
                return LappedState.LAPPING
            else:
                return LappedState.SAMELAP
