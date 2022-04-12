from rest_framework.exceptions import APIException


class InvalidTokenException(APIException):
    status_code = 500
    default_detail = {"deatil": "Invalid Token. Please contact administration"}


class TypeException(APIException):
    status_code = 500
    default_detail = {"deatil": "Param is of wrong type."}


class NotEnoughCashException(APIException):
    status_code = 404
    default_detail = {"deatil": "Invalid transaction: insufficient cash balance."}


class InvalidDataException(APIException):
    status_code = 404
    default_detail = {"deatil": "Invalid data."}


class RecordNotFoundException(APIException):
    status_code = 404
    default_detail = {"deatil": "Record not found."}
