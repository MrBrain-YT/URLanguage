from typing import Union
import math

import numpy as np
from scipy.interpolate import CubicSpline

from data_types import XYZPos, RobotData, Spline

class TrajectoryConstructor:
    
    @staticmethod
    def point_between(start_point: XYZPos, end_point: XYZPos, percentage:int):
        """
        Вычисляет точку между двумя заданными точками на заданном расстоянии в процентах.

        Args:
            start_point: Координаты начальной точки.
            end_point: Координаты конечной точки.
            percentage: Расстояние от начальной точки в процентах (от 0 до 100).

        Returns:
            Координаты точки, находящейся на заданном расстоянии от начальной точки.
            Возвращает None, если percentage не находится в диапазоне от 0 до 100.
        """
        # Convert from XYZPos to list
        start_point = start_point.export_to(export_type=list)
        end_point = end_point.export_to(export_type=list)
        
        # if not 0 <= percentage <= 100:
        #     return None  # Проверка на допустимый процент

        # Преобразуем процент в дробь
        fraction = percentage / 100.0

        # Убедимся, что точки имеют одинаковую размерность
        if len(start_point) != len(end_point):
            raise ValueError("Начальная и конечная точки должны иметь одинаковую размерность.")

        # Вычисляем координаты промежуточной точки
        result = []
        for i in range(len(start_point)):
            result.append(start_point[i] + (end_point[i] - start_point[i]) * fraction)

        return XYZPos.from_list(result)
    
    @staticmethod
    def normalize(v):
        norm = np.linalg.norm(v)
        if norm == 0: 
            return v
        return v / norm

    # Функция для вычисления точки на биссектрисе угла ACB
    def bisector_point(self, A, B, C, distance, distanse_multiplier):
        # Векторы от C к A и от C к B
        vector_CA = A - C
        vector_CB = B - C
        
        # Нормализуем векторы
        norm_CA = self.normalize(vector_CA)
        norm_CB = self.normalize(vector_CB)
        
        # Биссектриса будет равна нормализованной сумме этих векторов
        bisector = self.normalize(norm_CA + norm_CB)
        
        # Точка на биссектрисе на расстоянии distance / distanse_delimitr от точки C
        point_on_bisector = C + bisector * (distance * distanse_multiplier)
        return point_on_bisector
    

    # Функция для вычисления точек на отрезках на расстоянии distance от точки C
    def points_on_segments(self, A, B, C, distance):
        # Вектор от C к A и от C к B
        vector_CA = A - C
        vector_CB = B - C
        
        # Нормализуем векторы
        norm_CA = self.normalize(vector_CA)
        norm_CB = self.normalize(vector_CB)
        
        # Точки на отрезках на расстоянии distance от точки C
        point_A_dist = C + norm_CA * distance
        point_B_dist = C + norm_CB * distance
        
        return point_A_dist, point_B_dist

    # Функция для построения плавной кривой с использованием сплайна
    @staticmethod
    def spline_arc(center, start_point, end_point, num_points:int):
        # Вычисляем контрольные точки для сплайна (начальная точка, центр и конечная точка)
        points = np.array([start_point, center, end_point])
        
        # Создаем параметры для сплайна (индексы точек)
        t = np.array([0, 0.5, 1])  # Интерполяционные параметры
        
        # Создаем кубический сплайн для интерполяции по осям x, y и z
        spline_x = CubicSpline(t, points[:, 0])
        spline_y = CubicSpline(t, points[:, 1])
        spline_z = CubicSpline(t, points[:, 2])
        
        # Генерируем новые точки для сплайна
        t_new = np.linspace(0, 1, num_points)
        smoothed_arc_points = np.vstack([spline_x(t_new), spline_y(t_new), spline_z(t_new)]).T
        
        return smoothed_arc_points

    def get_smothed_arc_points(self, current_robot_position:XYZPos, target_point:XYZPos, num_points:int=25) -> list[XYZPos]:
        A = np.array(current_robot_position.export_to(export_type=list))  # Точка A (start point)
        B = np.array(target_point.smooth_endPoint.export_to(export_type=list))  # Точка B (end point)
        C = np.array(target_point.export_to(export_type=list))  # Точка C (angle point)

        distance = target_point.smooth_distance  # Расстояние, на которое сдвигаются точки
        # Находим точку на биссектрисе на расстоянии distance / 3 от точки C
        bisector = self.bisector_point(A, B, C, distance, 0.33)
        # Находим точки на отрезках на расстоянии distance от угла
        point_A_dist, point_B_dist = self.points_on_segments(A, B, C, distance)
        # Строим дугу с использованием сплайна через точку на биссектрисе
        smoothed_arc_points = self.spline_arc(bisector, point_A_dist, point_B_dist, num_points=num_points)
        converted_points = []
        for point in smoothed_arc_points:
            converted_points.append(XYZPos.from_list(point))
            
        if target_point.smooth_endPoint.smooth_endPoint is None:
            converted_points.append(target_point.smooth_endPoint)
        return converted_points
    
    @staticmethod
    def circle_center(p1, p2, p3):
        """
        Вычисляет центр и радиус окружности, проходящей через три точки в 3D-пространстве.
        """
        A, B, C = np.array(p1), np.array(p2), np.array(p3)

        # Векторы между точками
        AB = B - A
        AC = C - A

        # Векторное произведение — нормаль к плоскости
        normal = np.cross(AB, AC)
        normal = normal / np.linalg.norm(normal)  # Нормализация

        # Средние точки отрезков AB и AC
        mid_AB = (A + B) / 2
        mid_AC = (A + C) / 2

        # Вектора, перпендикулярные к AB и AC в плоскости
        perp_AB = np.cross(normal, AB)
        perp_AC = np.cross(normal, AC)

        # Решаем систему уравнений для пересечения серединных перпендикуляров
        A_matrix = np.array([perp_AB, -perp_AC]).T
        b_vector = mid_AC - mid_AB

        t = np.linalg.lstsq(A_matrix, b_vector, rcond=None)[0]
        center = mid_AB + t[0] * perp_AB

        # Радиус окружности
        radius = np.linalg.norm(center - A)

        return center, radius, normal
    
    @staticmethod
    def distance_between_points(point1: XYZPos, point2: XYZPos) -> float:
        """
        Вычисляет расстояние между двумя точками в 3D-пространстве.

        Args:
            point1: Первая точка.
            point2: Вторая точка.

        Returns:
            Расстояние между точками.
        """
        # Convert points to numpy arrays
        p1 = np.array(point1.export_to(export_type=list))
        p2 = np.array(point2.export_to(export_type=list))
        
        # Calculate the Euclidean distance
        distance = np.linalg.norm(p1 - p2)
        
        return distance

    def generate_arc_points(self, start_point:XYZPos, middle_point:XYZPos, end_point:XYZPos, num_points:int=25, distance:int=None, arc_angle:float=None, circles_count:int=0, is_check:Union[None, bool]=False, rebuild:bool=False):
        """
        Генерирует `num_points` точек на дуге, проходящей через три заданные точки.
        """
        if distance is None:
            distance = end_point.smooth_distance
            
        start_arc_angle = arc_angle
            
        # test generate arc points
        if is_check is not None:
            if not is_check:
                elements = self.generate_arc_points(
                    start_point,
                    middle_point,
                    end_point,
                    num_points,
                    distance,
                    arc_angle,
                    circles_count=0,
                    is_check=True
                    )
                
                if len(elements) == 2:
                    if elements[1] == 1:
                        return elements[0][0], elements[0][1], elements[0][2], elements[0][3]
        
        smooth_arc_angle = arc_angle + 2 if arc_angle is not None else None

        converted_start_point = start_point.export_to(export_type=list)
        converted_middle_point = middle_point.export_to(export_type=list)
        converted_end_point = end_point.export_to(export_type=list)

        center, radius, normal = self.circle_center(converted_start_point, converted_middle_point, converted_end_point)

        # Векторы от центра к точкам
        v1 = np.array(converted_start_point) - center
        v3 = np.array(converted_end_point) - center
        # Если угол окружности не задан, вычисляем его по точкам
        if arc_angle is None:
            
            arc_angle = np.arctan2(np.linalg.norm(np.cross(v1, v3)), np.dot(v1, v3))
            # Проверяем направление угла с учетом нормали
            if np.dot(normal, np.cross(v1, v3)) < 0:
                arc_angle = 2 * np.pi - arc_angle
                if rebuild:
                    arc_angle -= 2 * np.pi
                    # arc_angle = -arc_angle
                
                arc_angle += (360 * circles_count) * (math.pi / 180)
            elif np.dot(normal, np.cross(v1, v3)) > 0:
                arc_angle += (360 * circles_count) * (math.pi / 180)

        else:
            arc_angle = arc_angle * (math.pi / 180)

        # Ось вращения - нормаль к плоскости
        axis = normal / np.linalg.norm(normal)

        # Генерируем углы поворота
        angles = np.linspace(0, arc_angle, num_points)

        # Функция вращения вектора вокруг оси
        def rotate_vector(v, axis, theta):
            """
            Вращает вектор v вокруг оси axis на угол theta (радианы).
            """
            axis = axis / np.linalg.norm(axis)
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            return (v * cos_theta +
                    np.cross(axis, v) * sin_theta +
                    axis * np.dot(axis, v) * (1 - cos_theta))

        # Генерируем точки дуги
        arc_points = [center + rotate_vector(v1, axis, theta) for theta in angles]
        # Генерируем точки дуги для сглаживания
        if smooth_arc_angle is None:
            smooth_arc_points = arc_points
        else:
            smooth_angles = np.linspace(0, smooth_arc_angle * (math.pi /180), num_points)
            smooth_arc_points = [center + rotate_vector(v1, axis, theta) for theta in smooth_angles]

        # Длина всей дуги
        arc_length = radius * arc_angle  

        # Обрабатываем запрос точки от конца
        target_point_from_end = None
        if distance is not None:
            target_length = arc_length - distance  # Длина от начала до искомой точки
            if target_length < 0:
                # print("Ошибка: расстояние больше длины дуги, возвращаем начальную точку.")
                target_point_from_end = XYZPos().from_list(arc_points[0])
            else:
                target_angle = (target_length / arc_length) * arc_angle
                target_point_from_end = XYZPos().from_list(center + rotate_vector(v1, axis, target_angle))

        # Обрабатываем запрос точки от начала
        target_point_from_start = None
        if distance is not None:
            if distance > arc_length:
                # print("Ошибка: расстояние больше длины дуги, возвращаем конечную точку.")
                target_point_from_start = XYZPos().from_list(arc_points[-1])
            else:
                target_angle = (distance / arc_length) * arc_angle
                target_point_from_start = XYZPos().from_list(center + rotate_vector(v1, axis, target_angle))

        if is_check and start_arc_angle is None:
            two_point = XYZPos().from_list(arc_points[2])
            one_distance = self.distance_between_points(start_point, middle_point)
            two_distance = self.distance_between_points(two_point, middle_point)
            # TODO: repaire circles count
            if one_distance < two_distance:
                return self.generate_arc_points(start_point, middle_point, end_point, num_points, distance, start_arc_angle, circles_count=0, is_check=None, rebuild=True), 1

        return arc_points, target_point_from_end, target_point_from_start, smooth_arc_points
    
    @staticmethod
    def point_on_trajectory(start_point: XYZPos, end_point: XYZPos, distance:float):
        """
        Находит точку на прямой между p1 и p2, находящуюся на заданном расстоянии от p1.
        
        :param start_point: XYZPos, координаты первой точки
        :param end_point: XYZPos, координаты второй точки
        :param distance: float, расстояние от start_point до искомой точки
        :return: XYZPos - координаты найденной точки
        """
        start_point = np.array(start_point.export_to(export_type=list))
        end_point = np.array(end_point.export_to(export_type=list))
        direction = end_point - start_point  # Вектор направления
        length = np.linalg.norm(direction)  # Длина вектора
        
        if length == 0:
            raise ValueError("Точки совпадают, направление неопределено")
        
        direction = direction / length  # Нормализация вектора
        new_point = list(start_point + direction * distance)  # Вычисление новой точки
        
        return XYZPos.from_list(new_point)
    
    @staticmethod
    def find_smoothing_points(updating_end_point: Union[list, XYZPos], cartesian_points: list[XYZPos]) -> list[XYZPos]:
        while True:
            if isinstance(updating_end_point, list):
                if isinstance(updating_end_point[2].smooth_endPoint, list):
                    if updating_end_point[2].smooth_endPoint[2].smooth_endPoint is None:
                        break
                else:
                    if updating_end_point[2].smooth_endPoint.smooth_endPoint is None:
                        break
            elif isinstance(updating_end_point, XYZPos):
                if isinstance(updating_end_point.smooth_endPoint, list):
                    if updating_end_point.smooth_endPoint[2].smooth_endPoint is None:
                        cartesian_points.append(updating_end_point)
                        break
                else:
                    if updating_end_point.smooth_endPoint.smooth_endPoint is None:
                        cartesian_points.append(updating_end_point)
                        break
                    
            if isinstance(updating_end_point, list):
                """Smoothing from CIRC"""
                if isinstance(updating_end_point[2].smooth_endPoint, list):
                    # Smooth to CIRC trajectory
                    updating_end_point = updating_end_point[2].smooth_endPoint
                    # cartesian_points.append(updating_end_point)
                elif isinstance(updating_end_point[2].smooth_endPoint, XYZPos):
                    # Smooth to LIN trajectory
                    updating_end_point = updating_end_point[2].smooth_endPoint
                    # cartesian_points.append(updating_end_point)
            elif isinstance(updating_end_point, XYZPos):
                """Smoothing from LIN"""
                if isinstance(updating_end_point.smooth_endPoint, list):
                    # Smooth to CIRC trajectory
                    cartesian_points.append(updating_end_point)
                    updating_end_point = updating_end_point.smooth_endPoint
                elif isinstance(updating_end_point.smooth_endPoint, XYZPos):
                    # Smooth to LIN trajectory
                    cartesian_points.append(updating_end_point)
                    updating_end_point = updating_end_point.smooth_endPoint

        return cartesian_points
    
    def smooth_trajectory(self, robot_data: RobotData, full_trajectory_points: list[XYZPos], cartesian_points: list[XYZPos], updating_start_point: XYZPos, count_points: int) -> list[XYZPos]:
        for point in cartesian_points:
            if isinstance(point, XYZPos):
                if isinstance(point.smooth_endPoint, XYZPos):
                    # LIN to LIN
                    smoothed_arc_points = self.get_smothed_arc_points(updating_start_point, point)
                    full_trajectory_points += smoothed_arc_points
                    updating_start_point = smoothed_arc_points[-1]
                else:
                    # LIN to CIRC
                    # Find smooth distance end LIN point
                    end_smoothing_point = self.point_on_trajectory(point, full_trajectory_points[-1], point.smooth_distance)
                    # Find smooth distance start CIRC point
                    _coords, _end_smoothing_point, start_smoothing_point, _smooth_arc_points = self.generate_arc_points(
                        point.smooth_endPoint[0],
                        point.smooth_endPoint[1],
                        point.smooth_endPoint[2],
                        count_points,
                        distance=point.smooth_distance,
                        arc_angle=point.smooth_endPoint[2].circ_angle
                        )
                    
                    # Find middle spline point
                    A = np.array(end_smoothing_point.export_to(list))
                    C = np.array(point.export_to(list))
                    B = np.array(start_smoothing_point.export_to(list))
                    middle_spline_point = XYZPos.from_list(self.bisector_point(A, B, C, point.smooth_endPoint[2].smooth_distance, 2).tolist())
                    
                    # Add LIN trajectory to full trajectory
                    full_trajectory_points.append(end_smoothing_point)
                    
                    # Create smoothed trajectory
                    smoothed_trajectory = Spline(robot_data, system=self).add_point(end_smoothing_point, middle_spline_point, start_smoothing_point, start_smoothing_point)._create_catmull_rom_spline_points()
                    
                    # Create new CIRC trajectory
                    circles_count = point.smooth_endPoint[2].circ_angle // 360 if point.smooth_endPoint[2].circ_angle is not None else 0
                    circ_coords, _end_smoothing_point, _start_smoothing_point, _smooth_arc_points = self.generate_arc_points(
                        start_smoothing_point,
                        point.smooth_endPoint[1],
                        point.smooth_endPoint[2],
                        count_points,
                        circles_count=circles_count
                        )
                    
                    full_trajectory_points += smoothed_trajectory
                    full_trajectory_points.extend([XYZPos.from_list(cord) for cord in circ_coords])
                    
            elif isinstance(point, list):
                if isinstance(point[2].smooth_endPoint, XYZPos):
                    # CIRC to LIN
                    # Find smooth distance start CIRC point
                    if point[2].circ_angle < 18:
                        raise ValueError("Arc angle must be greater than 18 degrees.")
                    _coords, end_smoothing_point, _start_smoothing_point, smooth_arc_points = self.generate_arc_points(
                        point[0],
                        point[1],
                        point[2],
                        count_points,
                        arc_angle=point[2].circ_angle
                        )
                    
                    # Find smooth distance start LIN point
                    end_circ_point = XYZPos().from_list(smooth_arc_points[-1].tolist())
                    start_smoothing_point = self.point_on_trajectory(end_circ_point, point[2].smooth_endPoint, point[2].smooth_distance)
                    
                    # Find middle spline point
                    A = np.array(end_smoothing_point.export_to(list))
                    C = np.array(smooth_arc_points[-1].tolist())
                    B = np.array(start_smoothing_point.export_to(list))
                    middle_spline_point = XYZPos.from_list(self.bisector_point(A, B, C, point[2].smooth_distance, 0.33).tolist())
                    
                    # Create new CIRC trajectory
                    circles_count = point[2].circ_angle // 360 if point[2].circ_angle is not None else 0
                    circ_coords, _start_smooth_point, _start_smoothing_point, _smooth_arc_points = self.generate_arc_points(
                        point[0],
                        point[1],
                        end_smoothing_point,
                        count_points,
                        circles_count=circles_count
                        )
                    smoothed_trajectory = Spline(robot_data, system=self).add_point(end_smoothing_point, middle_spline_point, start_smoothing_point, start_smoothing_point)._create_catmull_rom_spline_points()
                    full_trajectory_points.extend([XYZPos.from_list(cord) for cord in circ_coords])
                    full_trajectory_points += smoothed_trajectory
                    if point[2].smooth_endPoint.smooth_endPoint is None:
                        full_trajectory_points.append(point[2].smooth_endPoint)
                else:
                    # CIRC to CIRC
                    # Find smooth distance end CIRC point
                    if point[2].circ_angle < 18:
                        raise ValueError("Arc in one angle must be greater than 18 degrees.")
                    _coords, end_smoothing_point, _start_smoothing_point, _smooth_arc_points = self.generate_arc_points(
                        point[0],
                        point[1],
                        point[2],
                        count_points,
                        arc_angle=point[2].circ_angle
                        )
                    # Find smooth distance start CIRC point
                    new_movement = point[2].smooth_endPoint
                    if new_movement[2].circ_angle < 18:
                        raise ValueError("Arc in two angle must be greater than 18 degrees.")
                    _coords, _end_smoothing_point, start_smoothing_point, _smooth_arc_points = self.generate_arc_points(
                        new_movement[0],
                        new_movement[1],
                        new_movement[2],
                        count_points,
                        distance=point[2].smooth_distance,
                        arc_angle=new_movement[2].circ_angle
                        )
                    
                    # Find middle spline point
                    middle_spline_point = self.point_between(new_movement[0], end_smoothing_point, 50)
                    
                    # Create new 1 CIRC trajectory
                    circles_count1 = point[2].circ_angle // 360 if point[2].circ_angle is not None else 0
                    circ_coords1, _end_smoothing_point, _start_smoothing_point, _smooth_arc_points = self.generate_arc_points(
                        point[0],
                        point[1],
                        end_smoothing_point,
                        count_points,
                        circles_count=circles_count1
                        )
                    full_trajectory_points.extend([XYZPos.from_list(cord) for cord in circ_coords1])
                    # Create new 2 CIRC trajectory
                    circles_count2 = new_movement[2].circ_angle // 360 if new_movement[2].circ_angle is not None else 0 # TODO: use circles_count2
                    circ_coords2, _end_smoothing_point, _start_smoothing_point, _smooth_arc_points = self.generate_arc_points(
                        start_smoothing_point,
                        new_movement[1],
                        new_movement[2],
                        count_points,
                        arc_angle=new_movement[2].circ_angle
                        )
                    # Create smoothed trajectory
                    smoothed_trajectory = Spline(robot_data, system=self).add_point(end_smoothing_point, middle_spline_point, start_smoothing_point, start_smoothing_point)._create_catmull_rom_spline_points()
                    full_trajectory_points += smoothed_trajectory
                    full_trajectory_points.extend([XYZPos.from_list(cord) for cord in circ_coords2])

        return full_trajectory_points