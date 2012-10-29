routes = [
    # Demoapp routes
    (r'/memorise', 'demoapp.demoapp.DemoMemoHandler'),
    (r'/api/fixed', 'demoapp.demoapp.DemoAPIHandlerFixed'),
    (r'/api/fixed/(.*)', 'demoapp.demoapp.DemoAPIHandlerFixed'),
    (r'/api/dynamic', 'demoapp.demoapp.DemoAPIHandlerDynamic'),
    (r'/api/dynamic/(.*)', 'demoapp.demoapp.DemoAPIHandlerDynamic'),
]
