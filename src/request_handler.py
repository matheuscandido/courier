import requests

class RequestHandler:
    def __init__(self, method: str, url: str, data: str, headers: dict) -> None:
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers
        self.headers["Content-type"] = "application/json"

    def send(self):
        if self.method == "GET":
            return requests.get(self.url, headers=self.headers)
        elif self.method == "POST":
            return requests.post(self.url, data=self.data, headers=self.headers)
        else:
            return None
