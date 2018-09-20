import requests

class Smmry(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = "http://api.smmry.com/"
        self.headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

    def smmry_text(self, text):
        r = requests.post("{ep}&SM_API_KEY={key}".format(ep=self.endpoint, key=self.api_key),
                          headers=self.headers,
                          data={"sm_api_input": text})
        return r.json()

    def smmry_url(self, url, **kwargs):

        params = {"SM_API_KEY": self.api_key}
        if kwargs:
            params.update(kwargs)
        params["SM_URL"] = url

        r = requests.get(self.endpoint,
                         headers=self.headers,
                         params=params)
        return r.json()

# if __name__ == '__main__':
#     s = Smmry(api_key="D39BB38989")
