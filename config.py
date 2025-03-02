class BaiduClass:
    appid = 20200810000542873
    secret = "VQQAAVJAECev1upFy"


class AIClass:
    endpoint = 'https://api.deepseek.com/'
    api_key = 'sk-69f7b6648922advadwfwf3b7c'
    model = 'deepseek-chat'
    temperature = 1


class SERPClass:
    api_key = "0oejfoejgeajoiegjeojg2j4i2o7e611de5ad5432145b458dd1492"
    engine = "google"
    q = ""
    location = "Shanghai, Shanghai, China"
    google_domain = "google.com"
    gl = "cn"
    hl = "zh-cn"
    safe = "off"
    nfpr = "1"

    def to_dict(self):
        # 获取类的所有成员变量，过滤掉方法和特殊变量
        return {key: value for key, value in SERPClass.__dict__.items()
                if not key.startswith('__') and not callable(value)}


class ConfigClass:
    baidu = BaiduClass()
    ai = AIClass()
    serp = SERPClass()


config = ConfigClass()
