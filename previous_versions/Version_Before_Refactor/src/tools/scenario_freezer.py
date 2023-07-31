import logging
import os
from queue import Queue

import keyboard
import yaml
from PIL import ImageGrab

from previous_versions.Version_Before_Refactor.src.backend.iRacing.telemetry import IRSDK, State, Telemetry


class ScenarioFreezer:
    """
    Use case explanation:
    When using the overlays, a tester should be able to press a button.
    On this button press, the tool will then take a screenshot. The screenshot includes both the game + overlays.
    At the same time, the tool will also log all current attributes of the Telemetry instance.
    And it will also log the current iRacing_sdk data to a yaml file
    Output folder of the logs will be: logs/scenario_freeze_{NR} where NR is unique, starting at 1 and going up

    Inputs:
        - Telemetry object (contains also iRacing_sdk object)

    Example output of tool:
    logs/scenario_freeze_1/
        - screenshot.png
        - telemetry_attributes.yaml
        - iRacing_sdk_data.yaml

        scenario_freeze_2/
        - screenshot.png
        - telemetry_attributes.yaml
        - iRacing_sdk_data.yaml
    """
    def __init__(self, telemetry: Telemetry, ui_queue: Queue):
        self.folder_path = None
        self.scenario_freeze_folder_name = None
        self.freeze_count = None
        self.telemetry = telemetry
        self.ui_queue = ui_queue
        self.logs_parent_folder = './logs'
        keyboard.add_hotkey("'", lambda: self.key_press_handler())

    def key_press_handler(self):
        """
        Triggered on button press.
        """
        print("Key pressed: freezing scenario")
        self.ui_queue.put((self.freeze_scenario, None))

    def freeze_scenario(self):
        """
        Added to the ui queue as a job.
        This will be done in the update of the ui queue.
        :return:
        """
        sub_folders = [f.path for f in os.scandir(self.logs_parent_folder) if f.is_dir()]

        self.freeze_count = len(sub_folders) + 1
        self.scenario_freeze_folder_name = f"scenario_freeze_{self.freeze_count}"
        self.folder_path = f"{self.logs_parent_folder}/{self.scenario_freeze_folder_name}"

        logging.info("Triggered freeze_scenario, stored in %s", self.folder_path)

        os.makedirs(self.folder_path, exist_ok=True)

        # self.save_telemetry_yaml()
        self.save_iracing_sdk_yaml()
        # self.take_screenshot()

    def take_screenshot(self):
        screenshot = ImageGrab.grab()
        screenshot.save(fp=f"{self.folder_path}/screenshot.png")

    def save_telemetry_yaml(self):
        """
        Saves the current telemetry attributes to yaml file
        """
        file_name = f"{self.folder_path}/telemetry_attributes.yaml"

        telemetry = self.telemetry.__dict__
        filtered_telemetry = {key: value for (key, value) in telemetry.items() if not isinstance(value, (IRSDK, State))}

        with open(rf'{file_name}', 'w') as file:
            _ = yaml.dump(filtered_telemetry, file)

    def save_iracing_sdk_yaml(self):
        """
        Saves the current iRacing sdk data to yaml file
        """
        binary_name = f"{self.folder_path}/iRacing_sdk_data.bin"
        file_name = f"{self.folder_path}/iRacing_sdk_data.yaml"

        self.telemetry.ir_sdk.startup(dump_to=binary_name)  # Gets the binary file and dumps it
        self.telemetry.ir_sdk.parse_to(file_name)  # Parses the data to a yaml file
