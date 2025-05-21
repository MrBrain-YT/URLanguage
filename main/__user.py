"""  module for get commands from Robot and Tools class for the user.

The tokenizer class is used to automatically send a token to the system class after registration.

"""

import requests

import __tools
import __robot
import __bases
from data_types import RobotData

external_token = ""
class tokenizer():

    def __init__(self, token) -> None:
        self.__token = token

    def set_token(self) -> None:
        global external_token
        external_token = self.__token
    
# United robotics system 
class system(__robot.Robot, __tools.Tools, __bases.Bases):
    
    def __init__(self, host:str, port:int, *token:str) -> None:
        self._token = token[0] if external_token == "" else external_token
        self._port = port
        self._host = host
        super().__init__(self._host, self._port, self._token)
        
    def set_emergency(self, robot_data:RobotData, state:bool) -> dict:
        url = f"https://{self._host}:{self._port}/set-emergency"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "state": str(state),
            "code" : robot_data.code
            }
        resp = requests.post(url, verify=True, json=data).json()
        return resp
        

    