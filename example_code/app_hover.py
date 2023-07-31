from tkinter import Tk, Button
from previous_versions.Version_Before_Refactor.src import HoverInfoWindow

root = Tk()
button = Button(root, text="Test button")
button.pack()
hi = HoverInfoWindow(master_widget=button, text="This info only shows when hovering")
root.mainloop()
