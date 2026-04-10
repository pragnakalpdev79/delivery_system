from rest_framework.renderers import JSONRenderer
import orjson

class OrjsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return orjson.dumps(data)