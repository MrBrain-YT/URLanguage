from typing import Union, TYPE_CHECKING

import requests

from data_types import RobotData, AnglePos, XYZPos, ReturnData
from utils.trajectory_creator import TrajectoryConstructor

if TYPE_CHECKING:
    import __super_admin as super_admin
    import __admin as admin
    import __user as user
    
# Trajectory sending variable (work in lin and circ functions)
TRAJECTORY_SEND_SWITCH = True # True - send data, false - don't send data

class Robot():
    
    def __init__(self, host:str, port:int, token:str) -> None:
        self._host = host
        self._port = port
        self._token = token
        
    def _speed_multiplier(self, speed_list:list, multiplier:float):
        for index, value in enumerate(speed_list):
            speed_list[index] = value * multiplier
        return speed_list
    
    def get_angles_count(self, robot_data:RobotData) -> int:
        url = f"https://{self._host}:{str(self._port)}/GetRobotAnglesCount"
        data = {
            "Robot": robot_data.name,
            "token": self._token
        }
        response = requests.post(url, verify=True, json=data).json()["data"]
        return response
        
    def check_emergency(self, robot_data:RobotData) -> bool:
        if TRAJECTORY_SEND_SWITCH:
            url = f"https://{self._host}:{str(self._port)}/GetRobotEmergency"
            data = {
                "Robot": robot_data.name,
                "token": self._token,
                "Code": robot_data.code
            }
            response = requests.post(url, verify=True, json=data).json()["data"]
            return response
        return False

    def set_robot_position(self, robot_data:RobotData, angles:Union[AnglePos, list[AnglePos]], is_multi_point:bool=False) -> dict:
        # Set position
        url = f"https://{self._host}:{str(self._port)}/CurentPosition"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code" : robot_data.code
            }
        if not is_multi_point:
            data = data | angles.export_to(export_type=dict).get("data")
        else:
            converted_angles = []
            for angle in angles:
                converted_angles.append(angle.export_to(export_type=dict).get("data"))
            data["angles_data"] = str(converted_angles)
        request_data = requests.post(url, verify=True, json=data)
        return request_data.json(), request_data.status_code
    
    def set_robot_speed(self, robot_data:RobotData, angles_speed:Union[AnglePos, list[AnglePos]], is_multi_point:bool=False) -> dict:
        # Set motor speed
        url = f"https://{self._host}:{str(self._port)}/CurentSpeed"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code" : robot_data.code
            }
        if not is_multi_point:
            data = data | angles_speed.export_to(export_type=dict).get("data")
        else:
            data["angles_data"] = angles_speed
            converted_speeds = []
            for angle_speed in angles_speed:
                converted_speeds.append(angle_speed.export_to(export_type=dict).get("data"))
            data["angles_data"] = str(converted_speeds)
        request_data = requests.post(url, verify=True, json=data)
        return request_data.json(), request_data.status_code
        
    def move_xyz(self, robot_data:RobotData, position:XYZPos) -> dict:
        url = f"https://{self._host}:{str(self._port)}/Move_XYZ"
        data = {
            "Robot": robot_data.name,
            "x": position.x,
            "y": position.y,
            "z": position.z,
            "token": self._token,
            "Code" : robot_data.code
            }
        response = requests.post(url, verify=True, json=data)
        return ReturnData(responce=response.text, code=response.status_code, trjectory=position)

    def move_angle(self, robot_data:RobotData, angles:AnglePos) -> dict:
        url = f"https://{self._host}:{str(self._port)}/angle_to_xyz"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code" : robot_data.code
            }
        angles_count = self.get_angles_count(robot_data)
        for count in range(angles_count):
            data[f"J{count+1}"] = angles.angles[f"J{count+1}"]
        return requests.post(url, verify=True, json=data).json()

    def xyz_to_angle(self, robot_data:RobotData, positions:list[XYZPos], is_multi_point:bool=False) -> Union[AnglePos, list[AnglePos]]:
        new_positions = []
        for pos in positions:
            new_positions.append(pos.export_to(export_type=list))
            
        url = f"https://{self._host}:{str(self._port)}/XYZ_to_angle"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code" : robot_data.code,
            "positions_data": str(new_positions)
            }
        result = requests.post(url, verify=True, json=data).json()["data"]
        if not is_multi_point:
            return AnglePos().from_dict(result[0], rewrite=True)
        else:
            angles:list[AnglePos] = []
            for res in result:
                angles.append(AnglePos().from_dict(res))
            return angles

    def angle_to_xyz(self, robot_data:RobotData, angles:AnglePos) -> dict:
        ''' TODO: add support MutiPoint angles'''
        url = f"https://{self._host}:{str(self._port)}/angle_to_xyz"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code" : robot_data.code
            }
        angles_count = self.get_angles_count(robot_data)
        for count in range(angles_count):
            data[f"J{count+1}"] = angles.angles[f"J{count+1}"]
        return requests.post(url, verify=True, json=data).json()
    
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

    def ptp(self, robot_data:RobotData, angles:AnglePos, step_count:int=100) -> ReturnData:
        url = f"https://{self._host}:{str(self._port)}/GetCurentPosition"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code": robot_data.code
            }
        current_angles = requests.post(url, verify=True, json=data).json()["data"]
        
        start_angles:AnglePos
        if isinstance(current_angles, list):
            start_angles = AnglePos().from_dict(current_angles[-1])
        else:
            start_angles = AnglePos().from_dict(current_angles)
        # Вычисление скоростей вращения для перемещения от начальной позиции к конечной
        speeds = AnglePos().from_list(self.calculate_speed(start_angles, angles, step_count))

        position_responce, pos_code = self.set_robot_position(robot_data, angles)
        speed_responce, speed_code = self.set_robot_speed(robot_data, speeds)
        
        response_data = {"Set position": position_responce,
                         "Set speed": speed_responce}
        response_codes = {"Set position": pos_code,
                         "Set speed": speed_code}
        return ReturnData(responce=response_data, code=response_codes, trjectory=[])

    
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
            points.append(XYZPos().from_list([x1 + i * x_step, y1 + i * y_step, z1 + i * z_step]))
        return points
    
    def lin(self, robot_data:RobotData, end_point:XYZPos, num_points:int=25, lin_step_count:int=25, speed_multiplier:int=1, start:XYZPos=None) -> ReturnData:
        if start is None:
            if TRAJECTORY_SEND_SWITCH:
                url = f"https://{self._host}:{str(self._port)}/GetXYZPosition"
                data = {
                    "Robot": robot_data.name,
                    "token": self._token
                    }
                responce_data = requests.post(url, verify=True, json=data).json()["data"]
                start = XYZPos().from_dict(responce_data)
            else:
                start = XYZPos().from_list([0, 0, 0])
        
        arc_points = []
        if end_point.smooth_endPoint is None:
            full_trajectory_points = self.generate_line_points(start, end_point, num_points)
        else:
            cartesian_points = []
            updating_end_point = end_point
            cartesian_points = TrajectoryConstructor().find_smoothing_points(updating_end_point, cartesian_points)
            
            # Create trajectory
            updating_start_point = start
            full_trajectory_points = [start]
            full_trajectory_points = TrajectoryConstructor().smooth_trajectory(robot_data, full_trajectory_points, cartesian_points, updating_start_point, lin_step_count)
            
        if TRAJECTORY_SEND_SWITCH:
            arc_points = self.xyz_to_angle(robot_data, full_trajectory_points, is_multi_point=True)
            new_speeds:list = []
            for index, point in enumerate(arc_points):
                old_point:AnglePos = None
                if index == 0:
                    url = f"https://{self._host}:{str(self._port)}/GetCurentPosition"
                    data = {
                        "Robot": robot_data.name,
                        "token": self._token
                        }
                    current_angles = requests.post(url, verify=True, json=data).json()["data"]
                    
                    if isinstance(current_angles, list):
                        old_point = AnglePos().from_dict(current_angles[-1])
                    else:
                        old_point = AnglePos().from_dict(current_angles)

                    old_point = AnglePos().from_list(old_point)
                    
                else:
                    old_point = arc_points[index-1]
                
                speed = self._speed_multiplier(self.calculate_lin(old_point, point, lin_step_count), speed_multiplier)
                new_speeds.append(AnglePos().from_list(speed))
            
            position_responce, pos_code = self.set_robot_position(robot_data, arc_points, is_multi_point=True)
            speed_responce, speed_code = self.set_robot_speed(robot_data, new_speeds, is_multi_point=True)
            
            response_data = {"Set position": position_responce,
                            "Set speed": speed_responce}
            response_codes = {"Set position": pos_code,
                            "Set speed": speed_code}
            return ReturnData(responce=response_data, code=response_codes, trjectory=full_trajectory_points)
        else:
            return ReturnData(responce=None, code=None, trjectory=full_trajectory_points)

    def circ(self, robot_data:RobotData, points_xyz:list[XYZPos], count_points:int, speed_multiplier:float=1, lin_step_count:int=10) -> ReturnData:
        if not self.check_emergency(robot_data):
            if points_xyz[2].smooth_endPoint is None:
                coords, _start_smooth_point, _start_smoothing_point = self.generate_arc_points(
                    points_xyz[0],
                    points_xyz[1],
                    points_xyz[2],
                    count_points
                    )
                full_trajectory_points = []
                for point in coords:
                    full_trajectory_points.append(XYZPos(x=point[0], y=point[1], z=point[2]))
            else:
                # Find smoothing points
                cartesian_points = [points_xyz]
                updating_end_point:Union[list[XYZPos], XYZPos] = points_xyz
                cartesian_points = TrajectoryConstructor().find_smoothing_points(updating_end_point, cartesian_points)
                # Create trajectory
                updating_start_point = points_xyz[0]
                full_trajectory_points = [points_xyz[0]]
                full_trajectory_points = TrajectoryConstructor().smooth_trajectory(robot_data, full_trajectory_points, cartesian_points, updating_start_point, count_points)
              
            if TRAJECTORY_SEND_SWITCH:            
                arc_points = self.xyz_to_angle(robot_data, full_trajectory_points, is_multi_point=True)
                new_speeds:list = []
                for index, point in enumerate(arc_points):
                    old_point:list = []
                    if index == 0:
                        url = f"https://{self._host}:{str(self._port)}/GetCurentPosition"
                        data = {
                            "Robot": robot_data.name,
                            "token": self._token
                            }
                        current_angles = requests.post(url, verify=True, json=data).json()["data"]
                        
                        if isinstance(current_angles, list):
                            old_point = AnglePos().from_dict(current_angles[-1])
                        else:
                            old_point = AnglePos().from_dict(current_angles)

                        old_point = AnglePos().from_list(old_point)
                        
                    else:
                        old_point = arc_points[index-1]

                    speed = self._speed_multiplier(self.calculate_lin(old_point, point, lin_step_count), speed_multiplier)
                    new_speeds.append(AnglePos().from_list(speed))
                    
                position_responce, pos_code = self.set_robot_position(robot_data, arc_points, is_multi_point=True)
                speed_responce, speed_code = self.set_robot_speed(robot_data, new_speeds, is_multi_point=True)
                
                response_data = {"Set position": position_responce,
                            "Set speed": speed_responce}
                response_codes = {"Set position": pos_code,
                                "Set speed": speed_code}
                return ReturnData(responce=response_data, code=response_codes, trjectory=full_trajectory_points)
            else:
                return ReturnData(responce=None, code=None, trjectory=full_trajectory_points)
        else:
            return "The robot is currently in emergency stop"
            

    def get_log(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{str(self._port)}/URLog"
        data = {
            "Robot": robot_data.name,
            "token": self._token
            }
        return requests.post(url, verify=True, json=data).json()

    def get_last_log(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{str(self._port)}/URLog"
        data = {
            "Robot": robot_data.name,
            "token": self._token
            }
        return requests.post(url, verify=True, json=data).json()["data"].split("\n")[-1]
    
    def debug(self, robot_data:RobotData, text:str) -> dict:
        url = f"https://{self._host}:{str(self._port)}/URLogs"
        data = {
            "Robot": robot_data.name,
            "Type": "DEBUG",
            "Text": text
            }
        return requests.post(url, verify=True, json=data).json()
    
    def set_program(self, robot_data:RobotData, program:str) -> dict:
        url = f"https://{self._host}:{str(self._port)}/SetProgram"
        data = {
            "Robot": robot_data.name,
            "Program": program.encode().hex(),
            "token": self._token,
            "Code" : robot_data.code
            }
        return requests.post(url, verify=True, json=data).json()
    
    def delete_program(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{str(self._port)}/DeleteProgram"
        data = {
            "Robot": robot_data.name,
            "token": self._token,
            "Code" : robot_data.code
            }
        return requests.post(url, verify=True, json=data).json()