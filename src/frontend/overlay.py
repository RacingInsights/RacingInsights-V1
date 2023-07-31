import tkinter
from abc import abstractmethod


class Overlay:
    """Super class for overlays"""

    def __init__(self, root: tkinter.Tk):
        self.y = None
        self.x = None
        self.overlay = tkinter.Toplevel(root)
        self.overlay.wm_withdraw()  # Step 1 required for showing icon in taskbar
        self.overlay.overrideredirect(True)
        self.overlay.lift()  # Step 2 required for showing icon in taskbar
        self.overlay.wm_attributes("-topmost", True)

        self.overlay.wm_attributes('-transparentcolor', "RED")
        self.overlay.iconbitmap("images/RacingInsights_Logo.ico")
        self.overlay.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.overlay.bind("<ButtonPress-1>", self.start_move)
        self.overlay.bind("<ButtonRelease-1>", self.stop_move)
        self.overlay.bind("<B1-Motion>", self.do_move)
        self._hidden = True

    def show(self):
        self.overlay.wm_deiconify()
        self.overlay.lift()
        self._hidden = False

    def hide(self):
        self.overlay.withdraw()
        self._hidden = True

    def set_correct_visibility(self):
        if not self.active and not self._hidden:
            self.hide()

        if self.active and self._hidden:
            self.show()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, _):
        self.x = None
        self.y = None

    def do_move(self, event):
        if self.locked:
            return

        delta_x = event.x - self.x
        delta_y = event.y - self.y
        self.set_offset_right(self.overlay.winfo_x() + delta_x)
        self.set_offset_down(self.overlay.winfo_y() + delta_y)
        self.overlay.geometry(f"+{self.offset_right}+{self.offset_down}")

    @abstractmethod
    def _on_closing(self):
        """
        Determines the behavior when the overlay is closed
        :return:
        """

    @abstractmethod
    def update(self) -> None:
        """
        Used to indicate that overlay classes should have an update method.
        """

    @property
    @abstractmethod
    def active(self) -> bool:
        ...

    @property
    @abstractmethod
    def locked(self) -> bool:
        ...

    @property
    @abstractmethod
    def offset_right(self) -> int:
        ...

    @property
    @abstractmethod
    def offset_down(self) -> int:
        ...

    @abstractmethod
    def set_offset_right(self, param):
        pass

    @abstractmethod
    def set_offset_down(self, param):
        pass
