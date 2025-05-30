import requests

from data_types import RobotData

class Bases():
    # tool creation is located in the admin console
    def __init__(self, host:str, port:str, token:str) -> None:
        self._host = host
        self._port = port
        self._token = token
        
    def get_base(self, base_name:str) -> dict:
        url = f"https://{self._host}:{self._port}/get-base"
        data = {
            "id": base_name,
            "token": self._token
            }
        return requests.post(url, verify=True, json=data).json()["data"]
    
    def set_robot_base(self, robot_data:RobotData, tool_id:str) -> dict:
        url = f"https://{self._host}:{self._port}/set-robot-base"
        data = {
            "robot": robot_data.name,
            "code": robot_data.code,
            "id": tool_id,
            "token": self._token
            }
        return requests.post(url, verify=True, json=data).json()