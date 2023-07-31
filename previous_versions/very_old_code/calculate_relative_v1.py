def calculate_relative(self, ir: IRSDK):
    """
    Calculates the data needed for populating a relative time overlay (F3 blackbox in iRacing).
    :param ir:
    :return:
    """
    player_car_id = ir['PlayerCarIdx']
    nr_of_results = len(ir['DriverInfo']['Drivers'])

    position_in_class = ir['CarIdxClassPosition']

    relative_time = []
    for est_time in ir['CarIdxEstTime']:
        relative_time.append(est_time - ir['CarIdxEstTime'][player_car_id])

    in_pit = ir['CarIdxOnPitRoad']
    tires_fitted = [(int(tire) != -1) for tire in ir['CarIdxTireCompound']]

    car_id = []
    car_nr = []
    driver_name = []
    car_brand = []
    driver_irating = []
    driver_license = []
    est_lap_time = []

    for i in range(0, nr_of_results):
        car_id.append(ir['DriverInfo']['Drivers'][i]['CarIdx'])
        car_nr.append(ir['DriverInfo']['Drivers'][i]['CarNumberRaw'])
        driver_name.append(ir['DriverInfo']['Drivers'][i]['UserName'])
        car_brand.append(ir['DriverInfo']['Drivers'][i]['CarScreenNameShort'])
        driver_irating.append(ir['DriverInfo']['Drivers'][i]['IRating'])
        driver_license.append(ir['DriverInfo']['Drivers'][i]['LicString'])
        est_lap_time.append(ir['DriverInfo']['Drivers'][i]['CarClassEstLapTime'])

    sorted_relative_entry = []
    for rel, nr, name, brand, irating, ir_license, est, carid, pos, pit, tires in sorted((
            zip(relative_time, car_nr, driver_name, car_brand, driver_irating, driver_license, est_lap_time, car_id,
                position_in_class, in_pit, tires_fitted))):

        if carid == player_car_id:  # Make sure the player is added even when on pit
            sorted_relative_entry.append([0, nr, name, brand, irating, ir_license, est, carid, pos])
        elif not pit and tires:  # Only add those who are not on pit and have tires equipped
            sorted_relative_entry.append([rel, nr, name, brand, irating, ir_license, est, carid, pos])

    for i, entry in enumerate(sorted_relative_entry):
        if entry[6] / 2 < abs(entry[0]):  # Check if estimated lap time/2 < relative, if so car is behind player
            if entry[0] < 0:
                entry[0] = entry[6] + entry[0]
            elif entry[0] > 0:
                entry[0] = -(entry[6] - entry[0])

    # Resort the list in revers to have the furthest ahead at [0], player in middle, and furthest behind at [-1]
    resorted_relative_entry = sorted(sorted_relative_entry, reverse=True)

    # Find the player's position in this list
    player_location_in_resorted = 0
    for i, entry in enumerate(resorted_relative_entry):
        if entry[7] == player_car_id:
            player_location_in_resorted = i

    self.relative_data = resorted_relative_entry
    self.player_location_in_sorted = player_location_in_resorted