import logging

from irsdk import IRSDK


class IRState:
    """
    Class that defines the desired_state of the iRacing sdk connection and the on track desired_state of the car
    """

    def __init__(self):
        self.ir_connected = False

    def update_state(self, ir_sdk: IRSDK):
        """
        Updates the desired_state based on the iRacing sdk data
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
