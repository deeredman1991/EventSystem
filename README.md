# EventSystem
A robust events system for python that can register and de-register event handlers and trigger events, uses currying for maximum flexibility when registering handlers.

# Usage
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
  
