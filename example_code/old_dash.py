# # Label of the current fuel
#
#         boxwidth = 10
#         boxwidth_half = 5
#         boxheigth = 2
#         boxheigth_small = 1
#         boxheigth_header = 1
#         y_pad = 2
#
#
#         self.fuelheader = Label(text="Fuel", font=('TkFixedFont 24'), bg="#1c2330", fg='WHITE', width=boxwidth, height=boxheigth_header, pady=y_pad)
#         self.fuelheader.grid(row=0, column=0, columnspan=10, sticky='W')
#         self.fuelvar = StringVar()
#         self.fuelvar.set("000.00")
#         self.fuellabel = Label(textvariable=self.fuelvar, font=('TkFixedFont 24'), bg="#1c2330", fg='WHITE', width=boxwidth, height=boxheigth)
#         self.fuellabel.grid(row=1, column=0, rowspan=2, columnspan=10, sticky='W')
#
#         # Label of the avg consumption, #bd461e
#         self.avgconsheader = Label(text="Consumption", font=('TkFixedFont 24'), bg="#bd461e", fg='WHITE', width=boxwidth, height=boxheigth_header, pady=y_pad)
#         self.avgconsheader.grid(row=0, column=10, columnspan=10, sticky='W')
#         self.avgconsvar = StringVar()
#         self.avgconsvar.set("000.00")
#         self.avgconslabel = Label(textvariable=self.avgconsvar, font=('TkFixedFont 24'), bg="#bd461e", fg='WHITE', width=boxwidth, height=boxheigth)
#         self.avgconslabel.grid(row=1, column=10, rowspan=2, columnspan=10, sticky='W')
#
#         # Label of the laps left in stint (based on avg consumption), #1c1a99
#         self.lapsheader = Label(text="Laps", font=('TkFixedFont 24'), bg="#1c1a99", fg='WHITE', width=boxwidth, height=boxheigth_header, pady=y_pad)
#         self.lapsheader.grid(row=0, column=20)
#         self.lapsleftvar = StringVar()
#         self.lapsleftvar.set("000.00")
#         self.lapsleftlabel = Label(textvariable=self.lapsleftvar, font=('TkFixedFont 24'), bg="#1c1a99", fg='WHITE',
#                                    width=boxwidth, height=boxheigth)
#         self.lapsleftlabel.grid(row=1, column=20, rowspan=2)
#
#         # Label of target for current amount of laps
#         self.targetheader = Label(font=('TkFixedFont 24'), bg="#910d63", fg='WHITE', width=boxwidth, height=boxheigth_header)
#         self.targetheader.grid(row=0, column=30, columnspan=10, sticky='W')
#         self.targetvar = StringVar()
#         self.targetvar.set("000.00")
#         self.targetlabel = Label(font=('TkFixedFont 24'), bg="#910d63", fg='WHITE', width=boxwidth_half, height=boxheigth_small)
#         self.targetlabel.grid(row=1, column=30,columnspan=5, sticky='W')
#
#         # Label of target for extra lap
#         self.targetextravar = StringVar()
#         self.targetextravar.set("000.00")
#         self.targetlabel = Label(font=('TkFixedFont 24'), bg="#910d63", fg='WHITE', width=boxwidth_half, height=boxheigth_small)
#         self.targetlabel.grid(row=1, column=35,columnspan=5,sticky='W')