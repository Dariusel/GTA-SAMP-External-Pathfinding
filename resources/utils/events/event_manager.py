from enum import Enum



class EventType(Enum):
    BlipChangedEvent = 0
    MarkerChangedEvent = 1
    DestinationReachedEvent = 2



class EventManager():
    _instance = None
    events = {}

    def __new__(cls):
        if EventManager._instance:
            return
        
        EventManager._instance = super().__new__(cls)
        EventManager.init_events()

    
    def init_events():
        from resources.utils.events.category.main import main_events
        from resources.utils.events.category.gps import gps_events


    def subscribe(subscriber, event_type):
        if event_type not in EventManager.events:
            EventManager.events[event_type] = []

        if subscriber not in EventManager.events[event_type]:
            EventManager.events[event_type].append(subscriber)


    def send_event(event_type, *args, **kwargs):
        if event_type in EventManager.events:
            for subscriber in EventManager.events[event_type]:
                subscriber(*args, **kwargs)

EventManager()