'''
    An Event System Framework for Python that attempts to be as flexible and implementation agnostic as possible.
'''
import threading
from collections.abc import Callable

class Event():
    def __init__(self, type=None):
        self.type = type
        
    def __str__(self):
        return self.type

class EventsManager():
    '''
        The main class that deals with registering and deregistering handlers as well as emitting event signals.
    '''
    _handlers = {}
    
    def __init__( self, name: str ="Events Manager", thread_safe: bool = False):
        '''
            Optionally takes in a name of type string. If a name is not provided the name will be set to "Events Manager" by default.
            Also takes in an optional 'thread_safe' boolean and will attempt to automatically support multi-threading by thread-locking the register and deregister methods.
                WARNING! This only effects the EventsManager! This does not make your enitre codebase thread safe! It is up to you to ensure that you are locking read/write operations especially after calling the "emit()" method.
        '''
        self.name = name
        self.thread_safe = thread_safe
        if self.thread_safe:
            self.thread_lock = threading.Lock()


    @property
    def events_list(self) -> []:
        '''
            returns a list of events that the event manager is actively managing.
            events may be of type int, float, string, or boolean.
        '''
        return list( self._handlers.keys() )

    def get_registered_handlers(self, event = '') -> []:
        '''
            returns a dictionary of events and their handlers. If an optional 'event' keyword parameter is provided; this method will only return a list of handler objects for that event.
            handler objects are just dictionaries that contain the keys "args", "handler", and "handler_id"
                args is a tuple containing the defaults args (stored as a tuple) and kwargs (stored as a dictionary) of the handler respectively.
                    get_registered_handlers()[event]['args'][0] is a tuple of args.
                    get_registered_handlers()[event]['args'][1] is a dictionary of kwargs.
                handler is a reference to the handler callable.
                hander_id is a unique id of type integer used for tracking and deregistering handlers.
        '''
        #TODO^: Change args[0] and args[1] to args and kwargs respectively. (maybe)

        if event == '':
            return self._handlers
        if not event in self._handlers:
            return

        return self._handlers[event]


    def register(self, event, handler: Callable, *args, **kwargs) -> None:
        '''
            Register a handler to listen to an event with a list of optional args and kwargs. The handler will be called with default args provided when the event is emitted.
            event parameter must be of type int, float, string, or boolean
            handler parameter must be callable (typically a function, method, or class).
        '''

        if self.thread_safe:
            self.thread_lock.acquire()

        if not callable(handler):
            raise TypeError(f"'{handler}' is not callable.")

        if not event in self._handlers:
            self._handlers[event] = []

        handler_id: int = 0
        unique: bool = False
        while not unique:
            unique = True
            for _handler in self._handlers[event]:
                if handler_id == _handler['handler_id']:
                    unique = False
                    handler_id += 1

        self._handlers[event].append( 
                { 'handler': handler, 
                  'handler_id': handler_id, 
                  'args': (args, kwargs) 
                }
            )

        if self.thread_safe:
            self.thread_lock.release()


    def deregister(self, event, handler_callable_or_id = None, *args, **kwargs) -> None:
        '''
            Deregister a handler and stop it from listening to an event by providing a reference to the handler callable or id. Additionally you may provide default args and kwargs to narrow your search.
        '''

        if self.thread_safe:
            self.thread_lock.acquire()

        assert (event in self._handlers) , f"Event '{event}' does not exist in {self.name}!"

        if handler_callable_or_id:
            assert (callable( handler_callable_or_id ) or type(handler_callable_or_id) == type(1)), f"EventsManager.deregister requires either a handler function or a handler ID as it's second argument"

        pop_indexes = []

        for handler in self._handlers[event]:
            if handler_callable_or_id != 0 and not handler_callable_or_id:
                pop_indexes.append( self._handlers[event].index( handler ) )
                continue
            
            registered_handler_func = handler['handler']
            registered_handler_id = handler['handler_id']
            registered_handler_args = handler['args'][0]
            registered_handler_kwargs = handler['args'][1]

            if ( callable( handler_callable_or_id ) and handler_callable_or_id == registered_handler_func ) or ( handler_callable_or_id == registered_handler_id ) :
                if args and not kwargs:
                    if args == registered_handler_args:
                        pop_indexes.append( self._handlers[event].index( handler ) )

                elif kwargs and not args:
                    if kwargs == registered_handler_kwargs:
                        pop_indexes.append( self._handlers[event].index( handler ) )

                elif args and kwargs:
                    if args == registered_handler_args and kwargs == registered_handler_kwargs:
                        pop_indexes.append( self._handlers[event].index( handler ) )

                else:
                    pop_indexes.append( self._handlers[event].index( handler ) )

        # Prepares pop_indexes list to handle removing values while iterating.
        for index, value in enumerate( pop_indexes ):
            pop_indexes[index] = value - index
            
        for index in pop_indexes:
            self._handlers[event].pop( index )
            
        if len( self._handlers[event] ) == 0:
            del self._handlers[event]

        if self.thread_safe:
            self.thread_lock.release()


    def emit(self, event, *args, **kwargs) -> None:
        '''
            Emit an event signal by providing an event of type int, float, string, or boolean. 
            Args and kwargs provided to EventsManager.emit() will overwrite any default values that were attached to the event handler on registration when an event is emitted.
        '''

        if not event in self._handlers:
            return

        for handler in self._handlers[event]:
            registered_handler_func = handler['handler']
            registered_handler_id = handler['handler_id']
            registered_handler_args = handler['args'][0]
            registered_handler_kwargs = handler['args'][1]

            new_args = args if args else registered_handler_args

            new_kwargs = registered_handler_kwargs.copy()
            if new_kwargs:
                new_kwargs.update( kwargs )
            else:
                new_kwargs = kwargs

            if new_args and not new_kwargs:
                registered_handler_func( *new_args )
            elif new_kwargs and not new_args:
                registered_handler_func( **new_kwargs )
            elif new_args and new_kwargs:
                registered_handler_func( *new_args, **new_kwargs )
            else:
                registered_handler_func()
    
    def __str__(self) -> str:
        return self.name + ': \n    "' + '", \n    "'.join( list( f'{key}": {len(value)}' for key, value in self._handlers.items() ) ) + '\n'


if __name__ == "__main__":
    events = EventsManager("Main Events Manager") # Name Argument is optional

    def function_handler( text_input, optional="handler" ):
        print( f"Got input {text_input}! Optional argument from {optional}." )

    handler = function_handler
    
    print()
    events.register( 'recieved input', handler ) # register handler to the 'recieved input' with no default arguments.
    events.emit('recieved input', 'from event emitter') # emit 'recieved input' event with the default argument(s) ('from event emitter')
    #>> Got input from event emitter! Optional argument from handler.
    
    print()
    events.deregister( 'recieved input' ) # Deregister all handlers from the 'recieved input' event.
    events.register( 'recieved input', handler, 'from event registration') # register handler to the 'recieved input' event with the default argument 'from event registration'.
    events.emit( 'recieved input' ) # emit 'recieved input' event
    #>> Got input from event registration! Optional argument from handler.

    print()
    events.emit( 'recieved input', 'from event emitter' ) # emit 'recieved input' event but replace the default argument(s) with ('from event emitter')
    #>> Got input from event emitter! Optional argument from handler.
    
    print()
    events.deregister( 'recieved input', handler ) # Deregister all handlers using our specific handler from the 'recieved input' event.
    events.emit( 'recieved input' ) # emit 'recieved input' event but nothing should happen because no events are registered to the Events Manager.
    print("No Output!")
    #>> No Output!

    print()
    events.register( 'recieved input', handler, 'from event registration') # register handler to the 'recieved input' event with the default argument 'from event registration'.
    events.register( 'recieved input', handler, 'from event registration2') # register handler to the 'recieved input' event with the default argument 'from event registration2'.
    events.emit( 'recieved input', optional='emitter' ) # emit 'recieved input' event. With the optional keyword argument 'optional=emitter'
    #>> Got input from event registration! Optional argument from emitter.
    #>> Got input from event registration2! Optional argument from emitter.
    
    print()
    events.deregister( 'recieved input', handler, 'from event registration') # only deregister handlers with the default argument 'from event registration'.
    events.register( 'recieved input', handler, 'from event registration', optional ='registration') # register handler to the 'recieved input' event with the default argument 'from event registration2' and the optional keyword argument 'optional=registration' 
    events.emit( 'recieved input' ) # emit 'recieved input' event.
    #>> Got input from event registration2! Optional argument from handler.
    #>> Got input from event registration! Optional argument from registration.

    print()
    class ClassHandler():
        def __init__(self, text_input):
            print( f"Got input {text_input}!" )

    handler = ClassHandler
    
    events.register( 'recieved input', handler, 'from class handler registration') # register handler to the 'recieved input' event with the default argument 'from class handler registration'.
    events.emit( 'recieved input' ) # emit 'recieved input' event
    #>> Got input from event registration2! Optional argument from handler.
    #>> Got input from event registration! Optional argument from registration.
    #>> Got input from class handler registration!

    events.deregister( 'recieved input', handler, 'from class handler registration') # only deregister handlers with the default argument 'from class handler registration'.

    print()
    class Event2(): # Create a new genertic object called Event.
        pass

    event1 = Event('input event') # Create an instance of the Event object and keep a reference to it.
    print( event1.type )
    #>> input event
    print( event1 )
    #>> input event

    print()
    event2 = Event2() # Create another instance of the Event2 object and keep a reference to it.
    
    events.register(event1, handler, 'from class event1 registration') # Register the handler using the event1 object reference.
    events.register(event2, handler, 'from class event2 registration') # Register the handler using the event2 object reference.
    events.emit( event1 ) # Emit an event signal using the event1 object reference.
    #>> Got input from class event1 registration!
    events.emit( event2 ) # Emit an event signal using the event2 object reference.
    #>> Got input from class event2 registration!
    
    events.deregister( event1 ) # Deregister all handlers associated with the event1 object reference.
    events.deregister( event2 ) # Deregister all handlers associated with the event2 object reference.

    print()
    print( events.events_list ) # Get a list of all events currently being managed by the event manager.
    #>> ['recieved input']

    print()
    import pprint as p
    p.pprint( events.get_registered_handlers('recieved input') ) # Get a list of dictionaries representing the registered handlers for the 'recieved input' event.
    #>> [{'args': (('from event registration2',), {}),
    #     'handler': <function function_handler at 0x0000024EBCEE8708>,
    #     'handler_id': 1},
    #    {'args': (('from event registration',), {'optional': 'registration'}),
    #     'handler': <function function_handler at 0x0000024EBCEE8708>,
    #     'handler_id': 0}]

    print()
    events.deregister( 'recieved input', 0 ) # Deregister handler by id.
    p.pprint( events.get_registered_handlers() ) # Get a dictionary[String, List] representing all events and their handlers.
    #>> {'recieved input': [{'args': (('from event registration2',), {}),
    #                        'handler': <function function_handler at 0x0000022E03BE8708>,
    #                        'handler_id': 1}]}

    print()
    print( events ) # The __str__() method of the EventsManager class returns a pretty string for console printing and logging containing a list of events being managed by the manager as well as how many handlers are registered to each event.
    #>> Main Event Manager:
    #       "recieved input": 1
