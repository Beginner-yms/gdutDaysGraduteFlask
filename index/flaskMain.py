# -*- coding: utf-8 -*-
# @Time      :2023/1/14 14:23
# @Author    :Ymir
# 本地测试文件

import flask
import re
from flask_cors import CORS
import json
from GdutUtil import GudtUtil, UtilsException
from libxduauth.sites.ids import CaptchaException, AccountError
from flask import request, jsonify
from gevent import pywsgi

import time

app = flask.Flask(__name__)

# 防止自动转unicode
app.config['JSON_AS_ASCII'] = False

# 注册CORS, "/*" 允许访问所有api
CORS(app, resources=r'/*')


@app.route('/api/test', methods=["POST", "GET"])
def get_kc():
    ret = {
        "code": 200,
        "Hi": "Ymri!"
    }
    return flask.jsonify(ret)


@app.route('/api/gdutLogin', methods=["POST", "GET"])
def login():
    t = time.time()
    ret = {
        "code": 4000,
        # 为了兼容前端，本科显示的是校区，研究生就显示学院吧
        "data": None,
        "userInfo": None,
        "cookies": None,
        # 学期
        "semester": None,
        "msg": "密码错误！",
        "isLive": False
    }
    # try:

    # print(account, password)
    # 这里会出现js 提醒，
    try:
        data = request.get_json()
        account = data["account"]
        password = data["password"]
    except Exception as e:
        ret = {
            "code": 404,
            "msg": "参数异常！"
        }
        return flask.jsonify(ret)
    try:
        user = GudtUtil(account, password)
        ret = user.login()
        return flask.jsonify(ret)
    except CaptchaException as e:
        ret['msg'] = "请回网页输验证码"
        return flask.jsonify(ret)
    except AccountError as e:
        ret['msg'] = "密码错误"
        return flask.jsonify(ret)
    except UtilsException as e:
        ret['msg'] = "服务器网络异常，请重试！"
        return flask.jsonify(ret)
    except Exception as e:
        ret['msg'] = "服务器网络异常，请重试！"
        return flask.jsonify(ret)


@app.route('/api/getUserInfo', methods=["POST", "GET"])
def get_user_info():
    t = time.time()
    # 假定前端传入的是json类型
    data = request.get_json()
    # print(data)
    try:
        cookies = data["cookies"]
        # 获得个人信息
        ret = GudtUtil.login_after_info(cookies=cookies)
        end = time.time()
        # print("耗时：" + str(end - t))
    except Exception as e:
        ret = {
            "code": 4000,
            "data": None,
            "msg": "请检查参数！"
        }
        print(e)
    # 如果获取的是空，则重新登录返回
    return flask.jsonify(ret)


@app.route('/api/checkCaptcha', methods=["POST", "GET"])
def check_need_captcha():
    """"
    检查是否需要验证码
    """
    t = time.time()

    # 假定前端传入的是json类型
    try:
        data = request.get_json()
        # print(data)
        username = data["stdId"]
        # 获得个人信息
        ret = GudtUtil.check_need_Captcha(username=username)
        end = time.time()
        # print("耗时：" + str(end - t))
    except Exception as e:
        ret = {
            "code": 4000,
            "data": None,
            "msg": "请检查参数！",
            "isLive": False
        }
        print(e)
    # 如果获取的是空，则重新登录返回
    return flask.jsonify(ret)


@app.route('/api/getCk', methods=["POST", "GET"])
def get_ck():
    t = time.time()
    # 假定前端传入的是json类型
    try:
        data = request.get_json()
        # print(data)
        cookies = data["cookies"]
        wid = data["semester"]
        ret = GudtUtil.get_ck_static(cookies=cookies, wid=wid)
        end = time.time()
    except Exception as e:
        ret = {
            "code": 4000,
            "data": None,
            "isLive": False,
            "msg": "请检查参数！"
        }
        print(e)
    # print("耗时：" + str(end - t))
    # 如果获取的是空，则重新登录返回
    return flask.jsonify(ret)


@app.route('/api/score', methods=["POST", "GET"])
def get_score():
    """
    考试成绩接口
    :return:
    """
    t = time.time()
    # 假定前端传入的是json类型
    try:
        data = request.get_json()
        # print(data)
        cookies = data["cookies"]
        ret = GudtUtil.get_exam_data(cookies=cookies)
        end = time.time()
    # print("耗时：" + str(end - t))
    # 如果获取的是空，则重新登录返回
    except Exception as e:
        ret = {
            "code": 4000,
            "data": None,
            "isLive": False,
            "msg": "请检查参数！"
        }
        print(e)
    return flask.jsonify(ret)


@app.route('/api/live', methods=["POST", "GET"])
def check_live():
    """
    检查用户信息是否有效
    :return:
    """
    # 假定前端传入的是json类型
    try:
        data = request.get_json()
        cookies = data["cookies"]
        ret = GudtUtil.get_user_info_by_cookies(cookies=cookies)
    except Exception as e:
        ret = {
            "code": 4000,
            "data": None,
            "isLive": False,
            "msg": "请检查参数！"
        }
    return flask.jsonify(ret)


server = pywsgi.WSGIServer(('0.0.0.0', 8888), app, )
server.serve_forever()

if __name__ == "__main__":
    run_code = 0
