import json
import os
import webapp2
from webapp2_extras import jinja2
from nacelle.conf import settings


class TemplateMixins(object):

    def get_template_dirs(self):
        for root, dirs, files in os.walk(settings.PROJECT_ROOT):
            for dirname in dirs:
                if dirname == 'templates':
                    yield os.path.join(root, dirname)

    def get_jinja2(self, factory=jinja2.Jinja2, app=None, config=None):
        key = 'webapp2_extras.jinja2.Jinja2'
        app = app or webapp2.get_app()
        jinja2 = app.registry.get(key)
        if not jinja2:
            jinja2 = app.registry[key] = factory(app, config)
        return jinja2

    @webapp2.cached_property
    def jinja2(self):
        template_loader = jinja2.jinja2.ChoiceLoader([jinja2.jinja2.FileSystemLoader(x) for x in self.get_template_dirs()])
        template_extensions = [
            'jinja2.ext.autoescape',
            'jinja2.ext.with_',
        ]
        if hasattr(settings, 'TEMPLATE_EXTENSIONS'):
            for ext in settings.TEMPLATE_EXTENSIONS:
                template_extensions.append(ext)

        config = {
            'template_path': 'templates',
            'compiled_path': None,
            'force_compiled': False,
            'environment_args': {
                'loader': template_loader,
                'autoescape': True,
                'extensions': template_extensions,
            },
            'globals': None,
            'filters': None,
        }
        # Returns a Jinja2 renderer cached in the app registry.
        return self.get_jinja2(app=self.app, config=config)

    def template_response(self, _template, **context):
        # Add request object to context
        context['REQUEST'] = self.request

        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)


class JSONMixins(object):

    def json_response(self, response_object):
        # if object is a string just return as is
        if isinstance(response_object, basestring):
            self.response.write(response_object)
        # else attempt to serialise and return
        else:
            response_object = json.dumps(response_object)
            self.response.write(response_object)
        # set the right content-type header
        self.response.headers['Content-Type'] = 'application/json'
