import tkinter
from time import sleep, time
from typing import List

from src.backend.iRacing.telemetry import RITelemetry
from src.frontend.user_interface import UserInterface
from src.frontend.utils.ri_event_handler import RIEventTypes, subscribe
from src.startup.my_configuration import CompleteConfig


class ClientApp:
    def __init__(self, root: tkinter.Tk, telemetry: RITelemetry, user_interface: UserInterface,
                 configuration: CompleteConfig):
        self.configuration = configuration
        self.root = root
        self.telemetry = telemetry
        self.user_interface = user_interface
        self.max_frames = 545
        self.desired_time = 1 / self.max_frames
        self._running = True

        self.user_interface.update()  # Update UI once to see if any windows are opened
        if not self.windows_open:
            print("No windows were set to active on startup, starting main instead")
            self.configuration.main_open = True
            self.user_interface.main_screen.open_in_middle()

        # Subscribe to close app event to listen for close commands from the screens
        subscribe(event_type=RIEventTypes.CLOSE_APP, fn=self.close_app)

    def run(self):
        current_frame = 0
        while self._running:
            start = time()
            self.telemetry.update()
            # telemetry_time = time() - start
            self.user_interface.update()
            # ui_time = time() - start + telemetry_time
            process_time = time() - start
            sleep_time = max(self.desired_time - process_time, 0)
            sleep(sleep_time)  # Cap frame rate
            # actual_time = time() - start
            # print(f"FPS: {int(1 / actual_time)}, telemetry_time = {telemetry_time:.2f}, ui_time = {ui_time:.2f}")

            if not self.windows_open:  # App should stop running when all windows are closed by user
                self.close_app()

    @property
    def windows_open(self) -> bool:
        return self.check_windows_open()

    def check_windows_open(self) -> bool:
        # check if the root window has any deiconified windows
        toplevel_children = self.get_toplevel_children()
        for toplevel in toplevel_children:
            if toplevel.state() == 'normal':
                return True  # Returns early when it found an open window
        return False  # If no open window was found, return False

    def get_toplevel_children(self) -> List[tkinter.Toplevel]:
        toplevel_children = []
        for child in self.root.winfo_children():
            if isinstance(child, tkinter.Toplevel):
                toplevel_children.append(child)
        return toplevel_children

    def close_app(self, event_data=None):
        """Called when all windows are closed or when main screen is manually closed"""
        self._running = False
