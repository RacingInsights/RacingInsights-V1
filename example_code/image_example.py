import tkinter
from tkinter import *
from PIL import Image, ImageTk

root = Tk()

# Create a photoimage object of the image in the path
image1 = Image.open("../docs/logos-design/RacingInsights_Icon.png")
image1 = image1.resize((100, 100))
test = ImageTk.PhotoImage(image1)

label1 = tkinter.Label(image=test)
label1.image = test
# Position image
label1.place(relx=0.5,rely=0.5)
root.mainloop()