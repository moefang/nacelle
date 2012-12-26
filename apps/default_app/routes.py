from webapp2 import Route

ROUTES = [
    # Default route to display a welcome page on a new project build
    (r'/', 'default_app.handlers.NewProjectHandler'),
]
