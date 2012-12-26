from webapp2 import Route

ROUTES = [
    # sharded counter handler route
    Route(r'/counter/<counter_name>', 'sharded_counter.handlers.CounterHandler'),
]
