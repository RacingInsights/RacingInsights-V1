import logging

from irsdk import IRSDK


class State:
    """
    Class that defines the state of the iRacing sdk connection and the on track state of the car
    """

    def __init__(self):
        self.ir_connected = False
        self.on_track = False

    def update_state(self, ir_sdk: IRSDK):
        """
        Updates the state based on the iRacing sdk data
        :param ir_sdk:
        :return:
        """
        if self.ir_connected and not (ir_sdk.is_initialized and ir_sdk.is_connected):
            self.ir_connected = False
            ir_sdk.shutdown()
            print('ir_sdk disconnected')
            logging.info('ir_sdk disconnected')

        elif not self.ir_connected and ir_sdk.startup() and ir_sdk.is_initialized and ir_sdk.is_connected:
            self.ir_connected = True
            print('ir_sdk connected')
            logging.info('ir_sdk connected')

        if self.ir_connected:
            self.on_track = ir_sdk['IsOnTrack']  # 1=Car on track physics running with player in car,
        else:
            # Cannot be in the car if iRacing is not connected
            self.on_track = False

        return self
