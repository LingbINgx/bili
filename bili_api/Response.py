import httpx
from loguru import logger


class Request:

    def __init__(self,
                 proxy: str | None = None,
    ):
        #self.session = requests.session()
        self.session = httpx.Client()
        self.proxy = proxy

    def Response(self,
                 url: str,
                 headers: dict,
                 method: str,
                 params: dict = {},
                 ):
        """
        requests

        : url: url
        : data: data
        : method: 方法
        : headers: headers
        : params: params
        : return: dict json
        
        """
        methods = {
            "get": self.session.get,
            "post": self.session.post,
        }
        if method in methods:
            response = methods[method](url=url, 
                                       headers=headers, 
                                       **({"params": params} if method == "get" else {"data": params}))
        else:
            raise ValueError("methodError")
        try:
            response.raise_for_status()
        except httpx.RequestError as http_err:
            raise f"HTTP error occurred: {http_err}"
        except Exception as err:
            raise f"Other error occurred: {err}"
        else:
            if "json" in response.headers["Content-Type"]:
                #print('返回的是 JSON')
                return response.json()
            elif "text" in response.headers["Content-Type"]:
                #print('返回的是 HTML')
                return response.text
            else:
                #print('返回的内容类型未知')
                return None
        



    def cookies(self):
        #return self.session.cookies.get_dict()
        return dict(self.session.cookies)