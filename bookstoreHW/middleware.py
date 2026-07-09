import datetime

import structlog

logger = structlog.get_logger()

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info('Request received', request=request)
        response = self.get_response(request)
        logger.info('Response proceed', response=response)
        response['my_mega_header'] = str(datetime.datetime.now())
        return response