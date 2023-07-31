from tkinter import *


class ToolTip(object):

    def __init__(self, widget):
        self.text = None
        self.widget = widget
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        """Display text in tooltip window"""
        self.text = text
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27

        self.tip_window = tw = Toplevel(self.widget)

        tw.wm_overrideredirect(True)

        tw.wm_geometry("+%d+%d" % (x, y))

        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


def create_tool_tip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

root = Tk()
button = Button(root, text = 'click mem')
button.pack()
create_tool_tip(button, text = 'Hello World\n'
                 'This is how tip looks like.'
                 'Best part is, it\'s not a menu.\n'
                 'Purely tipbox.')
root.mainloop()
