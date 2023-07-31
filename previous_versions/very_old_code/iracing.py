import statistics as stats
import math
import logging

import irsdk

from src.backend.utils.zero_div import zero_div


class State:
    ir_connected = False
    last_car_setup_tick = -1


class CarTelemetry:
    def __init__(self, ir_conn):
        # Over-the-line data
        self.list_lap_times = []
        self.last_lap_time = 0
        self.fuel_refuel = 0
        self.laps_refuel = 0
        self.laps_left = 0
        self.avg_lap_time = 0
        self.time_left = 0
        self.cons = 0
        self.laps_left_extra = 0
        self.laps_left_current = 0
        self.target_cons_current = 0
        self.target_cons_extra = 0
        self.laps_left_avg_ol = 0
        self.laps_completed = 0
        self.prev_lap_fuel = 0
        self.avg_cons = 0
        self.consumptions = []
        self.prev_on_pit = ir_conn['OnPitRoad']

        # Live data
        self.fuel = 0

    def step(self, state, ir_conn):
        """
        Step function that updates the telemetry data when it has a valid iRacing connection.
        Consists of 2 types of telemetry data:
            - live data that is updated for each step call
            - 'over-the-line' data that is only updated once a lap, when crossing the start finish line
        :param state:
        :param ir_conn:
        :return:
        """
        check_iracing(state=state, ir=ir_conn)

        if state.ir_connected:
            # Each step, freeze the buffer with live telemetry to have consistent data within one tick.
            ir_conn.freeze_var_buffer_latest()

            # Update the telemetry data
            self.update_live_data(ir_conn=ir_conn)
            self.update_over_the_line_data(ir_conn=ir_conn)

        else:
            # Reset the variables to prevent carrying over data from a previous session
            self.reset_variables()
            self.fuel = 0
            print("iRacing is not connected")
        return self

    def reset_variables(self):
        self.list_lap_times = []
        self.last_lap_time = 0
        self.fuel_refuel = 0
        self.laps_refuel = 0
        self.laps_left = 0
        self.avg_lap_time = 0
        self.time_left = 0
        self.cons = 0

        self.laps_left_extra = 0
        self.laps_left_current = 0
        self.target_cons_current = 0
        self.target_cons_extra = 0
        self.laps_left_avg_ol = 0
        self.laps_completed = 0
        self.prev_lap_fuel = 0
        self.avg_cons = 0
        self.consumptions = []

    def update_live_data(self, ir_conn):
        """
        Update the live data each step
        :return:
        """
        self.fuel = ir_conn['FuelLevel']

    def update_over_the_line_data(self, ir_conn):
        """
        Data that is updated only when crossing the start finish line
        :param ir_conn:
        :return:
        """
        if crossed_sf_line(prev_laps_completed=self.laps_completed, ir_conn=ir_conn):
            logging.info(msg=f"crossed_sf_line, prev_laps_completed:{self.laps_completed},{ir_conn['LapCompleted']}")
            if beginning_of_stint(prev_lap_fuel=self.prev_lap_fuel, ir_conn=ir_conn):
                self.reset_variables()
                logging.info('Started a new stint')
            else:
                self.cons = self.prev_lap_fuel - self.fuel
                self.consumptions.append(self.cons)

                # Remove consumption of incomplete lap at the start
                if len(self.consumptions) == 2 and self.consumptions[0] < 0.7 * self.consumptions[1]:
                    logging.info(f"Removed the first consumption: {self.cons}")
                    self.consumptions.pop(0)

                logging.info(f'prev_lap_fuel: {self.prev_lap_fuel}')

                self.avg_cons = stats.mean(self.consumptions)
                self.laps_left_avg_ol = zero_div(x=self.fuel, y=self.avg_cons)

                self.laps_left_extra = math.ceil(self.laps_left_avg_ol)
                self.laps_left_current = math.floor(self.laps_left_avg_ol)

                # Use zero_div() for ZeroDivisionError protection
                self.target_cons_current = zero_div(x=self.fuel - 0.3, y=self.laps_left_current)
                self.target_cons_extra = zero_div(x=self.fuel - 0.3, y=self.laps_left_extra)

                logging.info(f'Fuel across the line: {self.fuel}, consumption last lap: {self.cons}')

                # Calculate how much needs to be refuelled
                self.time_left = ir_conn['SessionTimeRemain']
                self.last_lap_time = ir_conn['LapLastLapTime']
                if self.last_lap_time > 0:
                    self.list_lap_times.append(self.last_lap_time)

                if len(self.list_lap_times) > 0:
                    # Remove the outlap
                    if len(self.list_lap_times) == 2 and self.list_lap_times[0] > 1.2 * self.list_lap_times[1]:
                        logging.info(f"Removed the first laptime (outlap): {self.list_lap_times[0]}")
                        self.list_lap_times.pop(0)

                    self.avg_lap_time = stats.mean(self.list_lap_times)

                self.laps_left = zero_div(self.time_left, self.avg_lap_time)
                self.laps_refuel = self.laps_left - self.laps_left_current
                self.fuel_refuel = self.laps_refuel * self.avg_cons

                logging.info(f"     last_lap_time: {self.last_lap_time}\n"
                             f"     list_lap_times: {self.list_lap_times}\n"
                             f"     laps_left: {self.laps_left}\n"
                             f"     laps_refuel: {self.laps_refuel}\n"
                             f"     fuel_refuel: {self.fuel_refuel}")

            self.prev_lap_fuel = self.fuel
            self.laps_completed = ir_conn['LapCompleted']


def check_iracing(state, ir):
    """
    Update the state.
    :param state:
    :param ir:
    :return:
    """
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        ir.shutdown()
        print('irsdk disconnected')
        logging.info('irsdk disconnected')
    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True
        print('irsdk connected')
        logging.info('irsdk connected')


def init_ir_connection():
    """
    Initialize the iracing connection and the state
    :return: ir_conn, state
    """
    ir_conn = irsdk.IRSDK()
    ir_conn.startup()
    state = State()
    return ir_conn, state


def beginning_of_stint(prev_lap_fuel, ir_conn):
    """
    Return true if started a new stint since last call
    """
    fuel = ir_conn['FuelLevel']

    if fuel > prev_lap_fuel:
        return True
    else:
        return False


def crossed_sf_line(prev_laps_completed, ir_conn):
    """
    Return true if crossed the finish line since last call
    """
    crossed = prev_laps_completed < ir_conn['LapCompleted']

    if crossed:
        return True
    else:
        return False
