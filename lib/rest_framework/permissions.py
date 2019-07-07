from rest_framework import permissions
from lib.rest_framework.exceptions import *
from lib.rest_framework.util import decode_jwt

import logging

logger = logging.getLogger(__name__)

def check_token(func):
    """
    装饰器，验证taoke_token
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        # TODO: 注意，这里粗略的获取了request对象，目前该装饰器只能装饰request在函数的第二个参数的函数
        taoke_token = args[1].META.get("HTTP_AUTHENTICATION")
        print(taoke_token)
        if taoke_token:
            try:
                info = decode_jwt(taoke_token) #验证token
            except:
                logger.info("Wrong oken: {token}".format(token=taoke_token))
                raise NotLogin
            else:
                # token正确，将用户信息存入request.META["REMOTE_USER"]
                args[1].META["REMOTE_USER"] = info
                return func(*args, **kwargs)
        else:
            logger.info("Without token! {request}".format(request=args[1].META))
            raise NotLogin

    return wrapper



def check_admin_token(func):
    """
    装饰器，验证admin_token
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        taoke_token = args[1].META.get("HTTP_AUTHENTICATION")
        if taoke_token:
            try:
                info = decode_jwt(taoke_token) #验证token
            except:
                logger.info("Wrong oken: {token}".format(token=taoke_token))
                raise NotLogin
            else:
                # token正确，将用户信息存入request.META["REMOTE_USER"]
                if info.get("type") == "admin":
                    args[1].META["REMOTE_USER"] = info
                    return func(*args, **kwargs)
                else:
                    raise PermissionDeny
        else:
            logger.info("Without admin token! {request}".format(request=args[1].META))
            raise NotLogin

    return wrapper

