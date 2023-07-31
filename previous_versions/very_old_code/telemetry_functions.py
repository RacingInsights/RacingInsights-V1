import statistics as stats
import math
import logging

from irsdk import IRSDK

from src.backend.iRacing.state import State
from src.backend.iRacing.telemetry import Telemetry
from src.backend.utils.zero_div import zero_div


def update_lap_telemetry(tm: Telemetry, ir: IRSDK):
    """
    Data that is only updated once a lap (when crossing the start finish line)
    :param tm:
    :param ir:
    :return:
    """
    logging.info(f"tm.time_left:{tm.time_left}")

    # Lap time data
    tm.last_lap_time = ir['LapLastLapTime']
    logging.info(f"tm.last_lap_time:{tm.last_lap_time}")

    tm.lap_time_list.append(tm.last_lap_time)
    tm.avg_lap_time = stats.median(tm.lap_time_list)

    # Fuel data
    tm.cons = tm.prev_lap_fuel - tm.fuel
    tm.consumption_list.append(tm.cons)
    tm.avg_cons = stats.median(tm.consumption_list)

    laps_left_on_fuel = zero_div(x=tm.fuel, y=tm.avg_cons)

    logging.info(f"laps_left_on_fuel: {laps_left_on_fuel}")

    tm.laps_left_current = math.floor(laps_left_on_fuel)
    tm.laps_left_extra = math.ceil(laps_left_on_fuel)

    tm.target_cons_current = zero_div(x=tm.fuel - 0.3, y=tm.laps_left_current)
    tm.target_cons_extra = zero_div(x=tm.fuel - 0.3, y=tm.laps_left_extra)

    # # Change this laps_left_in_race calculation to account for leader's position instead
    # tm.laps_left_in_race = zero_div(tm.time_left, tm.avg_lap_time)

    tm.laps_refuel = max(math.ceil(tm.laps_left_in_race) - laps_left_on_fuel + 0.1, 0)
    logging.info(f"laps_refuel: {tm.laps_refuel}")

    tm.refuel = tm.laps_refuel * tm.avg_cons
    logging.info(f"refuel: {tm.refuel}")

    tm.prev_lap_fuel = tm.fuel


def update_live_telemetry(tm: Telemetry, ir: IRSDK):
    """
    Data that is updated live
    :param tm:
    :param ir:
    :return:
    """
    # Self:
    tm.fuel = ir['FuelLevel']
    tm.laps_ir = ir['LapCompleted']

    # Live data needed to determine refuel amount
    tm.time_left = ir['SessionTimeRemain']


def update_others_telemetry(tm: Telemetry, ir: IRSDK):
    """
    Function to update the telemetry variables related to the other cars on track
    :param tm:
    :param ir:
    :return:
    """
    # Make sure the session data is available, [-1] to use the latest session as practice, qualy and race are separated
    if ir['SessionInfo']['Sessions'][-1]['ResultsPositions']:
        # Make sure the laps data is available
        if ir['SessionInfo']['Sessions'][-1]['ResultsPositions'][0]['LapsComplete']:
            new_sample_leader_laps_completed = ir['SessionInfo']['Sessions'][-1]['ResultsPositions'][0]['LapsComplete']

            # If leader started a new lap:
            if new_sample_leader_laps_completed > tm.leader_laps_completed:
                logging.info(f"Leader completed {new_sample_leader_laps_completed} laps")

                # Calculate the remaining laps in the race (based on fastest lap for now)
                fastest_lap_leader = ir['SessionInfo']['Sessions'][-1]['ResultsPositions'][0]['FastestTime']

                # Laps left in the race is ceil(sessiontime/laptime)
                # tm.laps_left_in_race = math.ceil(zero_div(tm.time_left, fastest_lap_leader))
                # logging.info(f"laps_left_in_race (based on leader): {tm.laps_left_in_race}")

                # Update the leaders lap completed in telemetry instance
                tm.leader_laps_completed = new_sample_leader_laps_completed


def step(tm: Telemetry, state: State, ir: IRSDK):
    # capture the previous state instance in a temporary variable for comparison
    previous_state_on_track = state.on_track

    # update the state instance
    current_state = state.update_state(ir)

    # If not driving, no need to display anything
    if not current_state.on_track:
        state = current_state

    # If driving and previously not, new session was started!
    elif not previous_state_on_track and current_state.on_track:
        logging.info("started a new session")
        # Set the fuel variables
        if ir['FuelLevel']:
            tm.fuel = ir['FuelLevel']

        if ir['SessionTimeRemain']:
            tm.time_left = ir['SessionTimeRemain']

        tm.prev_lap_fuel = tm.fuel

    # other scenarios remaining: driving and not started a new session
    else:
        laps = tm.laps_ir
        update_live_telemetry(tm, ir)

        update_others_telemetry(tm, ir)

        if laps < tm.laps_ir:  # Finished a lap
            update_lap_telemetry(tm, ir)

    return tm, state
