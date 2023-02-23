# -*- coding: utf-8 -*-
# @Time      :2023/1/14 14:32
# @Author    :Ymir

from libxduauth import *
import re
import json
import copy
import requests
from libxduauth.utils.aes import GdutCrypto
import time

class UtilsException(Exception):
    pass


# 获得课表
class GudtUtil(object):
    """
    登录和数据处理，直接拿到数据并返回
    """

    def __init__(self, acount, password):
        # 自动登录
        aes = GdutCrypto('gdutgdutgdutgdut')
        password = aes.decrypt(password)
        # print("密码解密，%s" % password)
        self.session = EhallSession(acount, password)
        """
        @TODO 
        这里有个学期时间获取，
        """
        self.semester_url = "http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/kfdxnxqcx.do"
        self.ck_url = "http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/xspkjgcx.do?XNXQDM=20221&*order=<*order>"
        self.__login_url = "https://authserver.gdut.edu.cn/authserver/login?service=http%3A%2F%2Fehall.gdut.edu.cn%2Fgsapp%2Fsys%2Fwdkbapp%2F*default%2Findex.do%3Famp_sec_version_%3D1%26gid_%3DanF6SjBZK2R1WVVlQ2l5cjJRSlBlckVnR05sSFVYRlVRWHVEYTVpT01WQ3Z0M01ENktsWXA5cHoveWxwNTdaSU9PMVRjWTF1Wk90Y3g4QjVOb3VhbWc9PQ%26EMAP_LANG%3Dzh%26THEME%3Dgolden%23%2Fxskcb"
        # 建议一次性把所有的cookies 全部获取
        self.user_info_url = "http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/wdkcb/initXsxx.do?XH="
        self.cookies = None
        self.wid = None

    def __login(self, try_again_times=3, url=None):
        """
        用于SSO中激活接口（拿到cookies授权）
        :param try_again_times:
        :url: 登录的url
        :return:
        """
        try:
            if not url:
                url = self.__login_url
            self.session.post(url, timeout=3)
        except Exception as e:
            print(e)
            try_again_times -= 1
            if try_again_times > 0:
                self.__login(try_again_times)
            else:
                raise UtilsException("接口授权失败")

    def __get_semester_message(self, try_again_times=3):
        """
        获得学期信息,返回最新的一条学期信息
        详细信息见接口：
            http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/kfdxnxqcx.do
        :return:
        """
        # 激活url
        self.__login(url=self.semester_url)
        while try_again_times > 0:
            try:
                # 登录
                response = self.session.request("POST", self.semester_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    try:
                        data = data["datas"]
                        data = data["kfdxnxqcx"]
                        data = data["rows"]
                        semester = data[0]
                        wid = semester["WID"]
                        self.wid = wid
                        return wid
                    except Exception as e:
                        print(e)
                        return None
            except Exception as e:
                print(e)
                try_again_times -= 1
            finally:
                pass
        return None

    @staticmethod
    def get_semester_message_by_cookies(cookies):
        """
        根据cookies 获取最新的学期信息
        :param cookies:
        :return:
        """
        url = "http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/kfdxnxqcx.do"
        response = GudtUtil.requests_by_cookies(url, cookies=cookies)
        if response:
            data = response
            try:
                data = data["datas"]
                data = data["kfdxnxqcx"]
                data = data["rows"]
                semester = data[0]
                wid = semester["WID"]
                wid = wid
                return wid
            except Exception as e:
                print(e)
                return None

    def get_kc_message(self, wid=None, try_again_times=3):
        """
        param try_again_times
        :return: json类型的课程数据
        """
        # 这里应该分开，方便优化
        if not wid:
            wid = self.__get_semester_message()
        if not wid:
            Exception("error!wid is None")
        # 激活url
        # print("获得最新的学期信息：" + str(wid))
        self.ck_url = self.ck_url.replace("20221", str(wid))
        self.__login(url=self.ck_url)
        while try_again_times > 0:
            try:
                # 登录
                payload = {}
                response = self.session.request("POST", self.ck_url, data=payload, timeout=5)
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
            except Exception as e:
                try_again_times -= 1
            finally:
                pass

    @staticmethod
    def get_kc_message_static(cookies, wid, try_again_times=3):
        """
        直接使用cookies获取版本，优化用户体验
        :param cookies: cookies
        :param wid: 学期id
        :return: json类型的课程数据
        """
        if cookies is None or wid is None:
            return None
        ck_url = "http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/xspkjgcx.do?XNXQDM=20221&*order=<*order>"
        ck_url = ck_url.replace("20221", str(wid))
        while try_again_times > 0:
            try:
                payload = {}
                headers = {
                    'Cookie': cookies,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/89.0.4389.114 Safari/537.36',
                }
                temp_session = requests.session()
                response = temp_session.post(ck_url, headers=headers, data=payload, timeout=5)
                if response.status_code == 200:
                    ret = response.json()
                    temp_session.close()
                    return ret
                else:
                    return None
            except Exception as e:
                try_again_times -= 1
            finally:
                pass

    @staticmethod
    def requests_by_cookies(url, cookies, try_again_times=3, postData=None, is_urlform_urlencoded=False):
        """
        请求工具
        :param try_again_times:
        :param url:  地址
        :param cookies:  cookies
        :param is_urlform_urlencoded: 是否是header是否使用urlendcoded
        :return:
        """
        while try_again_times > 0:
            try:
                payload = {}
                if postData:
                    payload = postData
                headers = {
                    'Cookie': cookies,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/89.0.4389.114 Safari/537.36',

                }
                if is_urlform_urlencoded:
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                # 底层还是开个session，默认keep-alive?
                temp_session = requests.session()
                response = temp_session.post(url, headers=headers, data=payload, timeout=5)
                if response.status_code == 200:
                    ret = response.json()
                    temp_session.close()
                    return ret
                else:
                    return None
            except Exception as e:
                print(e)
                try_again_times -= 1
            finally:
                pass
        return None

    def __cookies_2_list(self):
        """
        cookies2 list
        只找到需要的cookies
        :return:
        """
        cookies = None
        if not self.cookies:
            cookies = self.session.cookies
        else:
            return self.cookies
        ret_cookies = ""
        flag = False
        for i in cookies:
            temp_cookies = str(i).split("for")[0]
            temp_cookies = temp_cookies.replace(" ", "").replace("Cookie", "").replace("<", "")
            # 只过课表 cookies 防止cookies 泄露
            if "MOD_AUTH_CAS=" in temp_cookies:
                flag = True
            if flag:
                ret_cookies += temp_cookies + ";"
        return ret_cookies

    def get_user_info(self):
        """
        获得用户信息,接口参数直接返回
        "XH":  学号
        "XM": 姓名
        "YXDM": 不知道
        "YXDM_DISPLAY":学院中文
        "YXYWMC":学院英文
        :return:
        """
        # 激活url
        self.__login(url=self.user_info_url)
        try:
            # 登录
            response = self.session.request("GET", self.user_info_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                try:
                    data = data["data"]
                    user_info = data[0]
                    return user_info
                except Exception as e:
                    print(e)
                    return None
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_user_info_by_cookies(cookies):
        """"
        通过cookies获取用户信息,同时检查cookies是否有效
        :param cookies: cookies
        """
        url = "http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/wdkcb/initXsxx.do?XH="
        userInfo = GudtUtil.requests_by_cookies(url=url, cookies=cookies)
        ret = {
            # 请求成功的code
            "code": 4000,
            "data": None,
            "isLive": False
        }
        if userInfo:
            userInfo = userInfo["data"][0]
            ret["data"] = userInfo
            ret["isLive"] = True
        return ret

    @staticmethod
    def get_ck_static(cookies, wid):
        """
        如果cookies过期，请重新登录
        :param cookies:
        :param wid:
        :return:
        """
        data = GudtUtil.get_kc_message_static(cookies, wid)
        # print(data)
        if not data:
            ret = {
                # 请求成功的code
                "code": 4000,
                "data": None,
                "msg": "202202",
                "isLive": False
            }
            return ret
        ret = GudtUtil.kc_data_clear(data)
        ret["isLive"] = True
        return ret

    def login(self):
        """
        用户登录
        返回 个人信息、cookie、学期
        :return:
        """
        # 激活url
        start = time.time()
        self.__login()
        # 个人信息
        # user_info = self.get_user_info()
        # 学期
        # wid = self.__get_semester_message()
        # 课程权限获取
        self.__login(url=self.ck_url)

        # print("花费" + str(time.time() - start))
        # 关闭连接，防止出现连接异常
        self.session.close()
        cookies = self.__cookies_2_list()
        ret = {
            "code": 4000,
            # 为了兼容前端，本科显示的是校区，研究生就显示学院吧
            # "data": user_info["YXDM_DISPLAY"],
            "data": "研究生院",  # 后续获取校区信息
            "userInfo": None,
            "cookies": cookies,
            # 学期
            "semester": "20222",
            "msg": "登录成功",
            "isLive": True
        }
        if not cookies:
            ret["code"] = 4000
            ret["msg"] = "登录失败"
            ret["isLive"] = False
        return ret

    @staticmethod
    def __load_json():
        """
        加载json文件，测试使用
        :param json_path:
        :return:
        """
        json_path = "data.json"
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_ck(self):
        """
        返回课表信息
        :return:
        """
        self.__login()
        data = self.get_kc_message()
        ret = self.kc_data_clear(data)
        ret["msg"] = self.wid
        return ret

    @staticmethod
    def kc_data_clear(data):
        """
        数据清洗后返回
        1.拿到原始数据，然后把周次相同和星期相同的课程合并，
        2.根据周次进行展开
        3.合并连续的课程
        :return:
        """
        if data == None:
            return None
        data = data["datas"]
        data = data["xspkjgcx"]
        data = data["rows"]
        ret_data = []
        map = {}
        id = 0
        # 使用Map进行保存，然后list获取，接着按照星期，
        for i in data:
            # 清洗的时候使用
            temp = {
                "ad": i["JASMC"],  # 教室
                "cn": i["KCMC"],  # 课程名
                "tn": i["JSXM"],  # 老师
                "wd": i["XQ"],  # 星期,
                "w": i["ZCMC"],  # 周次，但是需要修改
                "cc": i["BJMC"],  # 课程描述，
                "cs": [],  # 等待合并的数据
                "key": str(i["KCMC"]) + str(i["ZCMC"]) + str(i["XQ"]),  # map 主键，课程名+周次+星期
                "xs": i["XS"],  # 周次情况
                # "KSJCDM": i["KSJCDM"],
                # "JSJCDM": i["JSJCDM"]
            }
            # 过滤
            temp["ad"] = str(temp["ad"]).replace("（", "").replace("）", "").replace(" ", "").replace("专用课室",
                                                                                                    "").replace(
                "专用教室", "")
            # 获得开始课程
            # 检查数据
            if map.get(temp["key"]) is None:
                # 添加课程
                temp["cs"].append(i["KSJCDM"])

                map[temp["key"]] = temp
            else:
                # 合并课程
                map[temp["key"]]["cs"].append(i["KSJCDM"])

        for key, value in map.items():
            # 清洗课程
            value["cs"].sort()
            temp_cs = ""
            for i in value["cs"]:
                temp_cs += str(i) + ","
            temp_cs = temp_cs[:-1]
            value["cs"] = temp_cs
            # 周次提取
            temp_w = value["w"].replace("周", "")
            temp_w = temp_w.split(",")
            # id 在前端用来显示颜色
            value["id"] = id
            id = id + 1
            for i in temp_w:
                if i.find("-") != -1:
                    temp_s_i = i.split("-")
                    for j in range(int(temp_s_i[0]), int(temp_s_i[1]) + 1):
                        temp_i = copy.deepcopy(value)
                        temp_i["w"] = str(j)
                        ret_data.append(temp_i)
                else:
                    temp_i = copy.deepcopy(value)
                    temp_i["w"] = i
                    ret_data.append(temp_i)
        # 把ret_data 按照w 排序
        ret_data.sort(key=lambda x: (x["w"]))
        ret = {}
        for i in range(1, 22):
            temp_list = []
            for j in ret_data:
                if j["w"] == str(i):
                    temp_list.append(j)
            # 同一周的保存在一起
            # 根据cs排序，需要把课程节次排个序
            """"
            @todo
            这里可能有潜在的bug，如果一天上2门一样的课，会自动合并在一起，前端显示会出现问题
            """
            temp_list.sort(key=lambda x: (x["wd"], x["cn"], x["cs"]))
            j = 1
            while j < len(temp_list):
                if temp_list[j]["wd"] == temp_list[j - 1]["wd"] and temp_list[j]["cn"] == temp_list[j - 1]["cn"]:
                    str_cs = temp_list[j - 1]["cs"] + "," + temp_list[j]["cs"]
                    str_cs = str_cs.split(",")
                    num_cs = [int(x) for x in str_cs]
                    num_cs.sort()
                    str_cs = ""
                    for m in num_cs:
                        str_cs += str(m) + ","
                    str_cs = str_cs[:-1]

                    temp_list[j - 1]["cs"] = str_cs
                    temp_list.pop(j)
                j += 1
            ret[str(i)] = temp_list
        # 特殊的放回数据
        ret = {
            # 请求成功的code
            "code": 4000,
            "data": ret,
            "msg": "202202",
            "isLive": True
        }
        return ret

    @staticmethod
    def get_exam_data(cookies):
        """
        通过cookies 自动成绩数据
        :return:
        # 研究生只有一个，成绩按照逆序排放
        接口详细： https://ehall.gdut.edu.cn/gsapp/sys/wdcjapp/modules/wdcj/xscjcx.do
        """
        url = "https://ehall.gdut.edu.cn/gsapp/sys/wdcjapp/modules/wdcj/xscjcx.do"
        # 获得考试成绩列表
        if not cookies:
            return None
        data = GudtUtil.requests_by_cookies(url=url, cookies=cookies)
        if not data:
            ret = {
                "code": 4000,
                "data": None,
                "msg": "true",
                "isLive": False
            }
            return ret
        return GudtUtil.exam_data_clear(data)

    @staticmethod
    def exam_data_clear(data):
        """
        成绩数据清洗
        :return:
        """
        if data is None:
            return None
        data = data["datas"]
        data = data["xscjcx"]
        # 每一门的数据
        data = data["rows"]
        temp_map = {}
        # 需要按照学期分类，使用map -list 进行保存
        # "KCLBDM": "04",
        # "KCLBMC": "公共选修课",
        # print(data)
        for i in data:
            temp_data = {
                "cType": "",  # 默认给空就好
                "cn": i["KCMC"],  # 名称
                "credit": i["XF"],  # 学分
                "gp": None,  # 无所谓gp
                "result": i["DYBFZCJ"],  # 成绩
                "term": i["XNXQDM"],  # 学期
                "type": i["KCLBMC"]  # 类型
            }
            if i["DYBFZCJ"] == "不及格" or float(i["DYBFZCJ"]) < 60:
                temp_data["gp"] = 0
            else:
                # 绩点计算
                temp_data["gp"] = (float(i["DYBFZCJ"]) - 50) / 10
            if temp_map.get(i["XNXQDM"]) is None:
                temp_map[i["XNXQDM"]] = [temp_data]
            else:
                temp_map[i["XNXQDM"]].append(temp_data)
        # 按照学期排序
        temp_map = dict(sorted(temp_map.items(), key=lambda x: x[0], reverse=True))

        ret = {
            "code": 4000,
            "data": temp_map,
            "msg": "true",
            "isLive": True
        }
        return ret

    @staticmethod
    def get_campus(cookies, term):
        """
        获取校区信息
        :param cookies:
        :param 学期 20222
        :return:
        """
        url = "http://ehall.gdut.edu.cn/gsapp/sys/wdkbapp/modules/xskcb/xsskjccx.do"
        if not cookies:
            return None
        term = {
            "XNXQDM": term
        }
        data = GudtUtil.requests_by_cookies(url=url, postData=term, cookies=cookies, is_urlform_urlencoded=True)
        if data:
            try:
                data = data["datas"]
                data = data["xsskjccx"]
                data = data["rows"]
                campus = data[0]
                campus = campus["JCFAMC"]
                # 第一节课上课的校区
                campus = str(campus).replace("节次方案", "")
                return campus
            except Exception as e:
                print("校区获取异常：")
                print(e)
                return None
        return None

    @staticmethod
    def login_after_info(cookies):
        """
        登录后需要获取的信息
        :param cookies:
        :return:
        """
        ret = GudtUtil.get_user_info_by_cookies(cookies)
        if ret["isLive"]:
            user_info = ret["data"]
            # 获取学期信息
            term_info = GudtUtil.get_semester_message_by_cookies(cookies)
            # 获取校区
            # campus = GudtUtil.get_campus(cookies, term_info)
            data = {
                "userInfo": user_info,
                "semester": term_info,
                "campus": "大学城校区"
            }
            ret["data"] = data
            return ret
        else:
            return ret

    @staticmethod
    def check_need_Captcha(username):
        """
        检查是否需要验证码
        :param username:
        :return:
        """
        url = "https://authserver.gdut.edu.cn/authserver/checkNeedCaptcha.htl"
        data = {
            "username": username
        }

        # 通过用户名获取是否需要验证码
        ret = GudtUtil.requests_by_cookies(cookies=None, url=url, postData=data)
        ret["code"] = 4000
        return ret
