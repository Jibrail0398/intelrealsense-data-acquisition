def success(data=None):
    return {"success": True, "data": data or {}}


def error(code, message, http_status=400):
    return (
        {"success": False, "error": {"code": code, "message": message}},
        http_status,
    )
