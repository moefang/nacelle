ROUTES = [
    # Default routes
    (r'/', 'nacelle.handlers.default.NewProjectHandler'),
    (r'/raisetemplate', 'nacelle.handlers.default.TemplateRaiseHandler'),
    (r'/raisejson', 'nacelle.handlers.default.JSONRaiseHandler'),
    # Demoapp routes
    (r'/memorise', 'demoapp.demoapp.DemoMemoHandler'),
    (r'/api/fixed', 'demoapp.demoapp.DemoAPIHandlerFixed'),
    (r'/api/fixed/(.*)', 'demoapp.demoapp.DemoAPIHandlerFixed'),
    (r'/api/dynamic', 'demoapp.demoapp.DemoAPIHandlerDynamic'),
    (r'/api/dynamic/(.*)', 'demoapp.demoapp.DemoAPIHandlerDynamic'),
]

demo_routes = ROUTES
