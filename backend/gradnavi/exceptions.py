from rest_framework import status
from rest_framework.exceptions import APIException, ErrorDetail, ValidationError
from rest_framework.views import exception_handler


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The request conflicts with an existing resource."
    default_code = "conflict"


def gradnavi_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    response.data = {
        "error": {
            "code": _get_error_code(exc),
            "message": _get_error_message(exc),
            "details": _get_error_details(exc, response.data),
        }
    }
    return response


def _get_error_code(exc):
    if isinstance(exc, ValidationError):
        return "validation_error"

    if isinstance(exc, ConflictError):
        return "conflict"

    if hasattr(exc, "get_codes"):
        codes = exc.get_codes()
        if isinstance(codes, str):
            return codes

    code = getattr(exc, "default_code", None)
    if code:
        return str(code)

    return "error"


def _get_error_message(exc):
    if isinstance(exc, ValidationError):
        return "The request contains invalid data."

    detail = getattr(exc, "detail", None)
    if isinstance(detail, ErrorDetail):
        return str(detail)
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict) and "message" in detail:
        return str(detail["message"])
    if isinstance(detail, list) and detail:
        return str(detail[0])

    default_detail = getattr(exc, "default_detail", None)
    if default_detail:
        return str(default_detail)

    return "An error occurred."


def _get_error_details(exc, data):
    if isinstance(exc, ValidationError):
        return data

    if isinstance(data, dict):
        return data.get("details", {})

    return {}
