import requests
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from dotenv import load_dotenv
import os

load_dotenv()

USER_AUTH_HOST = os.getenv('USER_AUTH_HOST')
VERIFY_TOKEN_URL = 'http://'+ USER_AUTH_HOST + '/api/verify_token/'

class ExternalUser:
    def __init__(self, user_info):
        self._info = user_info
        self.id = user_info.get('id')
        self.username = user_info.get('username')
        self.email = user_info.get('email')
        self.is_superuser = user_info.get('is_superuser')
        self.is_authenticated = True

    def get(self, key, default=None):
        return self._info.get(key, default)

    def __str__(self):
        return self.username or f"External User({self.id})"

class ExternalAuthServiceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            raise AuthenticationFailed(f'Authorization token is missing')

        token = token.split(' ')[1]

        user_info = self.verify_token(token)

        if not user_info:
            raise AuthenticationFailed(f'Invalid token.')

        user = ExternalUser(user_info['user_info'])
        return (user, token)

    def verify_token(self,token):
        try:
            response = requests.post(
                url=VERIFY_TOKEN_URL,
                json={"token":token},
                timeout=3
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            raise AuthenticationFailed('Token verification service is unavailable.')