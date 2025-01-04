""" Classes for creating robots positions or robot data"""

from typing import Union
from dataclasses import dataclass

class XYZPos:
    
    def __init__(self, **kwargs):
        self.x = kwargs.get('x')
        self.y = kwargs.get('y')
        self.z = kwargs.get('z')
        
    def __str__(self):
        print([self.x, self.y, self.z])
        
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
        print(self.angles)
        
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
                self.angles[f"J{index}"] = arg
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
        
@dataclass
class RobotData:
    name: str
    code: str
    
    def __str__(self):
        print(f"Robot '{self.name}' | code '{self.code}'")