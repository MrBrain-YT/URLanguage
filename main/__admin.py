"""  module for additional commands for the administrator.

The system class has a kwargs argument "token" so that a user
authorized by the SuperAdmin role can send commands belonging to the Admin role.
The tokenizer class is used to automatically send a token to the system class after registration.

"""

import shutil

import requests

import __user
from data_types import RobotData
from data_types import StaticData
from utils.config import Config

external_token = None
class tokenizer():

    def __init__(self, token) -> None:
        self.token = token

    def set_token(self) -> None:
        global external_token
        external_token = self.token

# United robotics system 
class system(__user.system):
    
    def __init__(self, host:str, port:int, *token:str) -> None:
        self._host = host
        self._port = port
        self._token = token[0] if external_token == None else external_token
        super().__init__(self._host, self._port, self._token)
        self.config = Config()

    def add_kinematics(self, path:str, file_name:str) -> dict:
        url = f"https://{self._host}:{self._port}/api/add-kinematic"
        shutil.make_archive(file_name, 'zip', path)
        file = {"file" : open(f"./{file_name}.zip", 'rb')}
        data = {
            "token": self.token
            }
        verify = self.config.verify
        resp = requests.post(url, files=file, verify=verify, json=data).json()
        return resp
    
    def bind_kinematics(self, robot_data:RobotData, folder_name:str) -> dict:
        url = f"https://{self._host}:{self._port}/api/bind-kinematic"
        data = {
            "robot": robot_data.name,
            "id": folder_name,
            "token": self.token
            }
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp

    def add_tool(self, id:str) -> dict:
        url = f"https://{self._host}:{self._port}/api/create-tool"
        data = {
            "id": id,
            "token": self._token
        }
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp
    
    def add_robot(self, robot_data:RobotData, password:str, angle_count:int, kinematics:str="None") -> dict:
        # Add robot
        url = f"https://{self._host}:{self._port}/api/create-robot"
        data = {
            "robot": robot_data.name,
            "angle": angle_count,
            "id": kinematics,
            "code": robot_data.code,
            "password": password,
            "token": self._token
            }
        verify = self.config.verify
        responce = requests.post(url, verify=verify, json=data).json()
        return responce
    
    def set_robot_home(self, robot_data:RobotData, angles:list) -> dict:
        url = f"https://{self._host}:{self._port}/api/set-home-position"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code" : robot_data.code
            }
        for i in range(1, len(angles)+1):
            data[f"J{i}"] = angles[i-1]
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp

    def delete_tool(self, id) -> dict:
        url = f"https://{self._host}:{self._port}/api/delete-tool"
        data = {
            "id": id,
            "token": self._token
            }
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp

    def delete_robot(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{self._port}/api/delete-robot"
        data = {
            "robot": robot_data.name,
            "token": self._token
            }
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp

    def add_user(self, name:str, password:str) -> dict:
        if password != "robot":
            url = f"https://{self._host}:{self._port}/api/create-account"
            data = {
                "name": name,
                "password": password,
                "user_role": StaticData.Roles.USER,
                "token": self._token
                }
            verify = self.config.verify
            resp = requests.post(url, verify=verify, json=data).json()
            return resp
        else:
            raise TypeError("The word robot cannot be used in the password because it is reserved")
    
    def get_robots(self) -> dict:
        url = f"https://{self._host}:{self._port}/api/get-robots"
        data = {
            "token": self._token
            }
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp

    def get_robot(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{self._port}/api/get-robot"
        data = {
            "robot": robot_data.name,
            "token": self._token
            }
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp
    
    def get_system_log(self, timestamp:int=None) -> dict:
        url = f"https://{self._host}:{self._port}/api/get-system-logs"
        data = {
            "token": self._token
            }
        if timestamp is not None:
            data["timestamp"] = timestamp
        verify = self.config.verify
        resp = requests.post(url, verify=verify, json=data).json()
        return resp
    
    # Reanamed to "debug" -> __robot.py
    # def add_log(self, robot_data:RobotData, type:str, text:str) -> bool:
    #     url = f"https://{self._host}:{str(self._port)}/AddRobotLog"
    #     data = {
    #         "robot": robot_data.name,
    #         "Type": type,
    #         "Text": text,
    #         "token": self._token
    #         }
    #     return requests.post(url, verify=verify, json=data).json()["status"]
    
    def set_calibrated_data(self, tool_id:str, data:dict) -> dict:
        url = f"https://{self._host}:{self._port}/api/set-tool-calibration"
        data = {
            "id": tool_id,
            "calibration_data": data,
            "token": self._token
            }
        verify = self.config.verify
        return requests.post(url, verify=verify, json=data).json()
    
    def create_base(self, base_name:str) -> dict:
        url = f"https://{self._host}:{self._port}/api/create-base"
        data = {
            "id": base_name,
            "token": self._token
            }
        verify = self.config.verify
        return requests.post(url, verify=verify, json=data).json()
    
    def get_bases(self) -> dict:
        url = f"https://{self._host}:{self._port}/api/get-bases"
        data = {
            "token": self._token
            }
        return requests.post(url, verify=verify, json=data).json()["data"]
    
    def set_base_data(self, base_name:str, base_data:dict) -> dict:
        url = f"https://{self._host}:{self._port}/api/set-base"
        data = {
            "id": base_name,
            "data": base_data,
            "token": self._token
            }
        verify = self.config.verify
        return requests.post(url, verify=verify, json=data).json()
    
    def delete_base(self, base_name:str) -> dict:
        url = f"https://{self._host}:{self._port}/api/delete-base"
        data = {
            "id": base_name,
            "token": self._token
            }
        verify = self.config.verify
        return requests.post(url, verify=verify, json=data).json()