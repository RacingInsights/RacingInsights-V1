import os
import random
import unittest

import irsdk

from previous_versions.Version_Before_Refactor.src.backend.iRacing.state import State
from previous_versions.Version_Before_Refactor.src.backend import Telemetry
from previous_versions.Version_Before_Refactor.tests.utils.disable_resource_warnings import ignore_warnings


class TestRelativeScreenTelemetry(unittest.TestCase):

    @ignore_warnings
    def test_is_other_ahead_or_behind(self):
        """
        test to check the telemetry.is_other_ahead_or_behind method
        Purpose: Check that the method correctly determines 'ahead' or 'behind' based on lap distance percentage
        :return:
        """
        # Initialize the instances
        self.ir_sdk = irsdk.IRSDK()
        state = State()
        self.telemetry = Telemetry(state=state, ir_sdk=self.ir_sdk)

        # Test for different combinations
        val_1 = self.telemetry.is_other_ahead_or_behind(dist_pct_1=0.1, dist_pct_2=0.2)
        self.assertEqual(val_1, "behind")

        val_2 = self.telemetry.is_other_ahead_or_behind(dist_pct_1=0.3, dist_pct_2=0.2)
        self.assertEqual(val_2, "ahead")

        val_3 = self.telemetry.is_other_ahead_or_behind(dist_pct_1=0.9, dist_pct_2=0.2)
        self.assertEqual(val_3, "behind")

        val_4 = self.telemetry.is_other_ahead_or_behind(dist_pct_1=0.6, dist_pct_2=0.2)
        self.assertEqual(val_4, "ahead")

        val_5 = self.telemetry.is_other_ahead_or_behind(dist_pct_1=0.6, dist_pct_2=0.9)
        self.assertEqual(val_5, "behind")

        val_6 = self.telemetry.is_other_ahead_or_behind(dist_pct_1=0.2, dist_pct_2=0.9)
        self.assertEqual(val_6, "ahead")

    @ignore_warnings
    def test_calculate_relative_time(self):
        """
        test to check the telemetry.calculate_relative_time method
        Purpose: Check that for each relative time, its absolute value is smaller than half the lap time of the player
        :return:
        """
        self.ir_sdk = irsdk.IRSDK()
        state = State()
        self.telemetry = Telemetry(state=state, ir_sdk=self.ir_sdk)

        # Mocking
        self.telemetry.car_class_id_player = 4011
        lap_time_player = 105.0

        # ir_sdk data is required to load estimation data
        root_folder = 'C:/Users/Thibe/Documents/GitHub/iRacing-refuel-overlay/tests/scenarios_to_test/'
        test_file_name = f"{root_folder}scenario_freeze_4/iRacing_sdk_data.bin"
        self.ir_sdk.startup(test_file=test_file_name)

        # Make sure the estimation data is loaded
        self.telemetry.estimation_data, self.telemetry.current_track_id = self.telemetry.get_relative_estimation_data(
            dummy_file='../../../logs/estimation_data_template.json')

        # Tests
        for i in range(20):
            pct_other = random.uniform(0, 1.0)
            pct_player = random.uniform(0, 1.0)

            rel_time = self.telemetry.calculate_relative_time_normal(pct_other=pct_other,
                                                                     pct_player=pct_player,
                                                                     lap_time_player=lap_time_player)

            self.assertLessEqual(abs(rel_time), lap_time_player / 2)

        self.ir_sdk.shutdown()

    @ignore_warnings
    def test_update_relative_telemetry_descending(self):
        """
        Purpose: Check whether the relative times in the relative are descending, for real data
        :return:
        """
        self.ir_sdk = irsdk.IRSDK()
        state = State()

        root_folder = 'C:/Users/Thibe/Documents/GitHub/iRacing-refuel-overlay/tests/scenarios_to_test/'

        for folder in os.listdir(root_folder):
            test_file_name = f"{root_folder}{folder}/iRacing_sdk_data.bin"
            if folder == "scenario_freeze_35":
                pass

            print("--------------------", folder, "---------------------------------")
            self.ir_sdk.startup(test_file=test_file_name)

            self.telemetry = Telemetry(state=state, ir_sdk=self.ir_sdk)

            self.telemetry.update()
            self.telemetry.update_relative_telemetry()

            # Print the data as is shown in the relative overlay
            print("----------------------------------")
            for entry in self.telemetry.relative_data:
                print(f"{entry['relative']:.2f} | {entry['driver_name']}")
            print("----------------------------------\n")

            self.run_descending_tests(telemetry=self.telemetry)

            self.ir_sdk.shutdown()

    def run_descending_tests(self, telemetry: Telemetry):
        prev_relative_time = None
        prev_dist_pct = None
        for i, entry in enumerate(telemetry.relative_data):
            relative_time_entry = entry["relative"]
            dist_pct_entry = self.telemetry.ir_sdk['CarIdxLapDistPct'][entry['car_id']]

            if prev_relative_time:
                # Checks whether the order is correct based on time
                self.assertLessEqual(relative_time_entry, prev_relative_time)

            if prev_dist_pct and self.telemetry.relative_mode == "NORMAL":
                # Checks whether the order is correct based on dist pct, for normal mode
                # This check could fail for LITE mode in multi-class as it does not have the data yet based on dist pct
                result = self.telemetry.is_other_ahead_or_behind(dist_pct_1=prev_dist_pct, dist_pct_2=dist_pct_entry)
                self.assertEqual(result, "ahead")

            prev_relative_time = relative_time_entry
            prev_dist_pct = dist_pct_entry

    @ignore_warnings
    def test_relative_entry_list_names(self):
        # Initialize the instances
        self.ir_sdk = irsdk.IRSDK()
        state = State()
        self.telemetry = Telemetry(state=state, ir_sdk=self.ir_sdk)

        # ir_sdk data is required to load estimation data
        root_folder = 'C:/Users/Thibe/Documents/GitHub/iRacing-refuel-overlay/tests/scenarios_to_test/'
        test_file_name = f"{root_folder}scenario_freeze_45/iRacing_sdk_data.bin"
        self.ir_sdk.startup(test_file=test_file_name)

        self.telemetry.update()
        self.telemetry.update_relative_telemetry()

        expected_names = ["Yusuf Toptas", "Nicholas Owen2", "Thibeau Teuwen", "Nathan Tapp", "Luke Withers",
                          "Reyer Borgesius"]

        for i, name in enumerate(self.telemetry.relative_data):
            print(self.telemetry.relative_data[i]["driver_name"])

        if self.telemetry.relative_mode == "NORMAL":
            for i, name in enumerate(expected_names):
                self.assertEqual(self.telemetry.relative_data[i]["driver_name"], name)
        else:
            print("Could not run this test as it might fail due to progress assumption difference dist vs lap time")

    @ignore_warnings
    def test_calculate_id_in_estimate_list(self):
        # Initialize the instances
        self.ir_sdk = irsdk.IRSDK()
        state = State()
        self.telemetry = Telemetry(state=state, ir_sdk=self.ir_sdk)

        self.telemetry.logged_resolution_pct = 0.20

        dist_pct_list = [0.05, 0.25, 0.29, 0.31, 0.51, 0.69, 0.71, 0.89, 0.91]
        expected_id = [0, 0, 0, 1, 2, 2, 3, 3, 4]

        for dist_pct, exp_id in zip(dist_pct_list, expected_id):
            returned_id = self.telemetry.calculate_id_in_estimate_list(estimate_dist_pct=dist_pct)
            print(f"expected: {exp_id}, returned: {returned_id}")
            self.assertEqual(returned_id, exp_id)

    @ignore_warnings
    def test_add_data_to_logged_estimate_lists(self):
        # Initialize the instances
        self.ir_sdk = irsdk.IRSDK()
        state = State()
        self.telemetry = Telemetry(state=state, ir_sdk=self.ir_sdk)

        # ir_sdk data is required to load estimation data
        root_folder = 'C:/Users/Thibe/Documents/GitHub/iRacing-refuel-overlay/tests/scenarios_to_test/'
        test_file_name = f"{root_folder}scenario_freeze_4/iRacing_sdk_data.bin"
        self.ir_sdk.startup(test_file=test_file_name)

        self.telemetry.init_logged_relative_data()  # This doesn't give error because ir_sdk test file used

        percentages = [3, 4.1, 4.2, 4.05, 4.98]
        estimate_pct_list = [pct * self.telemetry.logged_resolution_pct for pct in percentages]
        estimate_time_list = [12, 17, 18, 16.95, 20]

        for pct, time in zip(estimate_pct_list, estimate_time_list):
            self.run_add_data_to_logged_estimate_lists_tests(estimate_pct=pct, est_time=time)

    def run_add_data_to_logged_estimate_lists_tests(self, estimate_pct, est_time):
        # Calculate the corresponding log_id in list, this method has already been proven correct by other unit tests
        id_in_list = self.telemetry.calculate_id_in_estimate_list(estimate_dist_pct=estimate_pct)

        previous_time = self.telemetry.logged_estimate_time[id_in_list]

        # Run the method
        self.telemetry.add_data_to_logged_estimate_lists(estimate_dist_pct=estimate_pct,
                                                         estimate_time=est_time,
                                                         id_in_estimate_list=id_in_list)

        # Check that the relative result (equal, smaller, greater) of the interpolation is correct
        if estimate_pct == self.telemetry.logged_distance_pct[id_in_list]:
            self.assertEqual(self.telemetry.logged_estimate_time[id_in_list], est_time)

        elif estimate_pct > self.telemetry.logged_distance_pct[id_in_list]:
            self.assertLess(self.telemetry.logged_estimate_time[id_in_list], est_time)

        elif estimate_pct < self.telemetry.logged_distance_pct[id_in_list]:
            self.assertGreater(self.telemetry.logged_estimate_time[id_in_list], est_time)

        current_offset = abs(estimate_pct - self.telemetry.logged_distance_pct[id_in_list])
        previous_offset = abs(self.telemetry.logged_current_reference_pct_stored[id_in_list] -
                              self.telemetry.logged_distance_pct[id_in_list])

        # Check that it is updated only when the data is more accurate
        if current_offset < previous_offset:
            self.assertNotEqual(self.telemetry.logged_estimate_time[id_in_list], previous_time)
        elif current_offset > previous_offset:
            if previous_time != 0:
                self.assertEqual(self.telemetry.logged_estimate_time[id_in_list], previous_time)

        print(self.telemetry.logged_estimate_time[id_in_list])


if __name__ == '__main__':
    unittest.main()
