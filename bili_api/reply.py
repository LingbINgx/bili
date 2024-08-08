import json
import os

from loguru import logger
from bili_api.Response import Request



class reply:

    def __init__(self, net: Request):
        self.net = net
        self._load_cookie()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
            'Cookie': f"SESSDATA={self.cookie["SESSDATA"]}"
            }
        
    def _load_cookie(self) -> dict:
        path = "../log/cookie.json" if os.path.isfile("../log/cookie.json") else "./log/cookie.json"
        try:
            with open(path, "r") as f:
                self.cookie = json.load(f)
        except:
            self.cookie = {
                "SESSDATA": "",
                "bili_jct": "",
            }

    def get_reply(self, type: int, aid: int):
        """
        获取评论区评论
        
        : type	num	评论区类型代码
        : oid	num	目标评论区 id
        """
        params = {
            'type': type,
            'oid': aid,
            'sort': 0,
            'nohot': 0,
            'ps': 20,
            'pn': 1
        }
        resp = self.net.Response(url="https://api.bilibili.com/x/v2/reply",
                                 headers=self.headers,
                                 params=params,
                                 method="get")
        if resp["code"] != 0:
            logger.error(f"获取评论区失败 'code': {resp["code"]}, 'message': {resp["message"]}")
            return False
        logger.success(f"获取评论区成功 'code': {resp["code"]}, 'message': {resp["message"]}")
        return True
    
    def get_reply_num(self, type: int, oid: int):
        """
        获取评论区评论总数
        
        : type	num	评论区类型代码
        : oid	num	目标评论区 id
        """
        params = {
            'type': type,
            'oid': oid
        }
        num = self.net.Response(url="https://api.bilibili.com/x/v2/reply/count",
                                headers=self.headers,
                                params=params,
                                method="get")
        print(num)
        return num["data"]["count"]

    def reply_add(self, 
                  type: int, 
                  aid: int,
                  message: str)\
        -> bool:
        """
        对目标项目发送评论
        
        : type: int 评论区类型代码
        : aid: int 视频avid
        : message: str 评论内容
        
        return bool
        """
        params = {
            'type': type,
            'oid': aid,
            'message': message,
            'plat': 1,
            'csrf': self.cookie["bili_jct"]
        }
        add_resp = self.net.Response(url="https://api.bilibili.com/x/v2/reply/add",
                                     method="post",
                                     params=params,
                                     headers=self.headers)
        if add_resp["code"] != 0:
            logger.error(f"评论发送失败 'code': {add_resp["code"]}, 'message': {add_resp["message"]}")
            return False
        logger.success(f"评论发送成功 'code': {add_resp["code"]}, 'message': {add_resp["message"]}")
        return True

    def reply_action(self, type: int, aid: int, rpid: int, action: int) -> bool:
        """"
        对目标评论进行点赞操作
        
        : type	int	评论区类型代码	
        : oid	    int	目标评论区id	
        : rpid	int	目标评论rpid
        : action	int	操作代码(0: 取消点赞; 1: 点赞)
        """
        params = {
            'type': type,
            'oid': aid,
            'rpid': rpid,
            'action': action,
            'csrf': self.cookie["bili_jct"]
        }
        action_res = self.net.Response(url="https://api.bilibili.com/x/v2/reply/action",
                                       method="post",
                                       params=params,
                                       headers=self.headers)
        match action:
            case 1:
                if action_res["code"] != 0:
                    logger.error(f"点赞失败 'code': {action_res["code"]}, 'message': {action_res["message"]}")
                    return False
                else:
                    logger.success(f"点赞成功 'code': {action_res["code"]}, 'message': {action_res["message"]}")
                    return True
            case 0:
                if action_res["code"] != 0:
                    logger.error(f"取消点赞失败 'code': {action_res["code"]}, 'message': {action_res["message"]}")
                    return False
                else:
                    logger.success(f"取消点赞成功 'code': {action_res["code"]}, 'message': {action_res["message"]}")
                    return True
        
    def reply_hate(self, type: int, aid: int, rpid: int, action: int):
        """"
        对目标评论进行点踩操作
        
        : type	int	评论区类型代码	
        : oid	    int	目标评论区id	
        : rpid	int	目标评论rpid
        : action	int	操作代码(0: 取消点踩; 1: 点踩)
        """
        params = {
            'type': type,
            'oid': aid,
            'rpid': rpid,
            'action': action,
            'csrf': self.cookie["bili_jct"]
        }
        hate = self.net.Response(url="https://api.bilibili.com/x/v2/reply/hate",
                                 method="post",
                                 params=params,
                                 headers=self.headers)
        match action:
            case 1:
                if hate["code"] != 0:
                    logger.error(f"点踩失败 'code': {hate["code"]}, 'message': {hate["message"]}")
                    return False
                else:
                    logger.success(f"点踩成功 'code': {hate["code"]}, 'message': {hate["message"]}")
                    return True
            case 0:
                if hate["code"] != 0:
                    logger.error(f"取消点踩失败 'code': {hate["code"]}, 'message': {hate["message"]}")
                    return False
                else:
                    logger.success(f"取消点踩成功 'code': {hate["code"]}, 'message': {hate["message"]}")
                    return True


