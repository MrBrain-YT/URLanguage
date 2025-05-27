from typing import Any

import requests

from data_types import RobotData
from utils.config import Config

class Tools():
    # tool creation is located in the admin console
    def __init__(self, host:str, port:str, token:str) -> None:
        self._host = host
        self._port = port
        self._token = token
        self.config = Config()

    def get_tool_info(self, tool_id:str) -> dict:
        url = f"https://{self._host}:{self._port}/get-tool"
        data = {
            "id": tool_id,
            "token": self._token
            }
        verify = self.config.verify
        return requests.post(url, verify=verify, json=data).json()
    
    def set_tool_info(self, tool_id:str, config:Any) -> dict:
        url = f"https://{self._host}:{self._port}/set-tool"
        data = {
            "id": tool_id,
            "config": config,
            "token": self._token
            }
        verify = self.config.verify
        return requests.post(url, verify=verify, json=data).json()
    
    def set_robot_tool(self, robot_data:RobotData, tool_id:str) -> dict:
        url = f"https://{self._host}:{self._port}/set-robot-tool"
        data = {
            "robot": robot_data.name,
            "code": robot_data.code,
            "id": tool_id,
            "token": self._token
            }
        verify = self.config.verify
        return requests.post(url, verify=verify, json=data).json()
