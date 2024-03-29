from django import http
import json


class JSONResponseMixin(object):
	def render_to_response(self, context):
		"Returns a JSON response containing 'context' as payload"
		return self.get_json_response(self.convert_context_to_json(context))

	def get_json_response(self, content, **httpresponse_kwargs):
		"Construct an `HttpResponse` object."
		return http.HttpResponse(content,
		                         content_type='application/json',
		                         **httpresponse_kwargs)

	def convert_context_to_json(self, context):
		"Convert the context dictionary into a JSON object"
		# Note: This is *EXTREMELY* naive; in reality, you'll need
		# to do much more complex handling to ensure that arbitrary
		# objects -- such as Django model instances or querysets
		# -- can be serialized as JSON.
		return json.dumps(context)
