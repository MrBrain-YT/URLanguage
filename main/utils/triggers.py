from typing import Callable, TYPE_CHECKING, Union
import os
import sys
import inspect
from threading import Thread, currentThread
import time

import requests

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from data_types import RobotData

if TYPE_CHECKING:
    import __super_admin as super_admin
    import __admin as admin
    import __user as user

SYSTEM:Union["super_admin.system", "admin.system", "user.system"]

def triggers_handle(robot_data:RobotData, triggers:dict, refresh_timer:float) -> None:
    url_pos_id = f"https://{SYSTEM._host}:{str(SYSTEM._port)}/GetPositionID"
    data_pos_id = {
        "robot": robot_data.name,
        "token": SYSTEM._token
    }
    t = currentThread()
    while getattr(t, "running", True):
        response = requests.post(url_pos_id, verify=True, json=data_pos_id).json()["data"]
        for key, func in triggers.items():
            if str(response) == key:
                func()
        time.sleep(refresh_timer)

class TriggerHandler:
    
    def __init__(self, robot_data:RobotData, system: Union["super_admin.system", "admin.system", "user.system"], refresh_timer:float=1, **kwargs) -> None:
        global SYSTEM
        SYSTEM = system
        self.triggers = {}
        self.robot_data = robot_data
        for key, func in kwargs.items():
            if getattr(func, "__call__") is not None and isinstance(key, str):
                self.triggers[key] = func
        self.thread = None
        self.refresh_timer = refresh_timer
    
    def add_trigger(self, trigger_key:str, func:Callable) -> None:
        if getattr(func, "__call__") is not None and isinstance(trigger_key, str):
            self.triggers[trigger_key] = func
    
    def remove_trigger(self, trigger_key:str) -> None:
        if trigger_key in list(self.triggers.keys()):
            del self.triggers[trigger_key]
            
    def start_handling(self) -> None:
        if self.thread is None:
            handler = Thread(target=triggers_handle, kwargs={"robot_data": self.robot_data, "triggers": self.triggers, "refresh_timer": self.refresh_timer})
            handler.start()
            self.thread = handler
    
    def end_handling(self):
        if self.thread is not None:
            self.thread.running = False
            self.thread = None