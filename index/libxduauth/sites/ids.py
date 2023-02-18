import time
from io import BytesIO
from bs4 import BeautifulSoup
from ..AuthSession import AuthSession
from ..utils.page import parse_form_hidden_inputs
from ..utils.vcode import _process_vcode
from ..utils.aes import encrypt


class CaptchaException(Exception):
    """
    验证码异常
    """
    pass


class AccountError(Exception):
    """
    密码错误异常
    """


class IDSSession(AuthSession):
    cookie_name = 'ids'

    def __init__(
            self, target, username, password,
            *args, **kwargs
    ):
        super().__init__(f'{self.cookie_name}_{username}')
        # if self.is_logged_in():
        #     return
        # else:
        self.cookies.clear()
        page = self.get(
            'https://authserver.gdut.edu.cn/authserver/login',
            params={'service': target, 'type': 'userNameLogin'}
        ).text
        is_need_captcha, vcode = self.get(
            'https://authserver.gdut.edu.cn/authserver/checkNeedCaptcha.htl',
            params={'username': username, '_': int(time.time() * 1000)}
        ).json()['isNeed'], None
        if is_need_captcha:
            raise CaptchaException()
        page = BeautifulSoup(page, 'html.parser')
        form = page.findChild(attrs={'id': 'pwdFromId'})
        params = parse_form_hidden_inputs(form)
        # 找到所有的隐藏提交input
        enc = form.find('input', id='pwdEncryptSalt').get('value')

        ret = self.post(
            'https://authserver.gdut.edu.cn/authserver/login',
            params={'service': target},
            data=dict(params, **{
                'username': username,
                'password': encrypt(password.encode(), enc.encode()),
                'captcha': vcode,
                'rememberMe': 'true'
            })
        )
        # 重新回到了需要登录的首页，说明登录失败，密码问题，或者其他问题
        if str(ret.status_code) == "200":
            return
        if str(ret.status_code) == "401":
            raise AccountError()
        raise Exception("ids未知异常！")

    def is_logged_in(self):
        return self.get(
            'https://authserver.gdut.edu.cn/authserver/index.do',
            allow_redirects=False
        ).status_code != 302
