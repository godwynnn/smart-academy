from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import User,AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.db import database_sync_to_async

@database_sync_to_async
def GetUser(token):
    
    return JWTAuthentication().get_user(token)

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        
        query_string=parse_qs(scope['query_string'].decode())
        token=query_string.get('token',[None])[0]
        if token:
            try:
                validated_token=JWTAuthentication().get_validated_token(token)
                scope['user']=await GetUser(validated_token)
            except:
                scope['user']=AnonymousUser()
        else:
            scope['user']=AnonymousUser()

        return await super().__call__(scope, receive, send)