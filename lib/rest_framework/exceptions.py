from rest_framework.exceptions import APIException

"""
自定义异常，自定义个类，继承自APIException，并设置.status_code和.default_detail属性
"""
class TeamNotFound(APIException):
    status_code = 404
    default_detail = 'Team not found'
class NotFound(APIException):
    status_code = 404
    default_detail = 'Not found'

class NotAcitve(APIException):
    status_code = 401
    default_detail = 'Not Acitve'

class BadRequest(APIException):
    status_code = 400
    default_detail = 'Parameter format error'

class PermissionDeny(APIException):
    status_code = 403
    default_detail = 'Permission Deny'

class PasswordError(APIException):
    status_code = 422
    default_detail = "Username or Password error"

class StudentNotFound(APIException):
    status_code = 404
    default_detail = 'Student not found'

class CannotComment(APIException):
    status_code = 403
    default_detail = 'Cannot submit comment'

class NotLogin(APIException):
    status_code = 403
    default_detail = "Forbidden, you need to login"

class EducationCrash(APIException):
    status_code = 400
    default_detail = "educational system is not available now"

class TooManyPeople(APIException):
    status_code = 422
    default_detail = "当前代表队报名人数过多"

class Repetition(APIException):
    status_code = 423
    default_detail = "该运动员已经报过名了"

class NotMatch(APIException):
    status_code = 422
    default_detail = "类别与运动员不匹配"

class UnknowError(APIException):
    status_code = 502
    default_detail = "服务器未知错误"

class StatusError(APIException):
    status_code = 422
    default_detail = "比赛已经开始了"

class TooLessReferee(APIException):
    status_code = 422
    default_detail = "裁判数不足3人"

class NoRefereeLeader(APIException):
    status_code = 422
    default_detail = "该组没有裁判长"