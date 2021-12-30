import requests

class RequestHandler:
    def __init__(self, method: str, url: str, data: str, headers: dict) -> None:
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers

    def send(self):
        s = Session()
        req = Request(self.method, self.url, self.data, self.headers)
        prepped = req.prepare()

        return s.send(prepped)
