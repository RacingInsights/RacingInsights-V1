import logging
import queue
import tkinter
from os import makedirs
from time import sleep, time
from tkinter import ttk

import irsdk
import sv_ttk
import yaml

from previous_versions.Version_Before_Refactor.src.backend.aws.credentials import Credentials
from previous_versions.Version_Before_Refactor.src.backend.aws.export_logs import S3ResourceHandler
from previous_versions.Version_Before_Refactor.src.backend.iRacing.state import State
from previous_versions.Version_Before_Refactor.src.backend.iRacing import Telemetry
from previous_versions.Version_Before_Refactor.src import MainScreen
from previous_versions.Version_Before_Refactor.src.frontend.default_config import default_config  # backup configuration
from previous_versions.Version_Before_Refactor.src.frontend.login_screen import LoginScreen
from previous_versions.Version_Before_Refactor.src.tools.scenario_freezer import ScenarioFreezer

LOGS_FOLDER_NAME = 'logs'
LOGS_FILE_NAME = f'{LOGS_FOLDER_NAME}/RacingInsights_app_logs.log'


class UI:
    def __init__(self, config_data, telemetry: Telemetry, state: State):
        self.root = tkinter.Tk()

        self.set_ttk_specific_settings(config_data)

        self.login_screen = LoginScreen(self.root, config_data=config_data)

        if not self.login_screen.successful_login:
            return

        self.ui_queue = queue.Queue()  # The elements look as follows: queue_item = (method, (arg1,arg2,...,argN))

        self.main_screen = MainScreen(self.root, telemetry, state, config_data=config_data, ui_reference=self)

        self.scenario_freezer = ScenarioFreezer(telemetry=telemetry, ui_queue=self.ui_queue)

    def update(self):
        """
        This method is the worker that processes both the update methods and also the processes
        in the queue related to user inputs
        :return:
        """
        self.root.update()

        # First add the update process to the queue
        self.ui_queue.put((self.main_screen.update, None))

        self.finish_all_jobs_in_queue()

    def finish_all_jobs_in_queue(self):
        """
        Worker loop to finish all the current jobs in the ui_queue
        :return:
        """
        while True:  # Loop to perform the work in the queue
            if self.ui_queue.empty():  # If the queue is empty, stop the work
                break

            elif not self.ui_queue.empty():
                # Remove and return an item from the queue, button related events can be in this queue
                item = self.ui_queue.get()
                process = item[0]

                arguments = None
                if len(item) > 1:
                    arguments = item[1]

                if arguments:
                    process(*arguments)  # *passes values from a list as method arguments
                else:
                    process()

    @staticmethod
    def set_ttk_specific_settings(config_data):
        """
        Specific actions when using a ttk theme
        :param config_data:
        :return:
        """
        sv_ttk.set_theme("dark")
        font = f"{config_data['root']['font_style']}" \
               f" {config_data['root']['font_size']}" \
               f" {config_data['root']['font_extra']}"

        # Set the font style for all ttk widgets
        s = ttk.Style()
        s.configure('.', font=font)


class App:
    def __init__(self, ui: UI, backend: Telemetry, max_frames=30):
        self.ui = ui
        self.backend = backend
        self.max_frames = max_frames
        self._running = True
        self.ui.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.s3_resource_handler = S3ResourceHandler(log_id=ui.login_screen.log_id)

    def run(self):
        current_frame = 0
        while self._running:
            start = time()
            self.backend.update()
            # telemetry_time = time() - start
            self.ui.update()
            # ui_time = time() - start + telemetry_time
            # process_time = max(0.01, time() - start)
            # print(f"FPS: {int(1/(process_time))}, telemetry_time = {telemetry_time}, ui_time = {ui_time}")
            # If the app used less than 1/max_frames of a second, then sleep until that period is reached,
            # otherwise no sleep.
            sleep(max(1. / self.max_frames - (time() - start), 0))
            current_frame = 0 if current_frame == self.max_frames else current_frame + 1

    def _on_closing(self):
        self._running = False

        # TODO: Add all the functions here that upload the required data to the database
        self.backend.send_logged_data_to_db()
        # - current config_data (if changed since previous)
        self.s3_resource_handler.export_logs(log_file_name=LOGS_FILE_NAME)


def main():
    makedirs(LOGS_FOLDER_NAME, exist_ok=True)  # If logs directory doesn't exist, make one

    logging.basicConfig(format='|%(asctime)s | %(levelname)s | %(message)s\n'
                               '|---------------------------| %(pathname)s:%(lineno)d ',
                        filename=LOGS_FILE_NAME,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    # load config (yaml file) here and pass as input to frontend app
    try:
        with open(r'config_data.yaml') as config_file:
            config_data = yaml.safe_load(config_file)
    except FileNotFoundError:
        logging.info("config_data.yaml not found, loaded default_config instead")
        config_data = default_config

    # initialise the connection with iRacing
    ir = irsdk.IRSDK()
    ir.startup()

    # instantiate the state
    state = State()

    # instantiate the telemetry
    telemetry = Telemetry(state=state, ir_sdk=ir)

    ui = UI(config_data, telemetry, state)

    if not ui.login_screen.successful_login:
        logging.info("Login screen was closed without a successful login, the app is closed")
        return

    # Everything below can only be accessed for authenticated users
    # If it enters this, the log file will be sent to db and then deleted when the app is closed
    app = App(ui, telemetry)

    try:
        credentials = Credentials(cognito_idp_response=ui.login_screen.cognito_idp_response)  # Get the AWS credentials
        telemetry.relative_estimation_data_db_link.set_resource(credentials=credentials)  # Connect to DB
        app.s3_resource_handler.set_resource(credentials=credentials)  # Connect to S3 with credentials

        app.run()
    except Exception as exc:
        logging.exception(exc)
        app.s3_resource_handler.export_logs(log_file_name=LOGS_FILE_NAME)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.exception(e)
