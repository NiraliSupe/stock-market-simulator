from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class AuthMixin:
    """
    It verifies if the current user is authenticated.
    Available authentication ways:
        - django user authentication
        - Json Web Token
    """
    Authentication_classes = (SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication, )
