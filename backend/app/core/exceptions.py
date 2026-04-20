"""
业务异常定义
"""


class AppException(Exception):
    """业务异常基类"""

    def __init__(self, message: str, code: str = None, status_code: int = 400):
        self.message = message
        self.code = code or "ERROR"
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """认证错误"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTH_ERROR", 401)


class AuthorizationError(AppException):
    """权限错误"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message, "FORBIDDEN", 403)


class NotFoundError(AppException):
    """资源不存在"""

    def __init__(self, resource: str = "资源"):
        super().__init__(f"{resource}不存在", "NOT_FOUND", 404)


class ValidationError(AppException):
    """参数校验错误"""

    def __init__(self, message: str = "参数错误"):
        super().__init__(message, "VALIDATION_ERROR", 400)


class BusinessError(AppException):
    """业务逻辑错误"""

    def __init__(self, message: str = "业务处理失败"):
        super().__init__(message, "BUSINESS_ERROR", 400)


class ExternalServiceError(AppException):
    """外部服务错误"""

    def __init__(self, message: str = "外部服务调用失败"):
        super().__init__(message, "EXTERNAL_ERROR", 503)
