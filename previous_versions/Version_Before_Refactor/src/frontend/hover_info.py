from tkinter import Toplevel, Label


class HoverInfoWindow:
    def __init__(self, master_widget, text):
        self.info_window = None
        self.info_window_y_padding = 3
        self.master_widget = master_widget
        self.text = text
        self.x = 0
        self.y = 0

        self.master_widget.bind('<Enter>', self.show_info)
        self.master_widget.bind('<Leave>', self.hide_info)

    def show_info(self, event):
        """
        Displays the info in the hover info window
        :return:
        """
        if self.info_window or not self.text:
            return
        # Put the info window on the same x value as the cursor when entering
        x = self.master_widget.winfo_rootx() + event.x
        # Put the info window below the master widget with a padding inbetween
        y = self.master_widget.winfo_rooty() + self.master_widget.winfo_height() + self.info_window_y_padding

        self.info_window = Toplevel(self.master_widget)
        self.info_window.wm_overrideredirect(True)
        self.info_window.wm_geometry(f"+{int(x)}+{int(y)}")

        label = Label(self.info_window, text=self.text, anchor='w')
        label.pack()

    def hide_info(self, _):
        """
        Removes the hover info window
        :param _:
        :return:
        """
        if self.info_window:
            self.info_window.destroy()
            self.info_window = None
