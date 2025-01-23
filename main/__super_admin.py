"""  module for additional commands for the SuperAdmin.

The tokenizer class is used to automatically send a token to the system class after registration.

"""

import ast

import requests

import __admin

external_token = ""
class tokenizer():

    def __init__(self, token) -> None:
        self.token = token

    def set_token(self) -> None:
        global external_token
        external_token = self.token

# United robotics system 
class system(__admin.system):

    def __init__(self, host:str, port:int, *token:str) -> None:
        self.host = host
        self.port = port
        self.token = token if external_token == "" else external_token
        super().__init__(host, port, self.token)
        
    def delete_user(self, name:str) -> str:
        url = f"https://{self.host}:{self.port}/DeleteAccount"
        data = {
            "name": name,
            "token": self.token
            }
        resp = requests.post(url, verify=True, data=data).text
        return resp

    def add_user(self, name:str, password:str, role:str) -> str:
        if password != "robot":
            url = f"https://{self.host}:{self.port}/CreateAccount"
            data = {
                "name": name,
                "password": password,
                "user_role": role,
                "token": self.token
                }
            resp = requests.post(url, verify=True, data=data).text
            return resp
        else:
            raise TypeError("The word robot cannot be used in the password because it is reserved")
    
    def get_user_accounts(self) -> str:
        url = f"https://{self.host}:{self.port}/GetAccounts"
        data = {"token": self.token}
        resp = requests.post(url, verify=True, data=data).text
        return resp
    
    def change_password(self, name:str, password:str) -> str:
        url = f"https://{self.host}:{self.port}/ChangePass"
        data = {
            "name": name,
            "password": password,
            "token": self.token
        }
        resp = requests.post(url, verify=True, data=data).text
        return resp
    
    # def get_robot_token(self, name:str) -> str:
    #     url = f"https://{self.host}:{self.port}/GetToken"
    #     data = {
    #         "name": name,
    #         "password": "robot",
    #         "token": self.token
    #     }
    #     resp = requests.post(url, verify=True, data=data).text
    #     return resp
    #     ↓↓↓↓↓↓
    
    def get_account_token(self, name:str, password:str) -> str:
        url = f"https://{self.host}:{self.port}/GetToken"
        data = {
            "name": name,
            "password": password,
            "token": self.token
        }
        resp = requests.post(url, verify=True, data=data).text
        return resp
    
    def change_token(self, name:str, password:str) -> str:
        if password != "robot":
            url = f"https://{self.host}:{self.port}/ChangeToken"
            data = {
                "name": name,
                "password": password,
                "token": self.token
            }
            resp = requests.post(url, verify=True, data=data).text
            return resp
        else:
            raise TypeError("The word robot cannot be used in the password because it is reserved")
    
    def export_cache(self) -> list[dict]:
        url = f"https://{self.__host}:{self.__port}/ExportCache"
        data = {
            "token": self.__token
        }
        resp = requests.post(url, verify=True, data=data).text
        robots = ast.literal_eval(resp.split("\n")[0].replace("robots = ", ""))
        tools = ast.literal_eval(resp.split("\n")[1].replace("tools = ", ""))
        frames = ast.literal_eval(resp.split("\n")[2].replace("frames = ", ""))
        return [robots, tools, frames]
    
    def import_cache(self, robots:dict, tools:dict, frames:dict) -> str:
        url = f"https://{self.__host}:{self.__port}/ImportCache"
        data = {
            "token": self.__token,
            "robots": str(robots),
            "tools": str(tools),
            "frames": str(frames)
        }
        resp = requests.post(url, verify=True, data=data).text
        return resp