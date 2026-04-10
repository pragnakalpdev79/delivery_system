import logging

logger = logging.getLogger('main')

class QueryCountDebugMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response

    def __call__(self,request):
        from django.db import connection
        from django.db import reset_queries

        reset_queries()

        response = self.get_response(request)

        logger.info(f"Total Queries: {len(connection.queries)}")
        for query in connection.queries:
            logger.info(f"{query['time']} : {query['sql']}")

        return response