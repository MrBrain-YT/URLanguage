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
        self._host = host
        self._port = port
        self._token = token if external_token == "" else external_token
        super().__init__(host, port, self._token)
        
    def delete_user(self, name:str) -> str:
        url = f"https://{self._host}:{self._port}/DeleteAccount"
        data = {
            "name": name,
            "token": self._token
            }
        resp = requests.post(url, verify=True, data=data).text
        return resp

    def add_user(self, name:str, password:str, role:str) -> str:
        if password != "robot":
            url = f"https://{self._host}:{self._port}/CreateAccount"
            data = {
                "name": name,
                "password": password,
                "user_role": role,
                "token": self._token
                }
            resp = requests.post(url, verify=True, data=data).text
            return resp
        else:
            raise TypeError("The word robot cannot be used in the password because it is reserved")
    
    def get_user_accounts(self) -> str:
        url = f"https://{self._host}:{self._port}/GetAccounts"
        data = {"token": self._token}
        resp = requests.post(url, verify=True, data=data).text
        return resp
    
    def change_password(self, name:str, password:str) -> str:
        url = f"https://{self._host}:{self._port}/ChangePass"
        data = {
            "name": name,
            "password": password,
            "token": self._token
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
        url = f"https://{self._host}:{self._port}/GetToken"
        data = {
            "name": name,
            "password": password,
            "token": self._token
        }
        resp = requests.post(url, verify=True, data=data).text
        return resp
    
    def change_token(self, name:str, password:str) -> str:
        if password != "robot":
            url = f"https://{self._host}:{self._port}/ChangeToken"
            data = {
                "name": name,
                "password": password,
                "token": self._token
            }
            resp = requests.post(url, verify=True, data=data).text
            return resp
        else:
            raise TypeError("The word robot cannot be used in the password because it is reserved")
    
    def export_cache(self) -> list[dict]:
        url = f"https://{self._host}:{self._port}/ExportCache"
        data = {
            "token": self._token
        }
        resp = requests.post(url, verify=True, data=data).text
        robots = ast.literal_eval(resp.split("\n")[0].replace("robots = ", ""))
        tools = ast.literal_eval(resp.split("\n")[1].replace("tools = ", ""))
        frames = ast.literal_eval(resp.split("\n")[2].replace("frames = ", ""))
        return [robots, tools, frames]
    
    def import_cache(self, robots:dict, tools:dict, frames:dict) -> str:
        url = f"https://{self._host}:{self._port}/ImportCache"
        data = {
            "token": self._token,
            "robots": str(robots),
            "tools": str(tools),
            "frames": str(frames)
        }
        resp = requests.post(url, verify=True, data=data).text
        return resp