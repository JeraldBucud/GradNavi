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

    error_code = _get_error_code(exc)
    response.data = {
        "error": {
            "code": error_code,
            "message": _get_error_message(exc),
            "details": _get_error_details(exc, response.data),
        }
    }
    _audit_external_service_failure(
        response=response,
        error_code=error_code,
        context=context,
    )
    return response


def _audit_external_service_failure(
    *,
    response,
    error_code,
    context,
):
    if (
        response.status_code
        != status.HTTP_503_SERVICE_UNAVAILABLE
        or error_code != "external_service_unavailable"
    ):
        return

    try:
        from administration.models import AuditRecord

        view = (
            context
            .get("view")
            if isinstance(context, dict)
            else None
        )

        AuditRecord.objects.create(
            actor=None,
            action="external_service.failure",
            area="external_services",
            target_type="ExternalService",
            target_id="ai_provider",
            metadata={
                "result": "failure",
                "status_code": (
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                "error_code": error_code,
                "view": (
                    view.__class__.__name__
                    if view is not None
                    else ""
                ),
            },
        )

    except Exception:
        return


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
