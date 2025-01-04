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
        self.__host = host
        self.__port = port
        self.__token = token if external_token == "" else external_token
        super().__init__(self.__host, self.__port, self.__token)

    def add_kinematics(self, robot_data:RobotData, path:str, file_name:str) -> str:
        url = f"https://{self.__host}:{self.__port}/AddKinematics"
        shutil.make_archive(file_name, 'zip', path)
        file = {"file" : open(f"./{file_name}.zip", 'rb')}
        print(file)
        data = {
            "Robot": robot_data.name,
            "token": self.token
            }
        response = requests.post(url, files=file, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return response
    
    def bind_kinematics(self, robot_data:RobotData, folder_name:str) -> str:
        url = f"https://{self.__host}:{self.__port}/BindKinematics"
        data = {
            "Robot": robot_data.name,
            "Kinematics": folder_name,
            "token": self.token
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp

    def add_tool(self, id:str) -> str:
        url = f"https://{self.__host}:{self.__port}/URTC"
        data = {
            "Id": id,
            "token": self.__token
        }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp
    
    def add_robot(self, robot_data:RobotData, angle_count:int, kinematics:str="None") -> str:
        # Add robot
        url = f"https://{self.__host}:{self.__port}/CreateRobot"
        data = {
            "Robot": robot_data.name,
            "Angle": angle_count,
            "Kinematics": kinematics,
            "Code": robot_data.code,
            "token": self.__token
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        # Add account for so that the robot itself sends some system commands
        url = f"https://{self.__host}:{self.__port}/CreateAccount"
        data = {
            "name": robot_data.name,
            "password": "robot",
            "User_role": "robot",
            "token": self.__token
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp
    
    def set_robot_home(self, robot_data:RobotData, angles:list) -> str:
        url = f"https://{self.__host}:{self.__port}/HomePosition"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        for i in range(1, len(angles)+1):
            data[f"J{i}"] = angles[i-1]
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp

    def delete_tool(self, id) -> str:
        url = f"https://{self.__host}:{self.__port}/URTD"
        data = {
            "id": id,
            "token": self.__token
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp

    def delete_robot(self, robot_data:RobotData) -> str:
        url = f"https://{self.__host}:{self.__port}/DelRobot"
        data = {
            "Robot": robot_data.name,
            "token": self.__token
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp

    def add_user(self, name:str, password:str) -> None:
        if password != "robot":
            url = f"https://{self.__host}:{self.__port}/CreateAccount"
            data = {
                "name": name,
                "password": password,
                "User_role": roles.Roles.user,
                "token": self.__token
                }
            resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
            return resp
        else:
            raise TypeError("The word robot cannot be used in the password because it is reserved")
    
    def get_robots(self) -> str:
        url = f"https://{self.__host}:{self.__port}/GetRobots"
        data = {
            "token": self.__token
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp

    def get_robot(self, robot_data:RobotData) -> str:
        url = f"https://{self.__host}:{self.__port}/GetRobot"
        data = {
            "Robot": robot_data.name,
            "token": self.__token
            }
        resp = requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text
        return resp
    
    def add_log(self, robot_data:RobotData, type:str, text:str) -> bool:
        url = f"https://{self.__host}:{str(self.__port)}/URLogs"
        data = {
            "Robot": robot_data.name,
            "Type": type,
            "Text": text,
            "token": self.__token
            }
        return bool(requests.post(url, verify=True, data=json.loads(json.dumps(data, ensure_ascii=False))).text)
    