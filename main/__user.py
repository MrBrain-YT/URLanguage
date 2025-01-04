"""  module for get commands from Robot and Tools class for the user.

The tokenizer class is used to automatically send a token to the system class after registration.

"""
import json

import requests

import __tools
import __robot
from data_types import RobotData

external_token = ""
class tokenizer():

    def __init__(self, token) -> None:
        self.__token = token

    def set_token(self) -> None:
        global external_token
        external_token = self.__token
    
# United robotics system 
class system(__robot.Robot, __tools.Tools):
    
    def __init__(self, host:str, port:int, *token:str) -> None:
        self.__token = token if external_token == "" else external_token
        self.__port = port
        self.__host = host
        super().__init__(self.__host, self.__port, self.__token)
        
    def set_emergency(self, robot_data:RobotData, state:bool) -> str:
        url = f"https://{self.__host}:{self.__port}/Emergency"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "State": str(state),
            "Code" : robot_data.code
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp
        

    