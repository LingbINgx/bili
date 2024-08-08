from bili_api.Response import Request

"""
    获取用户信息
    文档 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/user/info.md 
"""


class user_information:

    def __init__(self, net: Request):
        """
        用户信息初始化
        : net: Request连接
        """
        self.net = net

    def user_card_info(self,
                       mid: int,
                       photo: bool = True) \
            -> dict:
        """
        获取uid为mid的账号个人信息（不需要cookie）
        : mid: 查询账号的uid
        : photo: 是否需要头像图片
        :return: dict
        """
        if not (isinstance(mid, int) and mid > 0):
            raise ValueError("The input must be a positive integer.")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'http://space.bilibili.com',
            'Host': 'api.bilibili.com'
        }
        params = {
            'mid': mid,
            'photo': photo
        }
        return self.net.Response(url="https://api.bilibili.com/x/web-interface/card",
                                 headers=headers,
                                 params=params,
                                 method="get")

    def login_user_detail_info(self, cookie: dict) \
            -> dict:
        """
        获取已登录账号的详细个人信息（须要cookie）
        : cookie: cookie
        :return: dict
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'http://space.bilibili.com',
            'Cookie': 'SESSDATA=' + cookie["SESSDATA"],
            'Host': 'api.bilibili.com'
        }
        return self.net.Response(url="https://api.bilibili.com/x/space/myinfo",
                                 headers=headers,
                                 method="get")

    def multi_user_info(self, uids: list) \
            -> dict:
        """
        可以同时获取较多的用户信息
        （据测试可以一次性获取 2000 多个用户的信息；若获取更多用户信息可能会返回 -504 服务调用超时）
        : uids: 目标用户的mid列表(列表或字符串（用','分割）)
        :return: dict
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'http://space.bilibili.com',
            'Host': 'api.bilibili.com'
        }
        params = {'uids': ",".join(str(x) for x in uids) if type(uids) is list else uids}
        return self.net.Response(url="https://api.bilibili.com/x/polymer/pc-electron/v1/user/cards",
                                 headers=headers,
                                 params=params,
                                 method="get")

    def multi_user_info_2(self, uids: list) \
            -> dict:
        """
        本接口较其他接口相比，只会返回非常有限的信息
        : uids: 目标用户的mid列表(列表或字符串（用','分割）)
        :return: dict
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'http://space.bilibili.com',
        }
        params = {'uids': ",".join(str(x) for x in uids) if type(uids) is list else uids}
        return self.net.Response(url="https://api.vc.bilibili.com/account/v1/user/cards",
                                 headers=headers,
                                 params=params,
                                 method="get")

    def user_info_details(self,
                          mid: int,
                          cookie: dict,
                          ) \
            -> dict:
        """
        获取用户的详细信息
        : mid: uid号
        : cookie: cookie
        :return: dict
        """
        if not (isinstance(mid, int) and mid > 0):
            raise ValueError("The input must be a positive integer.")
        from bili_api import get_Wbi
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'http://space.bilibili.com',
            'Cookie': 'SESSDATA=' + cookie["SESSDATA"],
            'Host': 'api.bilibili.com'
        }
        img_key, sub_key = get_Wbi.getWbiKeys()
        params = get_Wbi.encWbi(
            params={'mid': mid},
            img_key=img_key,
            sub_key=sub_key
        )

        return self.net.Response(url="https://api.bilibili.com/x/space/wbi/acc/info",
                                 headers=headers,
                                 params=params,
                                 method="get")
