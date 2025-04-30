from typing import Union, TYPE_CHECKING

import requests

from data_types import RobotData, AnglePos, XYZPos, ReturnData
from utils.trajectory_creator import TrajectoryConstructor
    
# Trajectory sending variable (work in lin and circ functions)
TRAJECTORY_SEND_SWITCH = True # True - send data, false - don't send data

class Robot():
    
    def __init__(self, host:str, port:int, token:str) -> None:
        self._host = host
        self._port = port
        self._token = token
        self.last_point_position = None
        
    def _speed_multiplier(self, speed_list:list, multiplier:float):
        for index, value in enumerate(speed_list):
            speed_list[index] = value * multiplier
        return speed_list
    
    def get_angles_count(self, robot_data:RobotData) -> int:
        url = f"https://{self._host}:{str(self._port)}/GetRobotAnglesCount"
        data = {
            "robot": robot_data.name,
            "token": self._token
        }
        response = requests.post(url, verify=True, json=data).json()["data"]
        return response
        
    def check_emergency(self, robot_data:RobotData) -> bool:
        if TRAJECTORY_SEND_SWITCH:
            url = f"https://{self._host}:{str(self._port)}/GetRobotEmergency"
            data = {
                "robot": robot_data.name,
                "token": self._token,
                "code": robot_data.code
            }
            response = requests.post(url, verify=True, json=data).json()["data"]
            return response
        return False

    def set_robot_position(self, robot_data:RobotData, angles:Union[AnglePos, list[AnglePos]], is_multi_point:bool=False, last_point_position:Union[XYZPos, None]=None) -> dict:
        # Set position
        url = f"https://{self._host}:{str(self._port)}/CurentPosition"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code" : robot_data.code
            }
        if not is_multi_point:
            data["angles"] = angles.export_to(export_type=dict)
        else:
            converted_angles = []
            for angle in angles:
                converted_angles.append(angle.export_to(export_type=dict))
            data["angles_data"] = str(converted_angles)
        if last_point_position is not None:
            self.last_point_position = last_point_position
        request_data = requests.post(url, verify=True, json=data)
        return request_data.json(), request_data.status_code
    
    def set_robot_speed(self, robot_data:RobotData, angles_speed:Union[AnglePos, list[AnglePos]], is_multi_point:bool=False) -> dict:
        # Set motor speed
        url = f"https://{self._host}:{str(self._port)}/CurentSpeed"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code" : robot_data.code
            }
        if not is_multi_point:
            data["angles"] = angles_speed.export_to(export_type=dict)
        else:
            data["angles_data"] = angles_speed
            converted_speeds = []
            for angle_speed in angles_speed:
                converted_speeds.append(angle_speed.export_to(export_type=dict))
            data["angles_data"] = str(converted_speeds)
        request_data = requests.post(url, verify=True, json=data)
        return request_data.json(), request_data.status_code
        
    def move_xyz(self, robot_data:RobotData, position:XYZPos) -> dict:
        url = f"https://{self._host}:{str(self._port)}/Move_XYZ"
        data = {
            "robot": robot_data.name,
            "x": position.x,
            "y": position.y,
            "z": position.z,
            "a": position.a,
            "b": position.b,
            "c": position.c,
            "token": self._token,
            "code" : robot_data.code
            }
        response = requests.post(url, verify=True, json=data)
        return ReturnData(responce=response.text, code=response.status_code, trjectory=position)

    def xyz_to_angle(self, robot_data:RobotData, positions:Union[XYZPos, list[XYZPos]], is_multi_point:bool=False) -> Union[AnglePos, list[AnglePos]]:
        new_positions = []
        if isinstance(positions, list):
            for pos in positions:
                new_positions.append(pos.export_to(export_type=list))
        else:
            new_positions.append(positions.export_to(export_type=list))
            
        url = f"https://{self._host}:{str(self._port)}/XYZ_to_angle"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code" : robot_data.code,
            "positions_data": new_positions
            }
        result = requests.post(url, verify=True, json=data).json()["data"]
        if not is_multi_point:
            return AnglePos().from_dict(result[0], rewrite=True)
        else:
            angles:list[AnglePos] = []
            for res in result:
                angles.append(AnglePos().from_dict(res))
            return angles

    def angle_to_xyz(self, robot_data:RobotData, angles:list[AnglePos], is_multi_point:bool=False) -> dict:
        new_angles = []
        for angle_pos in angles:
            new_angles.append(angle_pos.export_to(export_type=list))
            
        url = f"https://{self._host}:{str(self._port)}/angle_to_xyz"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code" : robot_data.code,
            "angles_data": new_angles
            }
        result = requests.post(url, verify=True, json=data).json()["data"]
        if not is_multi_point:
            return XYZPos().from_dict(result[0], rewrite=True)
        else:
            positions:list[XYZPos] = []
            for res in result:
                positions.append(XYZPos().from_dict(res))
            return positions
    
    @staticmethod
    def calculate_speed(start_angles:AnglePos, end_angles:AnglePos, steps:int) -> list:
        start_angles = start_angles.export_to(list)
        end_angles = end_angles.export_to(list)
        # pprint.pprint(start_angles)
        # pprint.pprint(end_angles)
        # Проверка на совпадение размеров списков
        if len(start_angles) != len(end_angles):
            raise ValueError("Списки начальных и конечных углов должны иметь одинаковую длину")
        # Инициализация списка скоростей
        speeds = []
        # Цикл по элементам списков углов
        for i in range(len(start_angles)):
            # Вычисление разницы между начальным и конечным углом для каждого сервомотора
            if isinstance(end_angles[i], (float, int)):
                angle_diff = end_angles[i] - start_angles[i]
                # Вычисление скорости вращения для каждого сервомотора
                speed = angle_diff / steps  # steps - количество шагов
                # Добавление скорости вращения в список
                speeds.append(abs(speed))
        return speeds

    def ptp(self, robot_data:RobotData, angles:AnglePos, step_count:int=100) -> ReturnData:
        url = f"https://{self._host}:{str(self._port)}/GetCurentPosition"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code": robot_data.code
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

    
    def lin(self, robot_data:RobotData, end_point:XYZPos, num_points:int=25, triggers:dict=None, speed_multiplier:int=1, start:XYZPos=None, lin_step_count:int=25) -> ReturnData:
        if start is None:
            if TRAJECTORY_SEND_SWITCH:
                url = f"https://{self._host}:{str(self._port)}/GetXYZPosition"
                data = {
                    "robot": robot_data.name,
                    "token": self._token
                    }
                responce_data = requests.post(url, verify=True, json=data).json()["data"]
                start = XYZPos().from_dict(responce_data)
            else:
                if self.last_point_position is not None:
                    start = self.last_point_position
                else:
                    start = XYZPos().from_list([0, 0, 0])
        
        arc_points = []
        if end_point.smooth_endPoint is None:
            full_trajectory_points = TrajectoryConstructor().generate_line_points(start, end_point, num_points)
            
        else:
            cartesian_points = []
            updating_end_point = end_point
            cartesian_points = TrajectoryConstructor().find_smoothing_points(updating_end_point, cartesian_points)
            
            # Create trajectory
            updating_start_point = start
            full_trajectory_points = [start]
            full_trajectory_points = TrajectoryConstructor().smooth_trajectory(robot_data, full_trajectory_points, cartesian_points, updating_start_point, lin_step_count)
            
        # Setting triggers in trajectory
        if triggers is not None:
            for trigger_id in triggers.keys():
                full_trajectory_points = TrajectoryConstructor().set_trigger_point_in_trajectory(full_trajectory_points, \
                    triggers[trigger_id], trigger_id)[2]

        self.last_point_position = full_trajectory_points[-1]
            
        if TRAJECTORY_SEND_SWITCH:
            arc_points = self.xyz_to_angle(robot_data, full_trajectory_points, is_multi_point=True)
            # Set send parameter from xyz point to angle point
            for index, point in enumerate(full_trajectory_points):
                arc_points[index]["send"] = point.send
            
            new_speeds:list = []
            for index, point in enumerate(arc_points):
                old_point:AnglePos = None
                if index == 0:
                    url = f"https://{self._host}:{str(self._port)}/GetCurentPosition"
                    data = {
                        "robot": robot_data.name,
                        "token": self._token
                        }
                    current_angles = requests.post(url, verify=True, json=data).json()["data"]
                    if isinstance(current_angles, list):
                        old_point = AnglePos().from_dict(current_angles[-1])
                    else:
                        old_point = AnglePos().from_dict(current_angles)
                else:
                    old_point = arc_points[index-1]

                speed = self._speed_multiplier(self.calculate_speed(old_point, point, lin_step_count), speed_multiplier)
                new_speeds.append(AnglePos(use_send=False).from_list(speed))
            
            position_responce, pos_code = self.set_robot_position(robot_data, arc_points, is_multi_point=True)
            speed_responce, speed_code = self.set_robot_speed(robot_data, new_speeds, is_multi_point=True)
            
            response_data = {"Set position": position_responce,
                            "Set speed": speed_responce}
            response_codes = {"Set position": pos_code,
                            "Set speed": speed_code}
            return ReturnData(responce=response_data, code=response_codes, trjectory=full_trajectory_points)
        else:
            return ReturnData(responce=None, code=None, trjectory=full_trajectory_points)

    def circ(self, robot_data:RobotData, points_xyz:list[XYZPos], count_points:int=50, triggers:dict=None, arc_angle:float=None, speed_multiplier:float=1, lin_step_count:int=10) -> ReturnData:
        if not self.check_emergency(robot_data):
            if arc_angle is not None:
                if arc_angle < 18:
                    raise ValueError("Arc angle must be greater than 18 degrees.")
            
            if points_xyz[2].smooth_endPoint is None:
                coords, _start_smooth_point, _start_smoothing_point = TrajectoryConstructor().generate_arc_3d(
                    points_xyz[0],
                    points_xyz[1],
                    points_xyz[2],
                    count_points,
                    arc_angle=arc_angle
                    )
                full_trajectory_points = coords
            else:
                points_xyz[2].circ_angle = arc_angle
                # Find smoothing points
                cartesian_points = [points_xyz]
                updating_end_point:Union[list[XYZPos], XYZPos] = points_xyz
                cartesian_points = TrajectoryConstructor().find_smoothing_points(updating_end_point, cartesian_points)
                # Create trajectory
                updating_start_point = points_xyz[0]
                full_trajectory_points = [points_xyz[0]]
                full_trajectory_points = TrajectoryConstructor().smooth_trajectory(robot_data, full_trajectory_points, cartesian_points, updating_start_point, count_points)
              
            # Setting triggers in trajectory
            if triggers is not None:
                for trigger_id in triggers.keys():
                    full_trajectory_points = TrajectoryConstructor().set_trigger_point_in_trajectory(full_trajectory_points, \
                        triggers[trigger_id], trigger_id)[2]
              
            self.last_point_position = full_trajectory_points[-1]
            
            if TRAJECTORY_SEND_SWITCH:            
                arc_points = self.xyz_to_angle(robot_data, full_trajectory_points, is_multi_point=True)
                # Set send parameter from xyz point to angle point
                for index, point in enumerate(full_trajectory_points):
                    arc_points[index]["send"] = point.send
                    
                new_speeds:list = []
                for index, point in enumerate(arc_points):
                    old_point:list = []
                    if index == 0:
                        url = f"https://{self._host}:{str(self._port)}/GetCurentPosition"
                        data = {
                            "robot": robot_data.name,
                            "token": self._token
                            }
                        current_angles = requests.post(url, verify=True, json=data).json()["data"]
                        
                        if isinstance(current_angles, list):
                            old_point = AnglePos().from_dict(current_angles[-1])
                        else:
                            old_point = AnglePos().from_dict(current_angles)
                    else:
                        old_point = arc_points[index-1]

                    speed = self._speed_multiplier(self.calculate_speed(old_point, point, lin_step_count), speed_multiplier)
                    new_speeds.append(AnglePos(use_send=False).from_list(speed))
                    
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
            

    def get_robot_log(self, robot_data:RobotData, timestamp:int=None) -> dict:
        url = f"https://{self._host}:{str(self._port)}/GetRobotLogs"
        data = {
            "robot": robot_data.name,
            "token": self._token
            }
        if timestamp is not None:
            data["timestamp"] = timestamp
        return requests.post(url, verify=True, json=data).json()

    # cut out due to unnecessary reasons
    # def get_last_log(self, robot_data:RobotData) -> dict:
    #     url = f"https://{self._host}:{str(self._port)}/GetRobotLogs"
    #     data = {
    #         "robot": robot_data.name,
    #         "token": self._token
    #         }
    #     return requests.post(url, verify=True, json=data).json()["data"][-1]
    
    def debug(self, robot_data:RobotData, text:str) -> dict:
        url = f"https://{self._host}:{str(self._port)}/AddRobotLog"
        data = {
            "robot": robot_data.name,
            "text": text
            }
        return requests.post(url, verify=True, json=data).json()
    
    def set_program(self, robot_data:RobotData, program:str) -> dict:
        url = f"https://{self._host}:{str(self._port)}/SetProgram"
        data = {
            "robot": robot_data.name,
            "program": program.encode().hex(),
            "token": self._token,
            "code" : robot_data.code
            }
        return requests.post(url, verify=True, json=data).json()
    
    def delete_program(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{str(self._port)}/DeleteProgram"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code" : robot_data.code
            }
        return requests.post(url, verify=True, json=data).json()
    
    def get_position_id(self, robot_data:RobotData) -> dict:
        url = f"https://{self._host}:{str(self._port)}/GetPositionID"
        data = {
            "robot": robot_data.name,
            "token": self._token
            }
        return requests.post(url, verify=True, json=data).json()
    
    def set_position_id(self, robot_data:RobotData, position_id: int) -> dict:
        url = f"https://{self._host}:{str(self._port)}/SetPositionID"
        data = {
            "robot": robot_data.name,
            "token": self._token,
            "code" : robot_data.code,
            "id" : position_id 
            }
        return requests.post(url, verify=True, json=data).json()