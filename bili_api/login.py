import json
import os
from time import sleep
from loguru import logger

from bili_api.Exception import LoginException, _412Exception
from bili_api.Response import Request

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Referer': 'https://passport.bilibili.com'
}


def path():
    current_dir = os.getcwd()
    return os.path.join(current_dir, "../log/" if str.endswith(current_dir, "bili_api") else "./log/")


def getCookie(res: dict) -> dict:
    url = res["data"]["url"]
    url.rsplit('&')
    key_value = url.split('?')[1].split('&')
    key_value_pairs = [pair.split('=') for pair in key_value]
    dist = {}
    for i in key_value_pairs:
        dist[i[0]] = i[1]
    dist["refresh_token"] = res["data"]["refresh_token"]
    return dist


def saveCookie(response: dict):
    new_path = path()
    try:
        with open(new_path + "cookie.json", 'w', encoding='utf-8') as write_f:
            json.dump(getCookie(response), write_f, indent=4, ensure_ascii=False)
            logger.success(f"cookie已保存至{new_path}cookie.json中")
    except Exception:
        raise Exception("文件写入错误")


def passwordRSA(password: str, key: str):
    from Crypto.Cipher import PKCS1_v1_5
    from Crypto.PublicKey import RSA
    import base64
    new_password = bytes(password, encoding="utf8")
    rsakey = RSA.import_key(key)
    cipher = PKCS1_v1_5.new(rsakey)
    cipher_text = cipher.encrypt(new_password)
    return base64.b64encode(cipher_text).decode("utf-8")


def showQRcode(url):
    from PIL import Image
    import qrcode
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.print_ascii(invert=True)
    qr.make(fit=True)
    qr.make_image(fill='black', back_color='white').save('./code.png')
    image = Image.open('./code.png')
    image.show()
    os.remove('./code.png')


class login:
    def __init__(self, net: Request):
        """
        登录初始化
        : net: Request连接
        """
        self.net = net

    def applyQRcode(self):
        response = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/qrcode/generate",
                                     headers=headers,
                                     method="get")
        qrcode_key = response["data"]["qrcode_key"]
        qrcode_url = response["data"]["url"]

        return qrcode_key, qrcode_url
    
    @logger.catch
    def login_QRcode(self):
        qrcode_key, qrcode_url = self.applyQRcode()
        params = {
            'qrcode_key': qrcode_key
        }
        showQRcode(qrcode_url)
        logger.info("请扫描二维码登录，若未弹出二维码，请到根目录打开code.png文件 ")
        sleep(3)
        while True:
            response = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/qrcode/poll",
                                         headers=headers,
                                         params=params,
                                         method="get"
                                         )
            if response["code"] == 0:
                match response["data"]["code"]:
                    case 0:
                        # 0：扫码登录成功
                        logger.success(f"登录成功 'code': {response["data"]["code"]}, 'message': {response["data"]["message"]}")
                        saveCookie(response)
                        return True
                    case 86038:
                        # 86038：二维码已失效
                        logger.error(f"'code': {response["data"]["code"]}, 'message': {response["data"]["message"]}")
                        raise TimeoutError("The QR code has expired")
                    case _:
                        # 86090：二维码已扫码未确认 86101：未扫码
                        logger.info(f"'code': {response["data"]["code"]}, 'message': {response["data"]["message"]}")
            elif response["code"] == -412:
                logger.error("IP 被B站封禁(412), 请尝试更换IP后继续使用")
                raise _412Exception("IP 被B站封禁(412), 请尝试更换IP后继续使用")
            elif response["code"] != 0:
                raise LoginException(f"登录失败 'code': {response["code"]}, 'message': {response["message"]}")
            sleep(2.5)

    def hash_key(self) -> tuple[str, str]:
        response = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/key",
                                     headers=headers,
                                     method="get")
        hash = response["data"]["hash"]
        key = response["data"]["key"]
        return hash, key

    @logger.catch
    def login_password(self, username: str, password: str):
        """
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/login/login_action/password.md
        : username: 用户名
        : password: 密码
        :return: bool
        """
        from bili_api.geetest import geetest
        hash, key = self.hash_key()
        token, challenge, validate, seccode = geetest()
        params = {
            "username": username,
            "password": passwordRSA(hash + password, key),
            "keep": "0",
            "token": token,
            "challenge": challenge,
            "validate": validate,
            "seccode": seccode,
            "source": 'main_web'
        }
        response = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/login",
                                     headers=headers,
                                     params=params,
                                     method="post")
        if response["code"] == -412:
            logger.error("IP 被B站封禁(412), 请尝试更换IP后继续使用" +
                         f"登录失败 'code': {response["code"]}, 'message': {response["message"]}")
            raise _412Exception("IP 被B站封禁(412), 请尝试更换IP后继续使用")
        elif response["code"] != 0:
            raise LoginException(f"登录失败 'code': {response["code"]}, 'message': {response["message"]}")
        if response["data"]["status"] == 0:
            logger.success(f"登录成功 'code': {response["data"]["status"]}, 'message': {response["data"]["message"]}")
            saveCookie(response)
            return True
        else:
            import re
            from bili_api.geetest import geetest_code

            logger.warning("登录失败, 需要二次验证")
            data_url = response["data"]["url"]
            tmp_token_match = re.search(r"tmp_token=(\w{32})", data_url)
            tmp_token = tmp_token_match.group(1) if tmp_token_match else ""
            scene_match = re.search(r"scene=([^&]+)", data_url)
            scene = scene_match.group(1) if scene_match else "loginTelCheck"

            info = self.net.Response(url=f"https://passport.bilibili.com/x/safecenter/user/info?tmp_code={tmp_token}",
                                     headers=headers,
                                     method="get")
            logger.info(f"手机号已绑定, 即将给 {info["data"]["account_info"]["hide_tel"]} 发送验证码")
            pre = self.net.Response(url="https://passport.bilibili.com/x/safecenter/captcha/pre",
                                    headers=headers,
                                    method="post")
            token = pre["data"]["recaptcha_token"]
            challenge = pre["data"]["gee_challenge"]
            validate = geetest_code(challenge=challenge, gt=pre["data"]["gee_gt"])
            seccode = validate + '|jordan'
            resend_params = {
                "tmp_code": tmp_token,
                "sms_type": scene,
                "recaptcha_token": token,
                "gee_challenge": challenge,
                "gee_validate": validate,
                "gee_seccode": seccode,
            }
            resend = self.net.Response(
                url="https://passport.bilibili.com/x/safecenter/common/sms/send",
                params=resend_params,
                headers=headers,
                method="post"
            )
            if resend["code"] != 0:
                raise LoginException(f"验证码发送失败 code: {resend['code']}, message: {resend['message']}")
            logger.success("验证码发送成功")
            resend_token = resend["data"]["captcha_key"]
            code = input("请输入验证码: ")
            if response["data"]["status"] == 1:
                data = {
                    "verify_type": "sms",
                    "tmp_code": tmp_token,
                    "captcha_key": resend_token,
                    "code": code
                }
                url = "https://passport.bilibili.com/x/safecenter/sec/verify"
            elif response["data"]["status"] == 2:
                data = {
                    "type": "loginTelCheck",
                    "tmp_code": tmp_token,
                    "captcha_key": resend_token,
                    "code": code
                }
                url = "https://passport.bilibili.com/x/safecenter/login/tel/verify"
            else:
                raise Exception("未知错误")
            login_res = self.net.Response(url=url, headers=headers, params=data, method="post")
            if login_res["code"] != 0:
                raise LoginException(f"验证码登录失败 {login_res['code']}: {login_res['message']}")
            logger.success("验证码登录成功")
            saveCookie(self.net.Response(
                url="https://passport.bilibili.com/x/passport-login/web/exchange_cookie",
                params={"source": "risk", "code": login_res["data"]["code"]},
                headers=headers,
                method="post",
            ))
            return True

    def buvid(self) -> tuple[str, str]:
        buvid3_resp = self.net.Response(url="https://api.bilibili.com/x/frontend/finger/spi",
                                        headers=headers,
                                        method="get")
        buvid3 = buvid3_resp["data"]["b_3"]
        buvid4 = buvid3_resp["data"]["b_4"]
        return buvid3, buvid4

    def getSMS(self, tel: str) -> str:
        buvid3, _ = self.buvid()
        from bili_api.geetest import geetest
        token, challenge, validate, seccode = geetest()
        params = {
            "cid": "86",
            "tel": tel,
            "source": "main_web",
            "token": token,
            "challenge": challenge,
            "validate": validate,
            "seccode": seccode
        }
        resp = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/sms/send",
                                 params=params,
                                 headers={**headers, "Cookie": "buvid3=" + buvid3},
                                 method="post")
        if resp["code"] != 0:
            raise LoginException(f"验证码发送失败 'code': {resp["code"]}, 'message': {resp["message"]}")
        logger.success(f"验证码发送成功 'code': {resp["code"]}, 'message': {resp["message"]}")
        return resp["data"]["captcha_key"]

    @logger.catch
    def login_SMS(self, tel: str):
        captcha_key = self.getSMS(tel)
        code = input("请输入验证码: ")
        params = {
            "cid": "86",
            "tel": tel,
            "code": code,
            "source": "main_web",
            "captcha_key": captcha_key,
            "keep": "true"
        }
        resp = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/login/sms",
                                 headers=headers,
                                 params=params,
                                 method="post")
        if resp["code"] != 0:
            raise LoginException(f"登录失败 'code': {resp["code"]}, 'message': {resp["message"]}")
        logger.success(f"登录成功 'code': {resp["code"]}, 'message': {resp["message"]}")
        saveCookie(resp)


