"""  Authorizing users and passing their token to the class corresponding to their role

To get users in the __get_role function, a server token is sent to the server,
which is created by the person who runs this server. After receiving data from the server,
it is checked with input data (username, password),
the received token is transferred to the tokenizer class and the system class is issued from a specific role module.

"""

import requests
import json

import __user as User
import __admin as Admin
import __super_admin as SuperAdmin

class Auth():
    def __init__(self, ip:str, port:int, server_token:str) -> None:
        self.ip = ip
        self.port = port
        self.server_token = server_token

    def __get_role(self, name, password):
        try:
            url = f"https://{self.ip}:{self.port}/GetRoleAccount"
            data = {
                "name": name,
                "password": password, 
                "server_token": self.server_token
                }
            response:dict = json.loads(requests.post(url, verify=True, data=data).text)
            if response.get("status") != False:
                return response.get("role"), response.get("token") 
            else:
                raise ValueError("Wrong login or password")
        except:
            raise ValueError("Wrong login or password")

    def user(self, name, password) -> User:
        if password != "robot":
            role, token = self.__get_role(name, password)
            User.tokenizer(token).set_token()
            return User
    
    def admin(self, name, password) -> Admin:
        if password != "robot":
            role, token = self.__get_role(name, password)
            if role != "user":
                    Admin.tokenizer(token).set_token()
                    return Admin
            else:
                raise TypeError("You don't have enough rights")
            
        
    def super_admin(self, name, password) -> SuperAdmin:
        if password != "robot":
            role, token = self.__get_role(name, password)
            if role != "user" and role != "administrator":
                SuperAdmin.tokenizer(token).set_token()
                return SuperAdmin
            else:
                raise TypeError("You don't have enough rights")
