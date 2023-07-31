# NOTE: This has been removed for updating configuration
# The alternative is to use @property at the side which would be the subscriber in case of an event handler
# Property should then return the specific attribute related to that event

from enum import Enum, auto


class RIEventTypes(Enum):
    CLOSE_APP = auto()  # Can be posted by main screen to close the entire app
    OPEN_FUEL_SETTINGS = auto()  # Posted by pressing fuel settings button in main
    FUEL_FEATURE_CHANGE = auto()  # Posted when a feature of the fuel overlay is changed
    OPEN_RELATIVE_SETTINGS = auto()  # Posted by pressing relative_time settings button in main
    RELATIVE_FEATURE_CHANGE = auto()  # Posted when a feature of the relative is changed
    ESTIMATION_DATA_LOGGED = auto()  # Posted when the RelativeDataLogger completed logging


"""
Event handler to implement an observer (listener) pattern.
Its main use case is handling the events of user inputs and communicating it to the UI elements
"""
subscribers = dict()  # Contains event type and all the functions that are subscribed


def subscribe(event_type: RIEventTypes, fn):
    """Function to append a specific function/method (fn) to the subscribers of certain event"""
    if event_type not in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)


def post_event(event_type: RIEventTypes, data=None):
    """
    This gets called when a new event occurs.
    It will pass the related data to each of the subscribers.
    """
    if event_type not in subscribers:
        return

    for subscribed_function in subscribers[event_type]:
        if data:
            subscribed_function(data)
        else:
            subscribed_function()
