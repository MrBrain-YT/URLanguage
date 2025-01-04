import json
import ast

import requests
import numpy as np
from scipy.interpolate import CubicSpline

from data_types import RobotData, AnglePos, XYZPos

class Robot():
    
    def __init__(self, host:str, port:int, token:str) -> None:
        self.__host = host
        self.__port = port
        self.__token = token
        
    # NOT USED
    # def __pointList_to_Dict(self, point:list) -> dict:
    #     dict_point = {}
    #     for count in range(len(point)):
    #         dict_point[f"J{count + 1}"] = point[count]
    #     return dict_point
    # def __pointDict_to_List(self, point:dict) -> list:
    #     list_point = []
    #     for count in range(len(point.keys())):
    #         list_point.append(point[f"J{count + 1}"])
    #     return list_point
    
    def get_angles_count(self, robot_data:RobotData):
        url = f"https://{self.__host}:{str(self.__port)}/GetRobotAnglesCount"
        data = {
            "Robot": robot_data.name,
            "token": self.__token
        }
        response = requests.post(url, verify=True, data=data).text
        return int(response)
    
    def __speed_multiplier(self, speed_list:list, multiplier:float):
        for index, value in enumerate(speed_list):
            speed_list[index] = value * multiplier

        return speed_list
        
    def check_emergency(self, robot_data:RobotData) -> bool:
        url = f"https://{self.__host}:{str(self.__port)}/GetRobotEmergency"
        data = {
            "Robot": robot_data.name,
            "token": self.__token
        }
        response = requests.post(url, verify=True, data=data).text
        if  bool(response):
            return True
        else:
            return False

    def ptp(self, robot_data:RobotData, angles:AnglePos) -> str:
        angles_dict = angles.export_to(export_type=dict).get("data")
        # Set position
        url = f"https://{self.__host}:{str(self.__port)}/CurentPosition"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        for i in range(1, len(angles_dict)+1):
            data[f"J{i}"] = angles_dict[i-1]
        responce = requests.post(url, verify=True, data=data).text
        # Set motor speed
        url = f"https://{self.__host}:{str(self.__port)}/CurentSpeed"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        for i in range(1, len(angles_dict)+1):
            data[f"J{i}"] = 1
        requests.post(url, verify=True, data=data)

        return responce
        
    def move_xyz(self, robot_data:RobotData, position:XYZPos) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/Move_XYZ"
        data = {
            "Robot": robot_data.name,
            "X": position.x,
            "Y": position.y,
            "Z": position.z,
            "token": self.__token,
            "Code" : robot_data.code
            }
        return requests.post(url, verify=True, data=data).text

    def move_angle(self, robot_data:RobotData, angles:AnglePos) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/angle_to_xyz"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        angles_count = self.get_angles_count(robot_data)
        for count in range(angles_count):
            data[f"J{count+1}"] = angles.angles[f"J{count+1}"]
        return requests.post(url, verify=True, data=data).text

    def xyz_to_angle(self, robot_data:RobotData, positions:list[XYZPos], is_multi_point:bool=False) -> list:
        new_positions = []
        for pos in positions:
            new_positions.append(pos.export_to(export_type=list))
            
        url = f"https://{self.__host}:{str(self.__port)}/XYZ_to_angle"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code,
            "positions_data": str(positions)
            }
        result = requests.post(url, verify=True, data=data).text
        if not is_multi_point:
            return AnglePos().from_dict(ast.literal_eval(result)[0], rewrite=True)
        else:
            return ast.literal_eval(result)

    def angle_to_xyz(self, robot_data:RobotData, angles:AnglePos) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/angle_to_xyz"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        angles_count = self.get_angles_count(robot_data)
        for count in range(angles_count):
            data[f"J{count+1}"] = angles.angles[f"J{count+1}"]
        return requests.post(url, verify=True, data=data).text
    
    @staticmethod
    def calculate_speed(start_angles:AnglePos, end_angles:AnglePos, steps:int) -> list:
        start_angles = start_angles.export_to(list)
        end_angles = end_angles.export_to(list)
        # Проверка на совпадение размеров списков
        if len(start_angles) != len(end_angles):
            raise ValueError("Списки начальных и конечных углов должны иметь одинаковую длину")
        # Инициализация списка скоростей
        speeds = []
        # Цикл по элементам списков углов
        for i in range(len(start_angles)):
            # Вычисление разницы между начальным и конечным углом для каждого сервомотора
            angle_diff = end_angles[i] - start_angles[i]
            # Вычисление скорости вращения для каждого сервомотора
            speed = angle_diff / steps  # steps - количество шагов
            # Добавление скорости вращения в список
            speeds.append(abs(speed))
        
        return speeds

    def ptp_lin(self, robot_data:RobotData, angles:AnglePos, step_count:int=100) -> None:
        url = f"https://{self.__host}:{str(self.__port)}/GetCurentPosition"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code": robot_data.code
            }
        resp = requests.post(url, verify=True, data=data).text
        speed_angles = json.loads(resp.replace("'", '"'))
        start_angles = AnglePos().from_dict(speed_angles)
        end_angles = angles
        # Вычисление скоростей вращения для перемещения от начальной позиции к конечной
        speeds = self.calculate_speed(start_angles, end_angles, step_count)

        # send current position
        url = f"https://{self.__host}:{str(self.__port)}/CurentPosition"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        for i in range(1, len(end_angles)+1):
            data[f"J{i}"] = end_angles[i-1]
        requests.post(url,  verify=True ,data=data)
        
        # send current speed
        url = f"https://{self.__host}:{str(self.__port)}/CurentSpeed"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        for i in range(1, len(end_angles)+1):
            data[f"J{i}"] = speeds[i-1]
        requests.post(url, verify=True, data=data)
        return "True"
    
    def calculate_lin(self, start_angles:AnglePos, target_angles:AnglePos, step_count:int=100) -> list:
        """Return speed list"""
        # calk speed lin robot moving
        speeds = self.calculate_speed(start_angles, target_angles, step_count)
        return speeds
    
    @staticmethod
    def generate_line_points(start:XYZPos, end:XYZPos, num_points:int):
        """
        Generates a list of points located on a line between two given points.

        :param start: Start point coordinates [x1, y1, z1]
        :param end: End point coordinates [x1, y1, z1]
        :param num_points: Count points
        :return: points_list [[x1, y1, z1], [x2, y2, z2], ...]
        """
        if num_points < 2:
            raise ValueError("The number of points must be at least 2.")

        x1, y1, z1 = start.export_to(list)
        x2, y2, z2 = end.export_to(list)

        # Вычисляем шаги для x, y и z
        x_step = (x2 - x1) / (num_points - 1)
        y_step = (y2 - y1) / (num_points - 1)
        z_step = (z2 - z1) / (num_points - 1)

        # Генерируем список точек
        points = []
        for i in range(num_points):
            points.append([x1 + i * x_step, y1 + i * y_step, z1 + i * z_step])
        return points
    
    def lin(self, robot_data:RobotData, start:XYZPos, end:XYZPos, num_points:int=50, lin_step_count:int=100, speed_multiplier:int=1):
        points = self.generate_line_points(start, end, num_points)
        arc_points = self.xyz_to_angle(robot_data, points, is_multi_point=True)
        
        new_speeds:list = []
        for index, point in enumerate(arc_points):
            old_point:list = []
            if index == 0:
                url = f"https://{self.__host}:{str(self.__port)}/GetCurentPosition"
                data = {
                    "Robot": robot_data.name,
                    "token": self.__token
                    }
                resp = requests.post(url, verify=True, data=data).text
                speed_angles = json.loads(resp.replace("'", '"'))
                angles_count = self.get_angles_count(robot_data)
                old_point = []
                for count in range(angles_count):
                    old_point.append(speed_angles[f"J{count+1}"])
                    
                old_point = AnglePos().from_list(old_point)
                
            else:
                old_point = AnglePos().from_dict(arc_points[index-1])
                
            point = AnglePos().from_dict(point)
            
            speed = self.__speed_multiplier(self.calculate_lin(old_point, point, lin_step_count), speed_multiplier)
            new_speeds.append(AnglePos().from_list(speed).export_to(dict).get("data"))
        
        # send current position
        url = f"https://{self.__host}:{str(self.__port)}/CurentPosition"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code,
            "angles_data": str(arc_points)
            }
        requests.post(url, verify=True ,data=data)
        
        # send current speed
        url = f"https://{self.__host}:{str(self.__port)}/CurentSpeed"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code,
            "angles_data": str(new_speeds)
            }
        requests.post(url, verify=True, data=data)
        return True
        
    @staticmethod
    def __interpolate_points(start_point:XYZPos, intermediate_point:XYZPos, end_point:XYZPos, num_points:int):
        # Создание массивов x, y и z координат для начальной, конечной и вспомогательной точек
        x = np.array([start_point.x, intermediate_point.x, end_point.x])
        y = np.array([start_point.y, intermediate_point.y, end_point.y])
        z = np.array([start_point.z, intermediate_point.z, end_point.z])

        # Интерполяция координат по кубическим сплайнам
        t = [0, 0.5, 1]  # Параметры времени для начальной, вспомогательной и конечной точек
        cs = CubicSpline(t, np.vstack([x, y, z]).T)
        # Генерация равномерных значений параметра времени от 0 до 1
        t_interp = np.linspace(0, 1, num=num_points)

        # Вычисление интерполированных координат x, y и z
        x_interp, y_interp, z_interp = cs(t_interp).T

        # Возвращение массива интерполированных точек
        interpolated_points = np.column_stack((x_interp, y_interp, z_interp))
        return interpolated_points

    def circ(self, robot_data:RobotData, points_xyz:list[XYZPos], count_points:int, speed_multiplier:float=1, lin_step_count:int=100) -> bool:
        if self.check_emergency(robot_data):
            coords = self.__interpolate_points(
                points_xyz[0],
                points_xyz[1],
                points_xyz[2],
                count_points)
            
            
            new_positions = []
            for point in coords.tolist():
                new_positions.append(XYZPos(point.x, point.y, point.z))
                
            points:list = []
            arc_points = self.xyz_to_angle(robot_data, new_positions, is_multi_point=True)
            for point in arc_points:
                points.append(point)
                
            new_speeds:list = []
            for index, point in enumerate(points):
                old_point:list = []
                if index == 0:
                    url = f"https://{self.__host}:{str(self.__port)}/GetCurentPosition"
                    data = {
                        "Robot": robot_data.name,
                        "token": self.__token
                        }
                    resp = requests.post(url, verify=True, data=data).text
                    speed_angles = json.loads(resp.replace("'", '"'))
                    angles_count = self.get_angles_count(robot_data)
                    old_point = []
                    for count in range(angles_count):
                        old_point.append(speed_angles[f"J{count+1}"])
                    old_point = AnglePos().from_list(old_point)
                    
                else:
                    old_point = AnglePos().from_dict(arc_points[index-1])
                    
                point = AnglePos().from_dict(point)
                speed = self.__speed_multiplier(self.calculate_lin(old_point, point, lin_step_count), speed_multiplier)
                new_speeds.append(AnglePos().from_list(speed).export_to(dict).get("data"))
                
            # send current position
            url = f"https://{self.__host}:{str(self.__port)}/CurentPosition"
            data = {
                "Robot": robot_data.name,
                "token": self.__token,
                "Code" : robot_data.code,
                "angles_data": str(points)
                }
            requests.post(url,  verify=True ,data=data)
            
            # send current speed
            url = f"https://{self.__host}:{str(self.__port)}/CurentSpeed"
            data = {
                "Robot": robot_data.name,
                "token": self.__token,
                "Code" : robot_data.code,
                "angles_data": str(new_speeds)
                }
            requests.post(url, verify=True, data=data)
            return True
        else:
            return "The robot is currently in emergency stop"

    def get_log(self, robot_data:RobotData) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/URLog"
        data = {
            "Robot": robot_data.name,
            "token": self.__token
            }
        return requests.post(url, verify=True, data=data).text

    def get_last_log(self, robot_data:RobotData) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/URLog"
        data = {
            "Robot": robot_data.name,
            "token": self.__token
            }
        return requests.post(url, verify=True, data=data).text.split("\n")[-1]
    
    def debug(self, robot_data:RobotData, text:str) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/URLogs"
        data = {
            "Robot": robot_data.name,
            "Type": "DEBUG",
            "Text": text
            }
        return requests.post(url, verify=True, data=data).text
    
    def set_program(self, robot_data:RobotData, program:str) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/SetProgram"
        data = {
            "Robot": robot_data.name,
            "Program": program.encode().hex(),
            "token": self.__token,
            "Code" : robot_data.code
            }
        return requests.post(url, verify=True, data=data).text
    
    def delete_program(self, robot_data:RobotData) -> str:
        url = f"https://{self.__host}:{str(self.__port)}/DeleteProgram"
        data = {
            "Robot": robot_data.name,
            "token": self.__token,
            "Code" : robot_data.code
            }
        return requests.post(url, verify=True, data=data).text