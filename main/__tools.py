from typing import Any

import requests

class Tools():
    # tool creation is located in the admin console
    def __init__(self, host:str, port:str, token:str) -> None:
        self.host = host
        self.port = port
        self.token = token


    def get_tool_info(self, id:str) -> dict:
        url = f"https://{self.host}:{self.port}/GetTool"
        data = {
            "id": id,
            "type": "read",
            "token": self.token
            }
        return requests.post(url, verify=True, json=data).json()
    
    def set_tool_info(self, id:str, config:Any) -> dict:
        url = f"https://{self.host}:{self.port}/GetTool"
        data = {
            "id": id,
            "type": "write",
            "config": config,
            "token": self.token
            }
        return requests.post(url, verify=True, json=data).json()
