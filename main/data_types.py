""" Classes for creating robots positions or robot data"""

from typing import Union, TYPE_CHECKING
import json
from dataclasses import dataclass

import requests
from scipy.interpolate import splprep, splev
import numpy as np

if TYPE_CHECKING:
    import __super_admin as super_admin
    import __admin as admin
    import __user as user

class XYZPos:
    
    def __init__(self, smooth_distance:float=5, smooth_endPoint:Union['XYZPos', None]=None, **kwargs):
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')
        self.z = kwargs.get('z')
        self.smooth_distance = smooth_distance
        self.smooth_endPoint = smooth_endPoint
        
    def __str__(self):
        return f"XYZPos: {[self.x, self.y, self.z]}"
        
    @classmethod
    def from_dict(cls, data:dict):
        new_x = data['x']
        new_y = data['y']
        new_z = data['z']
        return cls(x=new_x, y=new_y, z=new_z)
    
    @classmethod
    def from_list(cls, data:list):
        if len(data) == 3:
            new_x = data[0]
            new_y = data[1]
            new_z = data[2]
            return cls(x=new_x, y=new_y, z=new_z)
        else:
            raise ValueError('List must contain exactly 3 elements')
        
    def export_to(self, export_type:Union[list, dict]):
        if isinstance(export_type, dict) or export_type is dict:
            return {
                'type': export_type['type'],
                'data': {
                    'x': self.x,
                    'y': self.y,
                    'z': self.z
                }
            }
        elif isinstance(export_type, list) or export_type is list:
            return [self.x, self.y, self.z]
        else:
            raise ValueError('Export type must be a list or dictionary')  
        
class AnglePos:
    
    def __init__(self, *args):
        self.angles = {}
        for index, arg in enumerate(args):
            if not isinstance(arg, (int, float)):
                raise TypeError('All arguments must be numbers')
            else:
                self.angles[f"J{index}"] = arg
                
    def __len__(self):
        return len(self.angles.keys())
    
    def __getitem__(self, index:int) -> float:
        return self.export_to(list)[index]
                
    def __str__(self):
        return self.angles
        
    def from_dict(self, data:dict, rewrite:bool=False):
        if rewrite:
            self.angles = data
        else:
            for key, value in data.items():
                self.angles[key] = value
        return self
    
    def from_list(self, data:list):
        for index, arg in enumerate(data):
            if not isinstance(arg, (int, float)):
                raise TypeError('All arguments must be numbers')
            else:
                self.angles[f"J{index + 1}"] = arg
        return self
                
    def export_to(self, export_type:Union[list, dict]):
        if isinstance(export_type, dict) or export_type is dict:
            return {
                'type': export_type['type'],
                'data': self.angles
            }
        elif isinstance(export_type, list) or export_type is list:
            return list(self.angles.values())
        else:
            raise ValueError('Export type must be a list or dictionary')
           
class Spline():
    
    def __init__(self, robot_data:"RobotData", system:Union["super_admin.system", "admin.system", "user.system"], points_count:int=25, speed_multiplier:float=1, num_points:int=100):
        self.points:list[XYZPos] = []
        self.system = system
        self.robot_data = robot_data
        self.lin_step_count = points_count
        self.speed_multiplier = speed_multiplier
        self.num_points = num_points
        
    def add_point(self, *point: XYZPos) -> None:
        for _point in point:
            self.points.append(_point)
        
    def __create_spline_points(self) -> list[XYZPos]:
        converted_points = []
        for point in self.points:
            converted_points.append(point.export_to(export_type=list))
        points = np.array(converted_points)
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        tck, u = splprep([x, y, z], s=0)
        
        u_fine = np.linspace(0, 1, self.num_points)
        x_new, y_new, z_new = splev(u_fine, tck)

        new_points = np.array([x_new, y_new, z_new]).T
        
        points = []
        for point in new_points:
            points.append(XYZPos().from_list([point[0], point[1], point[2]]))
        return points
        
    def start_move(self) -> "ReturnData":
        full_trajectory_points = self.__create_spline_points()
        arc_points = self.system.xyz_to_angle(self.robot_data, full_trajectory_points, is_multi_point=True)
        new_speeds:list = []
        for index, point in enumerate(arc_points):
            old_point:AnglePos = None
            if index == 0:
                url = f"https://{self.system._host}:{str(self.system._port)}/GetCurentPosition"
                data = {
                    "Robot": self.robot_data.name,
                    "token": self.system._token
                    }
                resp = requests.post(url, verify=True, data=data).text
                current_angles = json.loads(resp.replace("'", '"'))
                
                if isinstance(current_angles, list):
                    old_point = AnglePos().from_dict(current_angles[-1])
                else:
                    old_point = AnglePos().from_dict(current_angles)

                old_point = AnglePos().from_list(old_point)
                
            else:
                old_point = arc_points[index-1]
            
            speed = self.system._speed_multiplier(self.system.calculate_lin(old_point, point, self.lin_step_count), self.speed_multiplier)
            new_speeds.append(AnglePos().from_list(speed))
            
        position_responce = self.system.set_robot_position(self.robot_data, arc_points, is_multi_point=True)
        speed_responce = self.system.set_robot_speed(self.robot_data, new_speeds, is_multi_point=True)
        
        response_data = {"Set position": position_responce.text,
                         "Set speed": speed_responce.text}
        response_codes = {"Set position": position_responce.status_code,
                         "Set speed": speed_responce.status_code}
        return ReturnData(responce=response_data, code=response_codes, trjectory=full_trajectory_points)

@dataclass
class RobotData:
    name: str
    code: str
    
    def __str__(self):
        return f"Robot '{self.name}' | code '{self.code}'"
        
@dataclass   
class ReturnData():
    responce: str
    code: int
    trjectory: list[XYZPos] = None