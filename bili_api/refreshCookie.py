import json
import os

from loguru import logger

from bili_api.Response import Request

path = "../log/cookie.json" if os.path.isfile("../log/cookie.json") else "./log/cookie.json"
try:
    with open(path, "r") as f:
        cookie = json.load(f)
except:
    cookie = {
        "SESSDATA": "",
        "bili_jct": "",
    }
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Cookie': f'SESSDATA={cookie["SESSDATA"]}'
}


def CorrespondPath(timestamp: str) -> str:
    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    import binascii

    pubkey = ("-----BEGIN PUBLIC KEY-----\n"
              "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg\n"
              "Uc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71\n"
              "nzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40\n"
              "JNrRuoEUXpabUzGB8QIDAQAB\n"
              "-----END PUBLIC KEY-----\n")
    key = RSA.importKey(pubkey)
    cipher = PKCS1_OAEP.new(key, SHA256)
    encrypted = cipher.encrypt(f'refresh_{timestamp}'.encode())
    return binascii.b2a_hex(encrypted).decode()


class refreshCookie:

    def __init__(self, 
                 net: Request, 
                 set: bool = False
    ):
        self.net = net
        self.set = set

    
    def isNeedRefresh(self) -> tuple[bool, str]:
        refresh = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/cookie/info",
                                    headers=headers,
                                    params={"csrf": cookie["bili_jct"]},
                                    method="get")
        if refresh["code"] != 0:
            # -101 账号未登录
            raise Exception(f"'code': {refresh["code"]}, 'message': {refresh["message"]}")
        logger.success(refresh)
        return refresh["data"]["refresh"], refresh["data"]["timestamp"]

    def getRefresh_csrf(self, correspondPath: str):
        from bs4 import BeautifulSoup
        csrf = self.net.Response(url=f"https://www.bilibili.com/correspond/1/{correspondPath}",
                            headers=headers,
                            method="get")
        soup = BeautifulSoup(csrf, 'html.parser')
        refresh_csrf = soup.find(id='1-name')
        return refresh_csrf.text

    #@logger.catch
    def refresh(self) -> bool:
        #try:
        refresh, timestamp = self.isNeedRefresh()
        #except:
            #raise Exception
        if not (refresh or self.set):
            logger.info("Cookie不需要刷新")
            return False
        else:
            correspondPath = CorrespondPath(timestamp)
            refresh_csrf = self.getRefresh_csrf(correspondPath)
            old_refresh_token = cookie["refresh_token"]
            params = {
                'csrf': cookie["bili_jct"],
                'refresh_csrf': refresh_csrf,
                'source': 'main_web',
                'refresh_token': old_refresh_token
            }
            refresh_resp = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/cookie/refresh",
                                             headers=headers,
                                             params=params,
                                             method="post")
            if refresh_resp["code"] != 0:
                raise Exception(f"'code': {refresh_resp["code"]}, 'message': {refresh_resp["message"]}")
            logger.success(refresh_resp)
            newcookie = {**self.net.cookies(), "refresh_token": refresh_resp["data"]["refresh_token"]}
            with open(path, 'w', encoding='utf-8') as write_f:
                json.dump(newcookie, write_f, indent=4, ensure_ascii=False)
                logger.success(f"新cookie已保存至{path}cookie.json中")
            data = {
                "csrf": newcookie["bili_jct"],
                "refresh_token": old_refresh_token
            }
            confirm = self.net.Response(url="https://passport.bilibili.com/x/passport-login/web/confirm/refresh",
                                        headers={**headers, "Cookie": f'SESSDATA={newcookie["SESSDATA"]}'},
                                        method="post",
                                        params=data)
            if confirm["code"] != 0:
                raise Exception(f"'code': {confirm["code"]}, 'message': {confirm["message"]}")
            logger.success("cookie已刷新，旧cookie已失效")
            return True

