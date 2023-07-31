"""
Prototype (in CLI) of the alternative relative (F3 blackbox in iracing) overlay

Data it should include; 3 cars ahead, 3 cars behind
- position in class     -> ir['CarIdxClassPosition'][i]
- car #                 -> ir['DriverInfo']['Drivers'][i]['CarNumberRaw']
- name of the driver    -> ir['DriverInfo']['Drivers'][i]['UserName']
- relative time         -> ir['CarIdxEstTime'][i]

Data it could include
* car brand             -> ir['DriverInfo']['Drivers'][i]['CarScreenNameShort']
* driver_irating        -> ir['DriverInfo']['Drivers'][i]['IRating']
* driver_license        -> ir['DriverInfo']['Drivers'][i]['LicString']
* pitted lap indication, if pitted before
"""
import time
import irsdk

ir = irsdk.IRSDK()
ir.startup(test_file='data.bin')

st = time.time()

player_car_id = ir['PlayerCarIdx']
player_rel_offset = ir['DriverInfo']['Drivers'][player_car_id]['CarClassEstLapTime'] - ir['CarIdxEstTime'][player_car_id]
nr_of_results = len(ir['DriverInfo']['Drivers'])

position_in_class = ir['CarIdxClassPosition']
relative_time = ir['CarIdxEstTime']

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

sorted_relative_entry = [[rel, nr, name, brand, irating, ir_license, est, carid] for rel, nr, name, brand, irating, ir_license, est, carid in sorted((zip(relative_time, car_nr, driver_name, car_brand, driver_irating, driver_license, est_lap_time, car_id))) if int(rel) != 0]

for i, entry in enumerate(sorted_relative_entry):
    if entry[6]-entry[0] < entry[0]:  # Check if estimated lap time - relative < relative, if so car is behind player
        entry[0] = -(entry[6]-entry[0]) + player_rel_offset

# Resort the list in revers to have furthest ahead at [0], player in middle, and furthest behind at [-1]
resorted_relative_entry = sorted(sorted_relative_entry, reverse=True)

# Find the player's position in this list
player_location_in_resorted = 0
for i, entry in enumerate(resorted_relative_entry):
    if entry[-1] == player_car_id:
        player_location_in_resorted = i

for entry in resorted_relative_entry[player_location_in_resorted-3:player_location_in_resorted+4]:
    print(entry)

et = time.time()
tot = et-st
print(tot)
