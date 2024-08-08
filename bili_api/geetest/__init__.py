
from bili_ticket_gt_python import ClickPy
from bili_api.Response import Request


def geetest():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'http://space.bilibili.com'
    }
    response = Request().Response(url="https://passport.bilibili.com/x/passport-login/captcha?source=main_web",
                                headers=headers, method='get')
    gt = response["data"]["geetest"]["gt"]
    token = response["data"]["token"]
    challenge = response["data"]["geetest"]["challenge"]
    validate = geetest_code(challenge, gt)
    seccode = validate + '|jordan'
    return token, challenge, validate, seccode


def geetest_code(challenge: str, gt: str) -> str:
    """
        极验自动验证
        https://github.com/Amorter/biliTicker_gt
    :param challenge:
    :param gt:
    :return: str
    """
    cp = ClickPy()
    try:
        validate = cp.simple_match_retry(gt=gt, challenge=challenge)
        return validate
    except Exception as e:
        print(f"识别失败 {e}")
