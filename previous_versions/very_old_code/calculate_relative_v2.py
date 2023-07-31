def calculate_relative(self, ir: IRSDK):
    """
    Calculates the data needed for populating a relative time overlay (F3 blackbox in iRacing).

    self.relative_data: [{},{},{},{},...,{}], list of dicts where each dict is a car on track
    First element is list is the car the furthest ahead of the player.
    The player is also in this list (centered in case of equal amount of cars in front and behind).
    Last element is the car the furthest behind the player.

    the relative entry dict {} consists of the following keys:
    "relative","car_nr","driver_name","car_brand","irating","ir_license","est_lap_time","car_id","class_position","in_pit"

    :param ir:
    :return:
    """
    player_car_id = ir['PlayerCarIdx']
    nr_of_results = len(ir['DriverInfo']['Drivers'])

    position_in_class = ir['CarIdxClassPosition']

    lap_dist_pct = ir['CarIdxLapDistPct']

    est_time_to_pos_difference = []
    for est_time in ir['CarIdxEstTime']:
        est_time_to_pos_difference.append(est_time - ir['CarIdxEstTime'][player_car_id])

    in_pit = ir['CarIdxOnPitRoad']
    tires_fitted = [(int(tire) != -1) for tire in ir['CarIdxTireCompound']]

    car_id = []
    car_nr = []
    driver_name = []
    car_brand = []
    driver_irating = []
    driver_license = []
    est_lap_time = []
    relative = []

    for i in range(0, nr_of_results):
        car_id.append(ir['DriverInfo']['Drivers'][i]['CarIdx'])
        car_nr.append(ir['DriverInfo']['Drivers'][i]['CarNumberRaw'])
        driver_name.append(ir['DriverInfo']['Drivers'][i]['UserName'])
        car_brand.append(ir['DriverInfo']['Drivers'][i]['CarScreenNameShort'])
        driver_irating.append(ir['DriverInfo']['Drivers'][i]['IRating'])
        driver_license.append(ir['DriverInfo']['Drivers'][i]['LicString'])
        est_lap_time.append(ir['DriverInfo']['Drivers'][i]['CarClassEstLapTime'])
        relative.append(est_lap_time[i] * (lap_dist_pct[i] - lap_dist_pct[player_car_id]))

    sorted_relative_entry = []  # list of relative entries, each entry is dict with keys:

    for rel, nr, name, brand, irating, ir_license, est, carid, pos, pit, tires in sorted((
            zip(est_time_to_pos_difference, car_nr, driver_name, car_brand, driver_irating, driver_license,
                est_lap_time, car_id,
                position_in_class, in_pit, tires_fitted)), reverse=True):

        if carid == player_car_id:  # Make sure the player is added even when on pit
            sorted_relative_entry.append({"relative": 0,
                                          "car_nr": nr,
                                          "driver_name": name,
                                          "car_brand": brand,
                                          "irating": irating,
                                          "ir_license": ir_license,
                                          "est_lap_time": est,
                                          "car_id": carid,
                                          "class_position": pos,
                                          "in_pit": pit,
                                          "is_player": True}
                                         )

        elif tires:  # Only add those who have tires equipped (filters out ppl who are not driving xD)
            sorted_relative_entry.append({"relative": rel,
                                          "car_nr": nr,
                                          "driver_name": name,
                                          "car_brand": brand,
                                          "irating": irating,
                                          "ir_license": ir_license,
                                          "est_lap_time": est,
                                          "car_id": carid,
                                          "class_position": pos,
                                          "in_pit": pit,
                                          "is_player": False}
                                         )

    for i, entry in enumerate(sorted_relative_entry):
        # Determine whether the entry is closer coming from behind (- relative time) or closer ahead (+ relative time)
        if entry["est_lap_time"] / 2 < abs(entry["relative"]):
            if entry["relative"] < 0:
                entry["relative"] = entry["est_lap_time"] + entry["relative"]
            elif entry["relative"] > 0:
                entry["relative"] = -(entry["est_lap_time"] - entry["relative"])

    # Resort as some relative values might have changed
    resorted_relative_entry = sorted(sorted_relative_entry, key=lambda k: k['relative'], reverse=True)

    player_location_in_resorted = 0
    # Store the index for the player in this list, such that the UI can center itself around this index later
    for i, entry in enumerate(resorted_relative_entry):
        if entry["car_id"] == player_car_id:
            player_location_in_resorted = i

    self.relative_data = resorted_relative_entry
    self.player_location_in_sorted = player_location_in_resorted