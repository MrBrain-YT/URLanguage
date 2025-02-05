import json

import requests

class Tools():
    # tool creation is located in the admin console
    def __init__(self, host:str, port:str, token:str) -> None:
        self.host = host
        self.port = port
        self.token = token


    def get_tool_info(self, name:str) -> dict:
        url = f"https://{self.host}:{self.port}/URTool"
        data = {
            "id": name,
            "type": "",
            "token": self.token
            }
        return json.loads(requests.post(url, verify=True, json=data).text)
    
    def set_tool_info(self, name:str, config:str) -> dict:
        url = f"https://{self.host}:{self.port}/URTool"
        data = {
            "id": name,
            "type": "write",
            "config": config,
            "token": self.token
            }
        return json.loads(requests.post(url, verify=True, json=data).text)
