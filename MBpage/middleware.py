from django.db.utils import OperationalError
from django.http import HttpResponse
from django.template import loader


class DBErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, OperationalError):
            template = loader.get_template('db_error.html')
            return HttpResponse(template.render({}, request), status=503)
        return None
