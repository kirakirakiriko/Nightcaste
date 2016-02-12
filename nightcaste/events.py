"""The events module conatins all events/actions which can occur in the game.

    TODO:
        Introduce a solution (inharitance?) to represent:
            - events with no target entity
            - events with one target entity
            - events with two target entitys (src and target)

"""
import logging
import Queue

logger = logging.getLogger('events')


class EventManager:
    """The central event manager which stores all events to be executed."""

    def __init__(self):
        # Event queue, which is continuuously processed by process_events
        self.events = Queue.Queue()
        # self.queue = Queue.PriorityQueue()    If priority is needed
        # self.deque = collections.deque()      Super fast unbounded queue
        #                                       without locking

        # Dictionary of processors listening for events of different types
        # {'event_type': EventProcessor}
        self.listeners = {}

    def register_listener(self, event_type, event_processor):
        """Register a processor to delegate the processing of a certain event
        type."""
        logger.debug(
            'Register processor %s for event type %s',
            event_processor,
            event_type)
        if event_type in self.listeners:
            self.listeners[event_type].append(event_processor)
        else:
            self.listeners.update({event_type: [event_processor]})

    def remove_listener(self, event_type, event_processor):
        "Unregisters the processor for events of the specified type."
        logger.debug(
            'Unregister processor %s for event type %s',
            event_processor,
            event_type)
        if event_type in self.listeners:
            try:
                self.listeners[event_type].remove(event_processor)
            except ValueError:
                logger.debug(
                    '%s is already unregistered from %s!',
                    event_processor,
                    event_type)

    def enqueue_event(self, event, rounds=0):
        """Enques an event which will be processed later"""
        self.events.put(event)

    def throw(self, eventIdentifier, data=None):
        """ Enqueues an event from an identifier String"""
        self.events.put(BaseEvent(eventIdentifier, data))

    def process_events(self, round):
        """Process all events in the queue.

            Args:
                round (long): The current round in the game.

            Returns:
                The number of process events in this round.

        """
        processed_events = 0
        while not self.events.empty():
            self.process_event(self.events.get_nowait(), round)
            processed_events += 1
        return processed_events

    def process_event(self, event, round):
        """Process a single event by delegating it to all registered processors.

            Args:
                event(Event): The event to be processed.
                round (long): The current round in the game.

        """
        logger.debug('Process event %s', event)
        if event.type() in self.listeners:
            for processor in self.listeners[event.type()]:
                processor.handle_event(event, round)


class BaseEvent(object):
    """Base class for all events. An Event contains the necessary information
    for a System to react accordingly."""

    def __init__(self, identifier, data):
        self.identifier = identifier
        self.data = data

    def type(self):
        """Returns the class name of the event"""
        # TODO: When refactoring event system, this can be removed, its calls
        # should be changed accordingly
        return self.__class__.__name__

    def __str__(self):
        result = self.type() + " ("
        for prop, val in self.__dict__.iteritems():
            result += str(prop) + ": " + str(val) + ", "
        return result[:-2] + ")"


class Event(object):
    """Base class for all events. An Event contains the necessary information
    for a System to react accordingly."""

    def type(self):
        """Returns the class name of the event"""
        return self.__class__.__name__

    def __str__(self):
        result = self.type() + " ("
        for prop, val in self.__dict__.iteritems():
            result += str(prop) + ": " + str(val) + ", "
        return result[:-2] + ")"


class EntityMoved(Event):
    """Indicates an entity was moved to a new position"""

    def __init__(self, entity, new_x, new_y):
        self.entity = entity
        self.new_x = new_x
        self.new_y = new_y


class KeyEvent(Event):
    """Base Class for key events."""

    def __init__(self, code=None):
        self.code = code


class KeyPressed(KeyEvent):
    """Indicates the user has pressed a key."""
    pass


class KeyReleased(KeyEvent):
    """Indicates the user has released a key."""
    pass


class MapChange(Event):
    """Indicates a map change.

    Args:
        map_name (str): The name of the map to change to.
        level (int): Target map level.

    """

    def __init__(self, map_name, level):
        self.map_name = map_name
        self.level = level


class EntitiesCollided(Event):
    """ Indicated that two or more entities have collided

    Args:
        entities ([int]): The colliding entities
    """

    def __init__(self, entities):
        self.entities = entities


class MenuOpen(Event):
    """Open the menu."""
    pass


class MoveAction(Event):
    """This action indicates that an entity should be moved.

    Args:
        entity (long): The entity which should be moved.
        dx (int): The distance to move horizontal.
        dy (int): The distance to move vertical.

    """

    def __init__(self, entity, dx, dy):
        self.entity = entity
        self.dx = dx
        self.dy = dy


class UseEntityAction(Event):
    """ Use an entity

    Args:
        user (long): Entity ID of the 'user', mostly the player
        direction ((int, int)): Direction in which to look for useables
    """

    def __init__(self, user, direction):
        self.user = user
        self.direction = direction


class ViewChanged(Event):

    def __init__(self, active_view):
        self.active_view = active_view


class WorldEnter(Event):
    """Indicates the player has started the game and enters the world."""
    pass
