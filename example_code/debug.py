import math

import irsdk
from pprint import pprint

from previous_versions.Version_Before_Refactor.src.backend import zero_div

ir = irsdk.IRSDK()
ir.startup()

def find_last_session_id(ir_conn):
    i = -1
    while True:
        if not ir_conn['SessionInfo']['Sessions'][i]['ResultsPositions']:
            i -= 1
        else:
            return i

avg_lap_time = 120
session_id = find_last_session_id(ir)
time_left = ir['SessionTimeRemain']
leader_CarIdx = ir['SessionInfo']['Sessions'][session_id]['ResultsPositions'][0]['CarIdx']
fastest_lap_leader = ir['SessionInfo']['Sessions'][session_id]['ResultsPositions'][0]['FastestTime']
estimate_to_pos_leader = ir['CarIdxEstTime'][leader_CarIdx]
estimate_lap_time_leader = ir['DriverInfo']['Drivers'][leader_CarIdx]['CarClassEstLapTime']
lap_progress_pct_leader = zero_div(estimate_to_pos_leader, estimate_lap_time_leader)
live_laps_to_finish_leader = math.ceil(zero_div(time_left, fastest_lap_leader)) - lap_progress_pct_leader
time_to_finish_leader = live_laps_to_finish_leader * estimate_lap_time_leader
laps_left_in_race = math.ceil(zero_div(time_to_finish_leader, avg_lap_time))
pprint(ir['SessionInfo']['Sessions'][session_id]['ResultsPositions'][0]['FastestTime'])
print(laps_left_in_race)
