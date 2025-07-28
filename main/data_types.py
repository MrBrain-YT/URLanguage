""" Classes for creating robots positions or robot data"""

from typing import Union, TYPE_CHECKING, Any
from dataclasses import dataclass

import requests
from scipy.interpolate import CubicSpline
import numpy as np

from utils.config import Config

if TYPE_CHECKING:
    import __super_admin as super_admin
    import __admin as admin
    import __user as user

class XYZPos:
    
    def __init__(self, smooth_distance:float=5, smooth_endPoint:Union['XYZPos', list['XYZPos'],None]=None, circ_angle:Union[float, None]=None, send:str=None, **kwargs):
        self.x:float = kwargs.get('x')
        self.y:float = kwargs.get('y')
        self.z:float = kwargs.get('z')
        self.a:float = kwargs.get('a') if kwargs.get('a') is not None else 0
        self.b:float = kwargs.get('b') if kwargs.get('b') is not None else 0
        self.c:float = kwargs.get('c') if kwargs.get('c') is not None else 0
        self.smooth_distance:float = smooth_distance
        self.smooth_endPoint:XYZPos = smooth_endPoint
        self.circ_angle:float = circ_angle
        self.send:str = "" if send is None else send
        
    def __str__(self):
        return f"XYZPos: {[self.x, self.y, self.z, self.c, self.b, self.a, self.send]}"
    
    def __eq__(self, value:"XYZPos"):
        return self.x == value.x and self.y == value.y and self.z == value.z
        
    @classmethod
    def from_dict(cls, data:dict):
        new_x = data['x']
        new_y = data['y']
        new_z = data['z']
        new_send = data.get("send")
        if (isinstance(data['a'], (int, float)) and isinstance(data['b'], (int, float)) and isinstance(data['c'], (int, float))):
            new_a = data['a']
            new_b = data['b']
            new_c = data['c']
            return cls(x=new_x, y=new_y, z=new_z, a=new_c, b=new_b, c=new_a, send=new_send)
        else:
            return cls(x=new_x, y=new_y, z=new_z, a=0, b=0, c=0, send=new_send)
    
    @classmethod
    def from_list(cls, data:list):
        new_x = data[0]
        new_y = data[1]
        new_z = data[2]
        if len(data) > 3:
            new_a = data[3]
            new_b = data[4]
            new_c = data[5]
            return cls(x=new_x, y=new_y, z=new_z, a=new_c, b=new_b, c=new_a)
        else:
            return cls(x=new_x, y=new_y, z=new_z, a=0, b=0, c=0)
        
    def export_to(self, export_type:Union[list, dict]):
        if isinstance(export_type, dict) or export_type is dict:
                return {
                    'x': self.x,
                    'y': self.y,
                    'z': self.z,
                    'a': self.c,
                    'b': self.b,
                    'c': self.a,
                    'send': self.send,
                }
        elif isinstance(export_type, list) or export_type is list:
            return [self.x, self.y, self.z, self.c, self.b, self.a, self.send]
        else:
            raise ValueError('Export type must be a list or dictionary')  
        
class AnglePos:
    
    def __init__(self, send:str=None, use_send:bool=True, *args):
        self.angles = {}
        if use_send:
            self.angles["send"] = "" if send is None else send
        for index, arg in enumerate(args):
            if not isinstance(arg, (int, float)):
                raise TypeError('All arguments must be numbers')
            else:
                self.angles[f"J{index}"] = arg
                
    def __len__(self):
        return len(self.angles.keys())
    
    def __getitem__(self, key:str) -> Union[Any, None]:
        if isinstance(key, str):
            return self.angles.get(key)
        elif isinstance(key, int):
            return self.export_to(list)[key]
        else:
            raise TypeError("Subscription argument can only be of type string or int")
    
    def __setitem__(self, key:str, value:Any) -> None:
        if isinstance(key, str):
            self.angles[key] = value
        elif isinstance(key, int):
            values = list(self.angles.keys())
            str_key = values.index(key)
            self.angles[str_key] = value
        else:
            raise TypeError("Subscription argument can only be of type string or int")
        
    def __str__(self):
        return str(self.angles)
        
    def from_dict(self, data:dict, rewrite:bool=False):
        if rewrite:
            self.angles = data
        else:
            for key, value in data.items():
                self.angles[key] = value
                
        if "send" not in list(self.angles.keys()):
            self.angles["send"] = ""
        return self
    
    def from_list(self, data:list):
        """ Import data from list \n
        Used only for angles parameters, not `send` parameter
        """
        for index, arg in enumerate(data):
            if not isinstance(arg, (int, float)):
                raise TypeError('All arguments must be numbers')
            else:
                self.angles[f"J{index + 1}"] = arg
        return self
                
    def export_to(self, export_type:Union[list, dict]):
        if isinstance(export_type, dict) or export_type is dict:
            return self.angles
        elif isinstance(export_type, list) or export_type is list:
            return list(self.angles.values())
        else:
            raise ValueError('Export type must be a list or dictionary')
           
class Spline:
    
    def __init__(self, robot_data: "RobotData", coordinate_system:str, system: Union["super_admin.system", "admin.system", "user.system"], points_count: int = 25, speed_multiplier: float = 1, num_points: int = 50):
        self.points: list[XYZPos] = []
        self.system = system
        self.robot_data = robot_data
        self.coordinate_system = coordinate_system
        self.lin_step_count = points_count
        self.speed_multiplier = speed_multiplier
        self.num_points = num_points
        self.config = Config()
        
    def add_point(self, *point: XYZPos) -> "Spline":
        self.points.extend(point)
        return self
    
    def catmull_rom_spline(self, P0, P1, P2, P3, t):
        """ Вычисляет точку на сплайне Катмулл-Рома """
        t2 = t * t
        t3 = t2 * t

        f1 = -0.5 * t3 + t2 - 0.5 * t
        f2 =  1.5 * t3 - 2.5 * t2 + 1
        f3 = -1.5 * t3 + 2.0 * t2 + 0.5 * t
        f4 =  0.5 * t3 - 0.5 * t2

        return P0 * f1 + P1 * f2 + P2 * f3 + P3 * f4

    def catmull_rom_chain(self, points):
        """ Генерирует гладкий сплайн через все заданные точки """
        new_points = []

        for i in range(1, len(points) - 2):  # Берем по 4 точки для интерполяции
            P0, P1, P2, P3 = points[i - 1], points[i], points[i + 1], points[i + 2]
            for t in np.linspace(0, 1, self.num_points // (len(points) - 3)):
                new_point = self.catmull_rom_spline(P0, P1, P2, P3, t)
                new_points.append(new_point)

        return np.array(new_points)

    def _create_catmull_rom_spline_points(self) -> list[XYZPos]:
        """ Преобразует точки в сглаженный сплайн Катмулл-Рома """
        if len(self.points) < 4:
            raise ValueError("Для сглаженного сплайна требуется минимум 4 точки.")

        # Преобразуем точки в массив NumPy
        converted_points = np.array([point.export_to(export_type=list)[0:-1] for point in self.points])

        # Добавляем фиктивные крайние точки (чтобы не терять сегменты)
        extended_points = np.vstack([converted_points[0], converted_points, converted_points[-1]])

        # Генерируем сглаженный сплайн
        new_points = self.catmull_rom_chain(extended_points)

        # Конвертируем обратно в список XYZPos
        return [XYZPos().from_list(point) for point in new_points]

    def _create_scypy_spline_points(self) -> list[XYZPos]:
        # Преобразуем все точки в numpy-массив
        converted_points = [point.export_to(export_type=list) for point in self.points]
        points = np.array(converted_points)
        # Разделяем координаты и углы
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        a, b, c = points[:, 3], points[:, 4], points[:, 5]
        # Создаем параметр t для интерполяции (равномерное распределение)
        t = np.linspace(0, 1, len(points))
        
        # Интерполяция кубическими сплайнами по каждой координате и углу
        cs_x = CubicSpline(t, x)
        cs_y = CubicSpline(t, y)
        cs_z = CubicSpline(t, z)
        cs_a = CubicSpline(t, a)
        cs_b = CubicSpline(t, b)
        cs_c = CubicSpline(t, c)
        # Новый параметр t с нужным количеством точек
        t_fine = np.linspace(0, 1, self.num_points)
        # Вычисляем новые значения по сплайнам
        x_new = cs_x(t_fine)
        y_new = cs_y(t_fine)
        z_new = cs_z(t_fine)
        a_new = cs_a(t_fine)
        b_new = cs_b(t_fine)
        c_new = cs_c(t_fine)
        # Формируем новые точки
        new_points = np.array([x_new, y_new, z_new, a_new, b_new, c_new]).T
        # Преобразуем массив в список объектов XYZPos
        result_points = [XYZPos().from_list(p.tolist()) for p in new_points]

        return result_points
            
    def start_move(self) -> "ReturnData":
        full_trajectory_points = self._create_scypy_spline_points()
        if self.config.trajectory_send:
            arc_points = self.system.xyz_to_angle(self.robot_data, full_trajectory_points, self.coordinate_system, is_multi_point=True)
            # Set send parameter from xyz point to angle point
            for index, point in enumerate(full_trajectory_points):
                    arc_points[index]["send"] = point.send
                    
            new_speeds:list = []
            for index, point in enumerate(arc_points):
                old_point:AnglePos = None
                if index == 0:
                    url = f"https://{self.system._host}:{str(self.system._port)}/GetCurentPosition"
                    data = {
                        "robot": self.robot_data.name,
                        "token": self.system._token
                        }
                    verify = self.config.verify
                    current_angles = requests.post(url, verify=verify, json=data).json()["data"]
                    
                    if isinstance(current_angles, list):
                        old_point = AnglePos().from_dict(current_angles[-1])
                    else:
                        old_point = AnglePos().from_dict(current_angles)
                else:
                    old_point = arc_points[index-1]
                speed = self.system._speed_multiplier(self.system.calculate_speed(old_point, point, self.lin_step_count), self.speed_multiplier)
                new_speeds.append(AnglePos(use_send=False).from_list(speed))
                
            position_responce = self.system.set_robot_position(self.robot_data, arc_points, is_multi_point=True, last_point_position=self.points[-1])
            speed_responce = self.system.set_robot_speed(self.robot_data, new_speeds, is_multi_point=True)
            
            response_data = {"Set position": position_responce[0],
                            "Set speed": speed_responce[0]}
            response_codes = {"Set position": position_responce[1],
                            "Set speed": speed_responce[1]}
            return ReturnData(responce=response_data, code=response_codes, trjectory=full_trajectory_points)
        else:
            return ReturnData(responce=None, code=None, trjectory=full_trajectory_points)

@dataclass
class RobotData:
    name: str
    code: str
    
    def __str__(self):
        return f"Robot '{self.name}' | code '{self.code}'"
        
@dataclass   
class ReturnData():
    responce: Union[str, dict, None]
    code: Union[str, dict, None]
    trjectory: list[XYZPos] = None
    
class StaticData:
    
    class Roles:
        """  Roles for create new users """
        ROBOT = "robot"
        USER = "user"
        ADMIN = "administrator"
        SUPER_ADMIN = "SuperAdmin"
        
    class CoordinatesSystem:
        """  Coordinates system for send to moving commands """
        FLANGE = "flange"
        TOOL = "tool"
        BASE = "base"
        WORLD = "world"