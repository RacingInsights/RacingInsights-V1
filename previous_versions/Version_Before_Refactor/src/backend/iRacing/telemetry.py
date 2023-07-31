import http.client
import logging
import math
import statistics as stats

from irsdk import IRSDK

from previous_versions.Version_Before_Refactor.src.backend.aws.relative_estimation_data import RelativeEstimationDataDBLink
from previous_versions.Version_Before_Refactor.src.backend.iRacing.state import State
from previous_versions.Version_Before_Refactor.src.backend.utils.exception_handler import exception_handler
from previous_versions.Version_Before_Refactor.src.backend.utils.zero_div import zero_div


class Telemetry:
    """
    Class that contains all the telemetry data
    """

    def __init__(self, state: State, ir_sdk: IRSDK, estimation_data=None, relative_estimation_data=None,
                 data_for_db=None, track_id=None):
        # Logging data
        self.flag_player_car_id_warning = False
        self.player_location_in_sorted: int | None = None
        self.meters_per_sample: float | None = None
        self.nr_estimate_samples = None
        self.current_track_id = track_id
        self.relative_mode = None
        self.logged_resolution_pct = None
        self.logged_current_reference_pct_stored: list[float] = []
        self.logged_estimate_time: list[float] = []
        self.logged_distance_pct: list[float] = []
        self.initialized_logged_relative_data = False
        self.data_for_db = data_for_db
        self.laps_left_in_race = 0
        self.leader_laps_completed = 0
        self.time_left = 0
        self.fuel = 0
        self.cons = 0
        self.consumption_list = []
        self.avg_cons = 0
        self.laps_left_current = 0
        self.laps_left_extra = 0
        self.target_cons_current = 0
        self.target_cons_extra = 0
        self.refuel = 0
        self.laps = 0
        self.lap_time_list = []
        self.laps_ir = 0  # Lap count as by iRacing, only used to check for crossing the start finish line,
        # not for lap count
        self.prev_lap_fuel = 0
        self.last_lap_time = 0
        self.avg_lap_time = 0
        self.laps_refuel = 0
        self.relative_data = None
        self.player_location_in_sorted: int
        self.session_type: str = "Practice"
        self.target_finish = 0
        self.estimate_data_checked = False
        self.car_class_id_player = None
        self.player_car_id = None
        self.ir_sdk = ir_sdk
        self.state = state
        self.estimation_data = estimation_data

        if not relative_estimation_data:
            self.relative_estimation_data_db_link = RelativeEstimationDataDBLink()
        else:
            self.relative_estimation_data_db_link = relative_estimation_data  # Here to keep the link (linked in main())

        logging.info("Initialized a Telemetry instance")

    def update(self):
        """
        Periodically called method that updates the telemetry attributes
        :return:
        """
        # capture the previous state instance in a temporary variable for comparison
        previous_state_on_track = self.state.on_track

        try:
            self.ir_sdk.freeze_var_buffer_latest()  # freeze buffer with live telemetry
        except http.client.IncompleteRead as e:
            logging.exception(e)
            return  # Do not continue with this telemetry update as the state could not be initialized
        except AttributeError as e:
            # This occurs when iracing not connected. It's a bug in irsdk
            pass

        try:
            current_state = self.state.update_state(self.ir_sdk)
        except Exception as e:
            logging.exception(e)

        # If not driving, no need to display anything
        if not current_state.on_track:
            self.state = current_state

        # If driving and previously not, new session was started!
        elif not previous_state_on_track and current_state.on_track:
            logging.info("started a new session, telemetry (re-)initialized")

            # Starting a new session? Telemetry resets
            self.__init__(state=self.state, ir_sdk=self.ir_sdk,
                          relative_estimation_data=self.relative_estimation_data_db_link,
                          estimation_data=self.estimation_data,
                          data_for_db=self.data_for_db,
                          track_id=self.current_track_id)

            self.player_car_id = self.ir_sdk['DriverInfo']['DriverCarIdx']
            self.car_class_id_player = self.ir_sdk['CarIdxClass'][self.player_car_id]

            # Set the fuel variables
            if self.ir_sdk['FuelLevel']:
                self.fuel = self.ir_sdk['FuelLevel']

            if self.ir_sdk['SessionTimeRemain']:
                self.time_left = self.ir_sdk['SessionTimeRemain']

            if self.ir_sdk['SessionInfo']['Sessions']:
                session_id = self.find_last_session_id(self.ir_sdk)

                if self.ir_sdk['SessionInfo']['Sessions'][session_id]['SessionType']:  # Set the session type
                    self.session_type = self.ir_sdk['SessionInfo']['Sessions'][session_id]['SessionType']

            self.prev_lap_fuel = self.fuel

            if not self.estimation_data:
                # Load the estimation data at the start of the session(from AWS DynamoDB), if not already logged
                self.estimation_data, self.current_track_id = self.get_relative_estimation_data()

        # other scenarios remaining: driving and not started a new session
        else:
            laps = self.laps_ir
            self.update_live_telemetry()
            self.update_relative_telemetry()

            if laps < self.laps_ir:  # Finished a lap
                self.update_lap_telemetry()

    def update_live_telemetry(self):
        """
        Data that is updated live
        :return:
        """
        # Self:
        self.fuel = self.ir_sdk['FuelLevel']
        self.laps_ir = self.ir_sdk['LapCompleted']

        # Live data needed to determine refuel amount
        self.time_left = self.ir_sdk['SessionTimeRemain']
        self.last_lap_time = self.ir_sdk['LapLastLapTime']

    @exception_handler
    def update_lap_telemetry(self):
        """
        Data that is only updated once a lap (when crossing the start finish line)
        :return:
        """
        # Lap time data
        self.lap_time_list.append(self.last_lap_time)
        self.avg_lap_time = stats.median(self.lap_time_list)

        # Fuel data
        self.cons = self.prev_lap_fuel - self.fuel
        self.consumption_list.append(self.cons)
        self.avg_cons = stats.median(self.consumption_list)
        laps_left_on_fuel = zero_div(x=self.fuel, y=self.avg_cons)

        self.laps_left_current = math.floor(laps_left_on_fuel)
        self.laps_left_extra = math.ceil(laps_left_on_fuel)

        self.target_cons_current = zero_div(x=self.fuel - 0.3, y=self.laps_left_current)
        self.target_cons_extra = zero_div(x=self.fuel - 0.3, y=self.laps_left_extra)

        self.laps_left_in_race = self.calculate_laps_left_in_race()  # This throws exceptions in some cases

        self.target_finish = zero_div(x=self.fuel, y=self.laps_left_in_race)

        self.laps_refuel = max(self.laps_left_in_race - laps_left_on_fuel + 0.15, 0)

        self.refuel = self.laps_refuel * self.avg_cons

        logging.info("self.time_left: %s", self.time_left)
        logging.info("self.last_lap_time: %s", self.last_lap_time)
        logging.info("laps_left_on_fuel: %s", laps_left_on_fuel)
        logging.info("laps_refuel: %s", self.laps_refuel)
        logging.info("refuel: %s", self.refuel)

        self.prev_lap_fuel = self.fuel

    def calculate_laps_left_in_race(self):
        """
        Calculates the laps left in the race for the player based on the time to finish for the current leader
        :return:
        """
        session_id = self.find_last_session_id(self.ir_sdk)
        leader_car_idx = self.ir_sdk['SessionInfo']['Sessions'][session_id]['ResultsPositions'][0]['CarIdx']
        logging.info("leader_car_idx: %s", leader_car_idx)
        fastest_lap_leader = self.ir_sdk['SessionInfo']['Sessions'][session_id]['ResultsPositions'][0]['FastestTime']
        logging.info("fastest_lap_leader: %s", fastest_lap_leader)
        estimate_to_pos_leader = self.ir_sdk['CarIdxEstTime'][leader_car_idx]
        logging.info("estimate_to_pos_leader: %s", estimate_to_pos_leader)
        estimate_lap_time_leader = self.calculate_estimate_lap_time_leader(leader_car_idx=leader_car_idx)
        logging.info("estimate_lap_time_leader: %s", estimate_lap_time_leader)
        lap_progress_pct_leader = zero_div(estimate_to_pos_leader, estimate_lap_time_leader)
        logging.info("lap_progress_pct_leader: %s", lap_progress_pct_leader)
        live_laps_to_finish_leader = math.ceil(zero_div(self.time_left, fastest_lap_leader)) - lap_progress_pct_leader
        logging.info("live_laps_to_finish_leader: %s", live_laps_to_finish_leader)
        time_to_finish_leader = live_laps_to_finish_leader * estimate_lap_time_leader
        logging.info("time_to_finish_leader: %s", time_to_finish_leader)
        laps_left_in_race = math.ceil(zero_div(time_to_finish_leader, self.avg_lap_time))
        logging.info("laps_left_in_race: %s", laps_left_in_race)
        return laps_left_in_race

    def calculate_estimate_lap_time_leader(self, leader_car_idx):
        for driver in self.ir_sdk['DriverInfo']['Drivers']:
            if driver['CarIdx'] == leader_car_idx:
                return driver['CarClassEstLapTime']

    def update_relative_telemetry(self):
        """
        Calculates the data needed for populating a relative time overlay (F3 blackbox in iRacing).

        self.relative_data: [{},{},{},{},...,{}], list of dicts where each dict is a car on track
        First element is list is the car the furthest ahead of the player.
        The player is also in this list (centered in case of equal amount of cars in front and behind).
        Last element is the car the furthest behind the player.

        the relative entry dict {} consists of the following keys:
        "relative","car_nr","driver_name","car_brand","irating","ir_license","car_id","class_position","in_pit"

        :return:
        """
        if self.ir_sdk['DriverInfo']['DriverCarIdx'] is None:
            if not self.flag_player_car_id_warning:
                logging.warning("['DriverInfo']['DriverCarIdx'] not available")  # This could occur when in test server
                self.flag_player_car_id_warning = True
            return

        if not self.player_car_id:
            self.player_car_id = self.ir_sdk['DriverInfo']['DriverCarIdx']

        if not self.car_class_id_player and self.ir_sdk['CarIdxClass']:
            self.car_class_id_player = self.ir_sdk['CarIdxClass'][self.player_car_id]

        if not self.estimation_data and self.car_class_id_player and not self.estimate_data_checked:
            self.estimation_data, self.current_track_id = self.get_relative_estimation_data()

        prev_mode = self.relative_mode

        if self.estimation_data:
            self.relative_mode = "NORMAL"
        else:
            self.relative_mode = "LITE"
            self.log_relative_data()  # Once the logged data is complete, it will populate self.estimation_data

        sorted_relative_entries, player_location_in_sorted = self.calculate_relative_normal()

        if prev_mode != self.relative_mode:
            logging.info(f"Now using {self.relative_mode} relative mode")

        self.relative_data = sorted_relative_entries
        self.player_location_in_sorted = player_location_in_sorted

    def calculate_relative_normal(self) -> (list[dict[str,]], int):

        driver_results = self.ir_sdk['DriverInfo']['Drivers']

        relative_entry_list = self.create_relative_entry_list(driver_results)

        # Sort the relative list based on relative time
        sorted_relative_entries = sorted(relative_entry_list, key=lambda k: k['relative'], reverse=True)

        player_location_in_sorted = self.find_player_location_in_sorted(sorted_relative_entries)

        return sorted_relative_entries, player_location_in_sorted

    def create_relative_entry_list(self, driver_results) -> list[dict[str,]]:
        lap_time_player = self.ir_sdk['DriverInfo']['DriverCarEstLapTime']
        lap_dist_pct = self.ir_sdk['CarIdxLapDistPct']

        lap_dist_pct_player = lap_dist_pct[self.player_car_id]

        tires_fitted = [(int(tire) != -1) for tire in self.ir_sdk['CarIdxTireCompound']]

        relative_entry_list = []  # list of relative entries, each entry is dict

        for i, dist_pct_entry in enumerate(lap_dist_pct):
            if dist_pct_entry == -1:
                # If others not driving, hence -1, they will be filtered out later anyway, no need to process
                continue

            if i >= len(driver_results):
                # Exit if list index out of range of the results
                continue

            # Get the correct driver. Note: iracing makes jumps in the car ids (affects driver_results)!
            driver = self.get_correct_driver(driver_results=driver_results, correct_id=i)

            if self.relative_mode == "NORMAL":
                relative_time = self.calculate_relative_time_normal(pct_other=dist_pct_entry,
                                                                    pct_player=lap_dist_pct[self.player_car_id],
                                                                    lap_time_player=lap_time_player)
            else:  # "LITE"
                relative_time = self.calculate_relative_time_lite(lap_progress_pct_other=dist_pct_entry,
                                                                  lap_progress_pct_player=lap_dist_pct_player,
                                                                  est_lap_time_other=driver['CarClassEstLapTime'],
                                                                  est_lap_time_player=lap_time_player)

            entry_tires_fitted = tires_fitted[i]

            relative_entry = self.filter_and_get_relative_entry(relative_time, driver, entry_tires_fitted, index=i)

            if relative_entry:
                relative_entry_list.append(relative_entry)

        return relative_entry_list

    @staticmethod
    def get_correct_driver(driver_results, correct_id):
        for driver in driver_results:
            if driver["CarIdx"] == correct_id:
                return driver

    def find_player_location_in_sorted(self, sorted_relative_entry) -> int:
        player_location_in_sorted = 0
        # Store the index for the player in this list, such that the UI can center itself around this index later
        for i, entry in enumerate(sorted_relative_entry):
            if entry["car_id"] == self.player_car_id:
                player_location_in_sorted = i

        return player_location_in_sorted

    def calculate_relative_time_normal(self, pct_other: float, pct_player: float, lap_time_player: float):
        """
        NOTE: An assumption is made here that the relative time is based on the estimate time of the player
        :param pct_other:
        :param pct_player:
        :param lap_time_player:
        :return:
        """
        estimate_other_pos_player = self.get_estimate_to_pos_pct(pct_other)
        estimate_to_pos_player = self.get_estimate_to_pos_pct(pct_player)
        relative_location = self.is_other_ahead_or_behind(pct_other, pct_player)

        relative_time = None

        if relative_location == "ahead":
            if pct_other < pct_player:  # This would mean that the start finish (sf) line
                # is between the other and the player
                time_to_sf_line = lap_time_player - estimate_to_pos_player
                time_sf_to_other = estimate_other_pos_player

                relative_time = time_to_sf_line + time_sf_to_other
            else:
                relative_time = estimate_other_pos_player - estimate_to_pos_player

        if relative_location == "behind":
            if pct_player < pct_other:  # This would mean that the start finish line
                # is between the player and the other
                time_to_sf_line_other = lap_time_player - estimate_other_pos_player
                time_sf_to_player = estimate_to_pos_player

                relative_time = -(time_to_sf_line_other + time_sf_to_player)
            else:
                relative_time = -(estimate_to_pos_player - estimate_other_pos_player)

        # Last post-processing step of relative time, to put ahead or behind based on lap time, instead of lap dist pct
        if abs(relative_time) > lap_time_player / 2:
            if relative_time < 0:
                relative_time += lap_time_player
            else:
                relative_time = -(lap_time_player - relative_time)

        return relative_time

    @staticmethod
    def calculate_relative_time_lite(lap_progress_pct_other, lap_progress_pct_player, est_lap_time_other,
                                     est_lap_time_player) -> float:

        lpp_diff = abs(lap_progress_pct_other - lap_progress_pct_player)

        if lpp_diff > 0.5:
            relative_progress_diff = 1 - lpp_diff
            rel_time = - relative_progress_diff * est_lap_time_player
        else:
            relative_progress_diff = lpp_diff
            rel_time = relative_progress_diff * est_lap_time_other

        if lap_progress_pct_other < lap_progress_pct_player:
            rel_time = - rel_time

        return rel_time

    def filter_and_get_relative_entry(self, rel_time, driver, entry_tires_fitted, index) -> dict | None:
        """
        Only returns a relative entry for valid data (player, and people in sim).
        Hence, it filters out cars that are not in the sim.
        The output of this is a dictionary including all necessary information for that relative entry.
        :param rel_time:
        :param driver:
        :param entry_tires_fitted:
        :param index:
        :return:
        """
        entry_in_pit = self.ir_sdk['CarIdxOnPitRoad'][index]
        entry_laps = self.ir_sdk['CarIdxLap'][index]
        entry_class_position = self.ir_sdk['CarIdxClassPosition'][index]

        if driver['CarIdx'] == self.player_car_id:
            relative_entry = self.populate_relative_entry_fields(rel_time, driver, entry_class_position,
                                                                 entry_in_pit, entry_laps)
            relative_entry["is_player"] = True

        elif entry_tires_fitted:  # Only add those who have tires equipped (filters out ppl who are not driving xD)
            relative_entry = self.populate_relative_entry_fields(rel_time, driver, entry_class_position,
                                                                 entry_in_pit, entry_laps)
            relative_entry["is_player"] = False

        else:
            relative_entry = None

        return relative_entry

    @staticmethod
    def populate_relative_entry_fields(rel_time, driver, entry_class_position, entry_in_pit, entry_laps):
        relative_entry = {"relative": rel_time,
                          "car_nr": driver['CarNumberRaw'],
                          "driver_name": driver['UserName'],
                          "car_brand": driver['CarScreenNameShort'],
                          "irating": driver['IRating'],
                          "ir_license": driver['LicString'],
                          "license_color": driver['LicColor'],
                          "car_id": driver['CarIdx'],
                          "class_position": entry_class_position,
                          "car_class_name": driver['CarClassShortName'],
                          "car_class_color": driver['CarClassColor'],
                          "in_pit": entry_in_pit,
                          "laps": entry_laps
                          }
        return relative_entry

    @staticmethod
    def is_other_ahead_or_behind(dist_pct_1, dist_pct_2) -> str:
        """
        Determines whether entry 1 is ahead or behind entry 2 purely based on lap distance pct.
        This does not necessarily correspond with ahead or behind when considering the lap time.
        To get ahead or behind based on lap time, an additional post-processing step is required.
        :param dist_pct_1:
        :param dist_pct_2:
        :return:
        """
        difference = dist_pct_1 - dist_pct_2
        if difference > 0:
            if difference < 0.5:
                return "ahead"
            else:
                return "behind"
        elif difference == 0:
            return "ahead"
        else:
            if abs(difference) > 0.5:
                return "ahead"
            else:
                return "behind"

    @staticmethod
    def find_last_session_id(ir_sdk) -> int:
        """
        Finds the last session log_id by checking for valid data starting from the last session until valid data is found
        :param ir_sdk:
        :return:
        """
        session_id = -1
        while True:
            if not ir_sdk['SessionInfo']['Sessions'][session_id]['ResultsPositions']:
                if abs(session_id) >= len(ir_sdk['SessionInfo']['Sessions']):
                    return session_id
                else:
                    session_id -= 1
            else:
                return session_id

    def get_estimate_to_pos_pct(self, pos_pct) -> float:
        """
        Returns the value that represents the time it would take the player to reach that position
        on track, measured starting from the start finish line
        :param pos_pct:
        :return:
        """
        data = self.estimation_data
        resolution_pct = data["ResolutionPct"]

        location_in_list = max((pos_pct / resolution_pct) - 1, 0)  # -1 because 0 not included in data
        upper_id = min(math.ceil(location_in_list),
                       len(data["EstimateTime"]) - 1)  # min to assure it doesn't go outside
        lower_id = math.floor(location_in_list)

        upper_value = data["EstimateTime"][upper_id]
        lower_value = data["EstimateTime"][lower_id]

        offset = location_in_list % 1

        estimate_to_pos_pct = lower_value + (upper_value - lower_value) * offset

        return estimate_to_pos_pct

    def get_relative_estimation_data(self, dummy_file=None) -> dict | tuple[None, None]:
        """
        Loads the estimation data required for the calculation of the relative time.
        Returns None if no valid estimation data is available
        This data is part of the AWS dynamoDB table with name: Relative_Estimation_Data
        :return:
        """
        if not self.ir_sdk.is_initialized:
            return None, None  # If not connected to iRacing sdk, then cannot yet determine which data to get

        self.estimate_data_checked = True  # Such that it will not keep calling the database to check

        # try:
        #     if dummy_file:
        #         with open(dummy_file) as f:
        #             data = json.load(f)
        #     else:
        #         with open('../estimation_data.json') as f:
        #             data = json.load(f)
        #
        # except FileNotFoundError:
        #     logging.info('The estimation data file was not found')
        #     return None, None

        current_track_id = self.ir_sdk["WeekendInfo"]["TrackID"]

        # Get the data from the AWS DynamoDB Table
        data = self.relative_estimation_data_db_link.get_relative_estimation_data(track_id=current_track_id,
                                                                                  car_class=self.car_class_id_player)

        valid = self.check_is_estimation_data_valid(data=data)

        if valid:
            estimation_data = data["EstimationData"][f"{self.car_class_id_player}"]
            return estimation_data, current_track_id
        else:
            return None, None

    def check_is_estimation_data_valid(self, data):
        """
        Validates whether the relative estimation data is available, valid and up-to-date. Returns False otherwise.
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

    def log_relative_data(self) -> None:
        """
        Adds the current data to the logged data.
        If the logging is completed: sets self.estimation_data to this logged data
        :return:
        """
        if not self.initialized_logged_relative_data:
            self.init_logged_relative_data()

        current_estimate_dist_pct = self.ir_sdk['CarIdxLapDistPct'][self.player_car_id]
        id_in_estimate_list = self.calculate_id_in_estimate_list(current_estimate_dist_pct)
        current_estimate_time = self.ir_sdk["CarIdxEstTime"][self.player_car_id]

        self.add_data_to_logged_estimate_lists(current_estimate_dist_pct, current_estimate_time, id_in_estimate_list)

        logged_data_complete = self.is_logged_data_complete()

        if logged_data_complete:
            self.set_logged_data_as_estimation_data()
            self.set_logged_data_as_data_for_db()

    def add_data_to_logged_estimate_lists(self, estimate_dist_pct, estimate_time, id_in_estimate_list):
        """
        Adds the data to the logged lists if it is an (accuracy)improvement over the currently available data in that log_id
        :param estimate_dist_pct:
        :param estimate_time:
        :param id_in_estimate_list:
        :return:
        """
        # Determine if this data is more accurate than previous reference data
        dist_pct_difference_previously = \
            abs(
                    self.logged_current_reference_pct_stored[id_in_estimate_list]
                    - self.logged_distance_pct[id_in_estimate_list]
            )
        dist_pct_difference_now = abs(estimate_dist_pct - self.logged_distance_pct[id_in_estimate_list])

        current_data_more_accurate: bool = dist_pct_difference_previously > dist_pct_difference_now

        if current_data_more_accurate:
            # If more accurate, use the data
            self.logged_current_reference_pct_stored[id_in_estimate_list] = estimate_dist_pct

            time_to_be_logged = (self.logged_distance_pct[id_in_estimate_list] / estimate_dist_pct) * estimate_time

            self.logged_estimate_time[id_in_estimate_list] = time_to_be_logged

    def init_logged_relative_data(self) -> None:
        if not self.logged_resolution_pct:
            self.logged_resolution_pct, self.nr_estimate_samples = self.calculate_resolution_pct()

        if not self.logged_distance_pct:
            for i in range(self.nr_estimate_samples):
                self.logged_distance_pct.append((i + 1) * self.logged_resolution_pct)

        if not self.logged_estimate_time:
            self.logged_estimate_time = [0] * self.nr_estimate_samples

        if not self.logged_current_reference_pct_stored:
            self.logged_current_reference_pct_stored = [0] * self.nr_estimate_samples

        self.initialized_logged_relative_data = True

    def calculate_resolution_pct(self) -> tuple[float, int]:
        km_to_m = 1000
        track_length_m = float(self.ir_sdk["WeekendInfo"]["TrackLengthOfficial"][0:-4]) * km_to_m

        self.meters_per_sample = 50
        nr_samples = math.ceil(track_length_m / self.meters_per_sample)
        resolution_pct = 1 / nr_samples

        return resolution_pct, nr_samples

    def calculate_id_in_estimate_list(self, estimate_dist_pct) -> int:
        return max(round(estimate_dist_pct / self.logged_resolution_pct) - 1, 0)

    def is_logged_data_complete(self) -> bool:
        """
        Returns True if the logged data is complete, otherwise returns False
        :return:
        """
        if any(sample == 0 for sample in self.logged_estimate_time):
            return False
        else:
            logging.info("Logged data is complete!")
            return True

    def set_logged_data_as_estimation_data(self):
        """
        This method is called when the logged data is complete, and it sets this as the current estimation data
        :return:
        """
        self.estimation_data = \
            {
                "DistancePct": self.logged_distance_pct,
                "EstimateTime": self.logged_estimate_time,
                "ResolutionPct": self.logged_resolution_pct
            }

        self.current_track_id = self.ir_sdk["WeekendInfo"]["TrackID"]

    def set_logged_data_as_data_for_db(self):
        self.data_for_db = \
            {
                "TrackDisplayName": self.ir_sdk["WeekendInfo"]["TrackDisplayName"],
                "TrackLengthOfficial": self.ir_sdk["WeekendInfo"]["TrackLengthOfficial"],
                "TrackConfigName": self.ir_sdk["WeekendInfo"]["TrackConfigName"],
                "TrackVersion": self.ir_sdk["WeekendInfo"]["TrackVersion"],
                "EstimationData":
                    {
                        f"{self.car_class_id_player}": self.estimation_data
                    }
            }

    def send_logged_data_to_db(self):
        """
        Method should send the currently logged data to database.
        NOTE: Currently locally storing the data in a json
        :return:
        """
        if self.data_for_db:  # Only send when data was made available before
            self.relative_estimation_data_db_link.send_relative_estimation_data(track_id=self.current_track_id,
                                                                                data=self.data_for_db)
            # with open('./estimation_data.json', 'w') as fp:
            #     json.dump(self.data_for_db, fp)
            #     logging.info("Saved the logged data for relative estimation in a json")
