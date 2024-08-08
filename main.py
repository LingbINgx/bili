from bili_api.login import login
from bili_api.refreshCookie import refreshCookie
from bili_api.Response import Request

class Init:
    def __init__(self, net: Request) -> None:
        self.net = net
        self.login()

    def login(self):
        def loginFun():
            print("请登录bilibili")
            print("登录方式：\n"
                "1: 二维码登录\n"
                "2: 账号密码登录\n"
                "3: 短信验证码登录")
            mod = int(input("请输入"))
            match mod:
                case 1:
                    login(self.net).login_QRcode()
                case 2:
                    username = input("请输入账号: \n")
                    password = input("请输入密码: \n")
                    login(self.net).login_password(username, password)
                case 3:
                    tel = input("请输入手机号: \n")
                    login(self.net).login_SMS(tel)
        try:
            refreshCookie(self.net, True).refresh()
        except:
            loginFun()
        else:
            print("Cookie导入成功! ")


    

net = Request()
Init(net).login()
