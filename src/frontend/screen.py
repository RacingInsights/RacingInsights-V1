import tkinter
from abc import abstractmethod
from enum import Enum


class IconTypes(Enum):
    LOGO = "images/RacingInsights_Logo.ico",
    SETTINGS = "images/RacingInsights_Settings.ico"


class Screen:

    def __init__(self, root: tkinter.Tk, title: str):
        self.root = root
        self.screen = tkinter.Toplevel(self.root)
        self.screen.title(title)
        self.screen.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._hidden = True

    @property
    def width(self) -> int:
        return self.screen.winfo_width()

    @property
    def height(self) -> int:
        return self.screen.winfo_height()

    def open_in_middle(self):
        """
        Requirements: Before this is called, all widgets have to be packed!
        Places the login screen in the middle with the right size
        """
        self.screen.withdraw()  # Widgets are already packed but not visible, withdraw the window
        self.root.update()  # Update all, this way all window sizes become available (even when withdrawn)

        # get screen width and height
        screen_width = self.screen.winfo_screenwidth()  # width of the screen
        screen_height = self.screen.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the screen to align it to the middle
        x_coord = (screen_width / 2) - (self.width / 2)
        y_coord = (screen_height / 2) - (self.height / 2)

        # set the dimensions of the screen and where it is placed
        self.screen.geometry(f"{self.width}x{self.height}+{int(x_coord)}+{int(y_coord)}")  # Sets it to the middle
        self.screen.iconbitmap(self.icon.value)  # Needs to be done after opening
        self.screen.deiconify()  # Now the screen can be shown, in the middle
        self.screen.lift()
        self._hidden = False

    def set_initial_visibility(self):
        """This method is to be called"""
        if self.active:
            self.open_in_middle()
        else:
            self.screen.withdraw()

    def set_correct_visibility(self, event_data=None):
        if not self.active and not self._hidden:
            self.hide()

        if self.active and self._hidden:
            self.open_in_middle()

    def hide(self):
        self.screen.withdraw()
        self._hidden = True

    @property
    @abstractmethod
    def active(self) -> bool:
        ...

    @property
    @abstractmethod
    def icon(self) -> IconTypes:
        ...

    @abstractmethod
    def _on_closing(self):
        """
        Determines the behavior when the screen is closed
        :return:
        """
