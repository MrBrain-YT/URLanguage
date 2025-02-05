"""  module for additional commands for the administrator.

The system class has a kwargs argument "token" so that a user
authorized by the SuperAdmin role can send commands belonging to the Admin role.
The tokenizer class is used to automatically send a token to the system class after registration.

"""

import shutil
import json

import requests

import __user
import roles
from data_types import RobotData

external_token = ""
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
        self._token = token[0] if external_token == "" else external_token
        super().__init__(self._host, self._port, self._token)

    def add_kinematics(self, robot_data:RobotData, path:str, file_name:str) -> dict:
        url = f"https://{self._host}:{self._port}/AddKinematics"
        shutil.make_archive(file_name, 'zip', path)
        file = {"file" : open(f"./{file_name}.zip", 'rb')}
        data = {
            "Robot": robot_data.name,
            "token": self.token
            }
        resp = requests.post(url, files=file, json=data).text
        return json.loads(resp)
    
    def bind_kinematics(self, robot_data:RobotData, folder_name:str) -> dict:
        url = f"https://{self._host}:{self._port}/BindKinematics"
        data = {
            "Robot": robot_data.name,
            "Kinematics": folder_name,
            "token": self.token
            }
        resp = requests.post(url, verify=True, json=data).text
        return json.loads(resp)

    def add_tool(self, id:str) -> dict:
        url = f"https://{self._host}:{self._port}/URTC"
        data = {
            "Id": id,
            "token": self._token
        }
        resp = requests.post(url, verify=True, json=data).text
        return json.loads(resp)
    
    def add_robot(self, robot_data:RobotData, angle_count:int, kinematics:str="None") -> dict:
        responces = {}
        # Add robot
        url = f"https://{self._host}:{self._port}/CreateRobot"
        data = {
            "Robot": robot_data.name,
            "Angle": angle_count,
            "Kinematics": kinematics,
            "Code": robot_data.code,
            "token": self._token
            }
        resp = requests.post(url, verify=True, json=data).text
        responces["CreateRobot"] = json.loads(resp)
        # Add account for so that the robot itself sends some system commands
        url = f"https://{self._host}:{self._port}/CreateAccount"
        data = {
            "name": robot_data.name,
            "password": "robot",
            "User_role": "robot",
            "token": self._token
            }
        resp = requests.post(url, verify=True, json=data).text
        responces["CreateAccount"] = json.loads(resp)
        return responces
    
    def set_robot_home(self, robot_data:RobotData, angles:list) -> dict:
        url = f"https://{self._host}:{self._port}/HomePosition"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code" : robot_data.code
            }
        for i in range(1, len(angles)+1):
            data[f"J{i}"] = angles[i-1]
        resp = requests.post(url, verify=True, json=data).text
        return json.loads(resp)

    def delete_tool(self, id) -> dict:
        url = f"https://{self._host}:{self._port}/URTD"
        data = {
            "id": id,
            "token": self._token
            }
        resp = requests.post(url, verify=True, json=data).text
        return json.loads(resp)

    def delete_robot(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{self._port}/DelRobot"
        data = {
            "Robot": robot_data.name,
            "token": self._token
            }
        resp = requests.post(url, verify=True, json=data).text
        return json.loads(resp)

    def add_user(self, name:str, password:str) -> dict:
        if password != "robot":
            url = f"https://{self._host}:{self._port}/CreateAccount"
            data = {
                "name": name,
                "password": password,
                "User_role": roles.Roles.user,
                "token": self._token
                }
            resp = requests.post(url, verify=True, json=data).text
            return json.loads(resp)
        else:
            raise TypeError("The word robot cannot be used in the password because it is reserved")
    
    def get_robots(self) -> dict:
        url = f"https://{self._host}:{self._port}/GetRobots"
        data = {
            "token": self._token
            }
        resp = requests.post(url, verify=True, json=data).text
        return json.loads(resp)

    def get_robot(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{self._port}/GetRobot"
        data = {
            "Robot": robot_data.name,
            "token": self._token
            }
        resp = requests.post(url, verify=True, json=data).text
        return json.loads(resp)
    
    def add_log(self, robot_data:RobotData, type:str, text:str) -> bool:
        url = f"https://{self._host}:{str(self._port)}/URLogs"
        data = {
            "Robot": robot_data.name,
            "Type": type,
            "Text": text,
            "token": self._token
            }
        return json.loads(requests.post(url, verify=True, json=data).text)["status"]
    