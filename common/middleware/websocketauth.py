from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
import logging

logger = logging.getLogger('main')


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope['user'] = AnonymousUser()

        token = self.get_token_from_scope(scope)
        if token:
            user = await self.get_user_from_token(token)
            scope['user'] = user
        return await super().__call__(scope, receive, send)

    def get_token_from_scope(self, scope):
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]
        return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            uid = access_token.get('user_id')
            if not uid:
                logger.info("Anon")
                return AnonymousUser()
            return get_user_model().objects.get(id=uid)
        except Exception:
            return AnonymousUser()
