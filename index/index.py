# -*- coding: utf-8 -*-
# @Time      :2022/10/7 12:57
# @Author    :Ymir

from libxduauth import *
from GdutUtil import GudtUtil
import re
import json
import functools
import requests


# 获得课表
def handler(event, context):
    """"
    华为函数式工作入口
    """
    # 返回
    ret = {}
    # error message
    flag = event
    try:
        queryStringParameters = event["queryStringParameters"]
        account = queryStringParameters["account"]
        password = queryStringParameters["password"]
        user = GudtUtil(account, password)
        data = user.login()
        ret = {
            "statusCode": 200,
            "body": json.dumps(data, ensure_ascii=False)
        }
    except Exception as e:
        ret = {
            "code": 4000,
            # 为了兼容前端，本科显示的是校区，研究生就显示学院吧
            "data": None,
            "userInfo": None,
            "cookies": None,
            # 学期
            "semester": None,
            "msg": "登录失败",
            "isLive": False
        }
        ret = {
            "statusCode": 200,
            "body": str(ret)
        }
    return ret
