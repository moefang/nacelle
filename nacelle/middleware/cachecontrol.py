from webob import Request


class CacheControlMiddleware(object):

	def __init__(self, app, max_age=600):
		self.app = app
		self.value = "public, max-age=%d" % max_age

	def __call__(self, environ, start_response):
		request = Request(environ)
		response = request.get_response(self.app)
		if 'Cache-Control' in response.headers and response.headers['Cache-Control'] == 'no-cache':
			response.headers['Cache-Control'] = self.value
		output = response(environ, start_response)
		return output
