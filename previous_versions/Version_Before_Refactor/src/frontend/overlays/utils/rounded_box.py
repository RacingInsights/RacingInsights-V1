import tkinter

from previous_versions.Version_Before_Refactor.src.frontend.overlays.utils.rounded_rectangle import create_good_rectangle


class RoundedBox:
    def __init__(self, master: tkinter.Frame, bg_out: str, bg_in: str, textvariable: tkinter.StringVar, font: str,
                 padding_x: int, padding_y: int, box_width):
        self.rectangle = None
        self.bg_in = bg_in
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.box_canvas = tkinter.Canvas(master=master, borderwidth=0, highlightthickness=0, bg=bg_out)
        self.box_frame = tkinter.Frame(master=self.box_canvas, bg=self.bg_in)
        self.box_label = tkinter.Label(master=self.box_frame, textvariable=textvariable, width=box_width, font=font,
                                       fg="BLACK", anchor='center', bg=self.bg_in)
        self.box_canvas.pack(side='left', expand=1, fill='both', padx=self.padding_x, pady=self.padding_y)
        self.box_frame.pack(side='left', expand=1, fill='both')
        self.box_label.pack(side='left', expand=1, fill='both')

        # Create a temporary window, just to spawn the widgets before calculating/spawning the final window
        self.box_canvas.create_window(0, 0, window=self.box_frame)
        self.create_rounded_box()

    def create_rounded_box(self):
        """
        Be careful, this makes a copy and cannot delete the previous window. Do not use this in loop
        :return:
        """
        # After putting all the content inside the frame, measure its size
        self.box_frame.update()  # Needs to be updated before measurements

        frame_width = self.box_frame.winfo_width()
        frame_height = self.box_frame.winfo_height()

        # Create the rounded rectangle based on inner frame dimensions
        window_padding = 3
        window_width = frame_width + window_padding
        window_height = frame_height + window_padding

        if self.rectangle:
            self.box_canvas.delete(self.rectangle)

        self.rectangle = create_good_rectangle(self.box_canvas, 0, 0, window_width, window_height, feather=3,
                                               color=self.bg_in)
        self.box_canvas.create_window(window_width / 2, window_height / 2, window=self.box_frame)
        self.box_canvas.configure(width=window_width, height=window_height)

    def configure(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'font':
                self.box_label.configure(font=value)
                self.create_rounded_box()  # As the size of the font changes, the window needs to change size too
            if key == 'bg':
                self.bg_in = value
                self.box_label.configure(bg=self.bg_in)
                self.box_frame.configure(bg=self.bg_in)
                self.box_canvas.itemconfig(self.rectangle, fill=value)  # PRAISE THE LORD FOR THIS LINE OF CODE
            if key == 'padding_x':
                self.padding_x = value
                self.box_canvas.pack(side='left', expand=1, fill='both', padx=self.padding_x, pady=self.padding_y)
            if key == 'padding_y':
                self.padding_y = value
                self.box_canvas.pack(side='left', expand=1, fill='both', padx=self.padding_x, pady=self.padding_y)
            if key == 'fg':
                self.box_label.configure(fg=value)

    def update(self):
        self.box_label.update()
        self.box_frame.update()
        self.box_canvas.update()
