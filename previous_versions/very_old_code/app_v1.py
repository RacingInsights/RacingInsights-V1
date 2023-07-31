import time
import threading
import logging

import previous_versions.very_old_code.iracing as iracing
import previous_versions.very_old_code.dashboard_v1 as dashboard


def main():
    """
    Main function that initializes both the front end and the backend and assigns and starts the corresponding threads.
    :return:
    """
    logging.basicConfig(filename='app_logs.log', level=logging.INFO)
    [ir_conn, state] = iracing.init_ir_connection()

    telemetry = iracing.CarTelemetry()

    fuel_telemetry_dash = dashboard.FuelTelemetryOverlay()
    # settings_window = dashboard.SettingsWindow()

    # fuel_telemetry_dash thread:
    fuel_telemetry_dash_thread = threading.Thread(target=update_dash, args=[fuel_telemetry_dash, telemetry, ir_conn, state])
    fuel_telemetry_dash_thread.start()

    # main thread:
    fuel_telemetry_dash.mainloop()
    # settings_window.mainloop()


def update_dash(db, tm, ir_conn, state):
    """
    Loop that updates the frontend (dashboard) based on the data it gets from the backend (iRacing telemetry).
    Note that this function is supposed to be called in a different thread than the main.
    :param db:
    :param tm:
    :param ir_conn:
    :param state:
    :return:
    """
    while True:
        # Get the telemetry data
        tm.step(state=state, ir_conn=ir_conn)

        # Update the frontend if still connected
        if state.ir_connected:
            db.fuelvar.set(f"{tm.fuel:.2f}")
            db.lastvar.set(f"{tm.cons:.2f}")
            db.avgvar.set(f"{tm.avg_cons:.2f}")
            db.targetcurrentvar.set(f"{tm.target_cons_current:.2f}")
            db.targetextravar.set(f"{tm.target_cons_extra:.2f}")
            db.rangevar.set(f"{tm.laps_left_current}")
            db.rangeextravar.set(f"{tm.laps_left_extra}")

        # Go to sleep. Minimum step-time is (1/60) seconds (=approx 17ms) as iRacing telemetry is updated at 60 Hz.
        step_time = 1
        time.sleep(step_time)
