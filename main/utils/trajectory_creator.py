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
    def bisector_point(self, A, B, C, distance, distance_multiplier):
        # Векторы от C к A и от C к B
        vector_CA = A - C
        vector_CB = B - C
        
        # Нормализуем векторы
        norm_CA = self.normalize(vector_CA)
        norm_CB = self.normalize(vector_CB)
        
        # Биссектриса будет равна нормализованной сумме этих векторов
        bisector = self.normalize(norm_CA + norm_CB)
        
        # Точка на биссектрисе на расстоянии distance * distance_multiplier от точки C
        point_on_bisector = C + bisector * (distance * distance_multiplier)
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
    
    @staticmethod
    def circle_center(p1, p2, p3):
        """
        Вычисляет центр и радиус окружности, проходящей через три точки в 3D-пространстве.
        """
        p1, p2, p3 = np.array(p1, dtype=np.float64), np.array(p2, dtype=np.float64), np.array(p3, dtype=np.float64)
    
        # Векторы, образующие плоскость
        v1 = p2 - p1
        v2 = p3 - p1
        
        # Нахождение нормали плоскости
        normal = np.cross(v1, v2)
        normal /= np.linalg.norm(normal)
        
        # Середина между p1 и p3
        mid = (p1 + p3) / 2
        
        # Направляющие векторы серединных перпендикуляров
        perp1 = np.cross(v1, normal)
        perp2 = np.cross(v2, normal)
        
        # Решаем систему уравнений для нахождения центра окружности
        A = np.vstack((perp1, -perp2)).T
        B = mid - (p1 + p2) / 2
        t = np.linalg.lstsq(A, B, rcond=None)[0][0]
        center = (p1 + p2) / 2 + t * perp1
        
        # Радиус окружности
        radius = np.linalg.norm(center - p1)
        
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
        
    def generate_arc_3d(self, start_point: XYZPos, middle_point: XYZPos, end_point: XYZPos, num_points: int = 25, distance: int = None, arc_angle: float = None):
        arc_angle_start = arc_angle
        # Поиск дельты углов ABC
        if arc_angle is None:
            if num_points % 2 != 0:
                num_points += 1
            a_delta_1 = -(start_point.a - middle_point.a)
            a_delta_2 = -(middle_point.a - end_point.a)
            b_delta_1 = -(start_point.b - middle_point.b)
            b_delta_2 = -(middle_point.b - end_point.b)
            c_delta_1 = -(start_point.c - middle_point.c)
            c_delta_2 = -(middle_point.c - end_point.c)
            # Поиск угла на 1 шаг для первого отрезка
            a_step_1 = a_delta_1 / (num_points / 2)
            b_step_1 = b_delta_1 / (num_points / 2)
            c_step_1 = c_delta_1 / (num_points / 2)
            # Поиск угла на 1 шаг для второго отрезка
            a_step_2 = a_delta_2 / (num_points / 2)
            b_step_2 = b_delta_2 / (num_points / 2)
            c_step_2 = c_delta_2 / (num_points / 2)
        else:
            a_delta = -(start_point.a - middle_point.a)
            b_delta = -(middle_point.b - end_point.b)
            c_delta = -(start_point.c - middle_point.c)
            
            a_step = a_delta / num_points
            b_step = b_delta / num_points
            c_step = c_delta / num_points
            
        # Конвертируем точки в список для удобства
        converted_start_point = start_point.export_to(export_type=list)[0:3]
        converted_middle_point = middle_point.export_to(export_type=list)[0:3]
        converted_end_point = end_point.export_to(export_type=list)[0:3]
        
        p1 = np.array(converted_start_point)
        p2 = np.array(converted_middle_point)
        p3 = np.array(converted_end_point)
        center, radius, normal = self.circle_center(p1, p2, p3)
        
        # Векторы от центра к точкам
        v1 = np.array(p1) - center
        v3 = np.array(p3) - center
        
        if arc_angle_start is None:
            # Если угол не задан, вычисляем угол между p1 и p3
            arc_angle = np.degrees(np.arccos(np.dot(v1, v3) / (np.linalg.norm(v1) * np.linalg.norm(v3))))
        
        # Определяем угол дуги на основе параметра arc_angle (в радианах)
        theta_total = np.radians(arc_angle)  # Преобразуем угол в радианы
        theta = np.linspace(0, theta_total, num_points)
        
        # Ортонормированные базисные векторы в плоскости окружности
        u = v1 / np.linalg.norm(v1)
        w = np.cross(normal, u)

        if distance is not None:
            # Вычисляем координаты всех точек дуги
            arc_points = [XYZPos().from_list(coord) for coord in np.array([center + radius * (np.cos(t) * u + np.sin(t) * w) for t in theta]).tolist()]
            # Применяем шаги углов для каждой точки
            arc_points[0].a = start_point.a; arc_points[0].b = start_point.b; arc_points[0].c = start_point.c
            if arc_angle_start is None:
                # 1 отрезок
                for i in range(1, int(num_points/2) + 1):
                    arc_points[i].a = arc_points[i-1].a + a_step_1
                    arc_points[i].b = arc_points[i-1].b + b_step_1
                    arc_points[i].c = arc_points[i-1].c + c_step_1
                # 2 отрезок
                for i in range(int(num_points/2)+1, num_points):
                    arc_points[i].a = arc_points[i-1].a + a_step_2
                    arc_points[i].b = arc_points[i-1].b + b_step_2
                    arc_points[i].c = arc_points[i-1].c + c_step_2
            else:
                for i in range(1, num_points):
                    arc_points[i].a = arc_points[i-1].a + a_step
                    arc_points[i].b = arc_points[i-1].b + b_step
                    arc_points[i].c = arc_points[i-1].c + c_step
                
            # Длина дуги между двумя точками на окружности
            arc_length = radius * np.radians(arc_angle)
            
            # Вычисляем угол для целевой точки
            theta_end = np.radians((1 - distance / arc_length) * arc_angle)  # Угол для точки от конца
            theta_start = np.radians(distance / arc_length * arc_angle)  # Угол для точки от начала
            
            # Индекс точки на дуге, до которой нужно вычислить
            target_index = np.searchsorted(theta, theta_end)
            
            # Обрезаем список точек дуги до целевой точки
            arc_points = arc_points[:target_index]
            
            # Вычисляем точки на дуге на нужных расстояниях
            target_point_from_start = XYZPos().from_list(center + radius * (np.cos(theta_start) * u + np.sin(theta_start) * w))
            target_point_from_end = XYZPos().from_list(center + radius * (np.cos(theta_end) * u + np.sin(theta_end) * w))
            
            return arc_points, target_point_from_end, target_point_from_start
        
        else:
            # Если distance == None, возвращаем все точки до угла (arc_angle_calc)
            arc_points = [XYZPos().from_list(coord) for coord in np.array([center + radius * (np.cos(t) * u + np.sin(t) * w) for t in np.linspace(0, np.radians(arc_angle), num_points)])]
            if arc_angle_start is None:
                # 1 отрезок
                for i in range(1, int(num_points/2) + 1):
                    arc_points[i].a = arc_points[i-1].a + a_step_1
                    arc_points[i].b = arc_points[i-1].b + b_step_1
                    arc_points[i].c = arc_points[i-1].c + c_step_1
                # 2 отрезок
                for i in range(int(num_points/2)+1, num_points):
                    arc_points[i].a = arc_points[i-1].a + a_step_2
                    arc_points[i].b = arc_points[i-1].b + b_step_2
                    arc_points[i].c = arc_points[i-1].c + c_step_2
            else:
                for i in range(1, num_points):
                    arc_points[i].a = arc_points[i-1].a + a_step
                    arc_points[i].b = arc_points[i-1].b + b_step
                    arc_points[i].c = arc_points[i-1].c + c_step
            return arc_points, end_point, start_point

    
    def point_on_trajectory(self, start_point: XYZPos, end_point: XYZPos, distance:float):
        """
        Находит точку на прямой между p1 и p2, находящуюся на заданном расстоянии от p1.
        
        :param start_point: XYZPos, координаты первой точки
        :param end_point: XYZPos, координаты второй точки
        :param distance: float, расстояние от start_point до искомой точки
        :return: XYZPos - координаты найденной точки
        """
        getted_start_point = start_point
        a_delta = -(start_point.a - end_point.a)
        b_delta = -(start_point.b - end_point.b)
        c_delta = -(start_point.c - end_point.c)
        old_distance = self.distance_between_points(start_point, end_point)
        
        a_step = a_delta / old_distance
        b_step = b_delta / old_distance
        c_step = c_delta / old_distance
        
        a_new_delta = a_step * distance
        b_new_delta = b_step * distance
        c_new_delta = c_step * distance
        getted_start_point = start_point
        
        start_point = np.array(start_point.export_to(export_type=list))
        end_point = np.array(end_point.export_to(export_type=list))
        direction = end_point - start_point  # Вектор направления
        length = np.linalg.norm(direction)  # Длина вектора

        if length == 0:
            return getted_start_point
        
        direction = direction / length  # Нормализация вектора
        new_point = list(start_point + direction * distance)  # Вычисление новой точки
        new_point.extend([getted_start_point.a+a_new_delta, getted_start_point.b+b_new_delta, getted_start_point.c+c_new_delta])
        return XYZPos.from_list(new_point)
    
    @staticmethod
    def generate_line_points(start: XYZPos, end: XYZPos, num_points: int):
        """
        Generates a list of points located on a line between two given points,
        including smooth transition for position (x, y, z) and orientation (a, b, c).

        :param start: Start point with coordinates and orientation [x, y, z, a, b, c]
        :param end: End point with coordinates and orientation [x, y, z, a, b, c]
        :param num_points: Number of points to generate (must be >= 2)
        :return: List of XYZPos instances with interpolated positions and orientations
        """
        if num_points < 2:
            raise ValueError("The number of points must be at least 2.")

        # Получаем значения из start и end
        x1, y1, z1, a1, b1, c1 = start.export_to(list)
        x2, y2, z2, a2, b2, c2 = end.export_to(list)

        # Вычисляем шаги для координат и ориентации
        x_step = (x2 - x1) / (num_points - 1)
        y_step = (y2 - y1) / (num_points - 1)
        z_step = (z2 - z1) / (num_points - 1)
        a_step = (a2 - a1) / (num_points - 1)
        b_step = (b2 - b1) / (num_points - 1)
        c_step = (c2 - c1) / (num_points - 1)

        # Генерируем точки
        points = []
        for i in range(num_points):
            x = x1 + i * x_step
            y = y1 + i * y_step
            z = z1 + i * z_step
            a = a1 + i * a_step
            b = b1 + i * b_step
            c = c1 + i * c_step
            point = XYZPos().from_list([x, y, z, a, b, c])
            points.append(point)
        return points
    
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
                    start_smoothing_point = self.point_on_trajectory(point, full_trajectory_points[-1], point.smooth_distance)
                    end_smoothing_point = self.point_on_trajectory(point, point.smooth_endPoint, point.smooth_distance)
                    # Find middle spline point
                    A = np.array(end_smoothing_point.export_to(list)[0:3])
                    C = np.array(point.export_to(list)[0:3])
                    B = np.array(start_smoothing_point.export_to(list)[0:3])
                    middle_spline_point = XYZPos.from_list(self.bisector_point(A, B, C, point.smooth_distance, 0.3).tolist())
                    middle_spline_point.a = point.a; middle_spline_point.b = point.b; middle_spline_point.c = point.c
                    # Create smoothed trajectory
                    smoothed_arc_points = Spline(robot_data, system=self).add_point(start_smoothing_point, middle_spline_point, end_smoothing_point, end_smoothing_point)._create_catmull_rom_spline_points()
                    line_1 = self.generate_line_points(full_trajectory_points[-1], start_smoothing_point, count_points)
                    line_2 = self.generate_line_points(smoothed_arc_points[-1], point.smooth_endPoint, count_points)
                    full_trajectory_points.extend(line_1)
                    full_trajectory_points.extend(smoothed_arc_points)
                    if point.smooth_endPoint.smooth_endPoint is None:
                        full_trajectory_points.extend(line_2)
                    else:
                        pass
                else:
                    # LIN to CIRC
                    # Find smooth distance end LIN point
                    end_smoothing_point = self.point_on_trajectory(point, full_trajectory_points[-1], point.smooth_distance)
                    line_trajectory = self.generate_line_points(full_trajectory_points[-1], end_smoothing_point, count_points)
                    # Find smooth distance start CIRC point and create CIRC trajectory
                    circ_coords, _start_smoothing_point, _end_smoothing_point  = self.generate_arc_3d(
                        point.smooth_endPoint[0],
                        point.smooth_endPoint[1],
                        point.smooth_endPoint[2],
                        count_points,
                        distance=0,
                        arc_angle=point.smooth_endPoint[2].circ_angle
                        )

                    circ_coords, start_smoothing_point, _end_smoothing_point  = self.generate_arc_3d(
                        circ_coords[-1],
                        point.smooth_endPoint[1],
                        point.smooth_endPoint[0],
                        count_points,
                        distance=point.smooth_distance,
                        arc_angle=point.smooth_endPoint[2].circ_angle
                        )
                    circ_coords.reverse()
                        
                    # Find middle spline point
                    smoothed_angle_point = self.point_between(end_smoothing_point, point, 80)
                    A = np.array(end_smoothing_point.export_to(list))
                    C = np.array(smoothed_angle_point.export_to(list))
                    B = np.array(start_smoothing_point.export_to(list))
                    middle_spline_point = XYZPos.from_list(self.bisector_point(A, B, C, point.smooth_endPoint[2].smooth_distance, 1).tolist())
                    
                    # Add LIN trajectory to full trajectory
                    full_trajectory_points.extend(line_trajectory)
                    
                    # Find ABC angles
                    end_smoothing_point.a = point.a; end_smoothing_point.b = point.b; end_smoothing_point.c = point.c
                    if point.smooth_endPoint is not None:
                        a_delta = -(circ_coords[-1].a - point.smooth_endPoint[0].a) / 2
                        b_delta = -(circ_coords[-1].b - point.smooth_endPoint[0].b) / 2
                        c_delta = -(circ_coords[-1].c - point.smooth_endPoint[0].c) / 2
                    start_smoothing_point.a = circ_coords[0].a;\
                        start_smoothing_point.b = circ_coords[0].b; start_smoothing_point.c = circ_coords[0].c
                    middle_spline_point.a = end_smoothing_point.a + (a_delta / 2);\
                        middle_spline_point.b = end_smoothing_point.b + (b_delta / 2); middle_spline_point.c = end_smoothing_point.c + (c_delta / 2)
                    pre_start_smoothing_point = self.point_between(middle_spline_point, start_smoothing_point, 90)
                    # Create smoothed trajectory
                    smoothed_trajectory = Spline(robot_data, system=self).add_point(end_smoothing_point, middle_spline_point, \
                        pre_start_smoothing_point, start_smoothing_point)._create_catmull_rom_spline_points()
                    # Add smoothed and CIRC trajectory to full trajectory
                    full_trajectory_points.extend(smoothed_trajectory)
                    full_trajectory_points.extend([cord for cord in circ_coords])
                    
            elif isinstance(point, list):
                if isinstance(point[2].smooth_endPoint, XYZPos):
                    # CIRC to LIN
                    # Find smooth distance start CIRC point
                    if point[2].circ_angle is not None:
                        if point[2].circ_angle < 18:
                            raise ValueError("Arc angle must be greater than 18 degrees.")
                    coords, end_smoothing_point, _start_smoothing_point = self.generate_arc_3d(
                        point[0],
                        point[1],
                        point[2],
                        count_points,
                        distance=point[2].smooth_distance,
                        arc_angle=point[2].circ_angle
                        )
                    last_circ_point = coords[-1]
                    
                    smoothed_coords, _end_smoothing_point, _start_smoothing_point = self.generate_arc_3d(
                        point[0],
                        point[1],
                        point[2],
                        count_points,
                        distance=None,
                        arc_angle=point[2].circ_angle+5 if point[2].circ_angle is not None else None,
                        )
                    
                    # Find smooth distance start LIN point
                    end_circ_point = smoothed_coords[-1]
                    start_smoothing_point = self.point_on_trajectory(end_circ_point, point[2].smooth_endPoint, point[2].smooth_distance)
                    
                    # Find middle spline point
                    A = np.array(coords[-1].export_to(list))
                    C = np.array(smoothed_coords[-1].export_to(export_type=list))
                    B = np.array(start_smoothing_point.export_to(list))
                    middle_spline_point = XYZPos.from_list(self.bisector_point(A, B, C, point[2].smooth_distance, 0.33).tolist())
                    
                    end_smoothing_point.a = last_circ_point.a; end_smoothing_point.b = last_circ_point.b; end_smoothing_point.c = last_circ_point.c
                    if point[2].smooth_endPoint is not None:
                        a_delta = -(last_circ_point.a - point[2].smooth_endPoint.a) / 2
                        b_delta = -(last_circ_point.b - point[2].smooth_endPoint.b) / 2
                        c_delta = -(last_circ_point.c - point[2].smooth_endPoint.c) / 2
                    start_smoothing_point.a = end_smoothing_point.a + a_delta;\
                        start_smoothing_point.b = end_smoothing_point.b + b_delta; start_smoothing_point.c = end_smoothing_point.c + c_delta
                    middle_spline_point.a = end_smoothing_point.a + (a_delta / 2);\
                        middle_spline_point.b = end_smoothing_point.b + (b_delta / 2); middle_spline_point.c = end_smoothing_point.c + (c_delta / 2)
                    # TODO: repair Spline parametrs
                    smoothed_trajectory = Spline(robot_data, system=self).add_point(end_smoothing_point, middle_spline_point, start_smoothing_point, start_smoothing_point)._create_catmull_rom_spline_points()
                    full_trajectory_points.extend([cord for cord in coords])
                    full_trajectory_points += smoothed_trajectory
                    full_trajectory_points.extend(self.generate_line_points(smoothed_trajectory[-1], point[2].smooth_endPoint, count_points))
                    if point[2].smooth_endPoint.smooth_endPoint is None:
                        full_trajectory_points.append(point[2].smooth_endPoint)
                else:
                    # CIRC to CIRC
                    # Find smooth distance end CIRC point
                    if point[2].circ_angle is not None:
                        if point[2].circ_angle < 18:
                            raise ValueError("Arc in one angle must be greater than 18 degrees.")
                    circ_coords1, end_smoothing_point, _start_smoothing_point = self.generate_arc_3d(
                        point[0],
                        point[1],
                        point[2],
                        count_points,
                        distance=point[2].smooth_distance,
                        arc_angle=point[2].circ_angle
                        )
                    
                    smoothed_coords1, _end_smoothing_point, _start_smoothing_point = self.generate_arc_3d(
                        point[0],
                        point[1],
                        point[2],
                        count_points,
                        distance=None,
                        arc_angle=point[2].circ_angle+10 if point[2].circ_angle is not None else None,
                        )
                    end_circ_point = smoothed_coords1[-1]
                    
                    # Find smooth distance start CIRC point
                    new_movement = point[2].smooth_endPoint
                    if new_movement[2].circ_angle is not None:
                        if new_movement[2].circ_angle < 18:
                            raise ValueError("Arc in two angle must be greater than 18 degrees.")
                    circ_coords2, start_smoothing_point, _end_smoothing_point,  = self.generate_arc_3d(
                        new_movement[2],
                        new_movement[1],
                        new_movement[0],
                        count_points,
                        distance=new_movement[2].smooth_distance,
                        arc_angle=new_movement[2].circ_angle
                        )
                    
                    smoothed_coords2, _end_smoothing_point, _start_smoothing_point = self.generate_arc_3d(
                        new_movement[2],
                        new_movement[1],
                        new_movement[0],
                        count_points,
                        distance=new_movement[2].smooth_distance,
                        arc_angle=new_movement[2].circ_angle+10 if new_movement[2].circ_angle is not None else None,
                        )
                    start_circ_point = smoothed_coords2[-1]

                    # Find middle spline point
                    middle_spline_point = self.point_between(end_circ_point, start_circ_point, 50)   
                    
                    # find rebuildet end_circ_point and start_circ_point
                    end_circ_point = self.point_between(end_circ_point, middle_spline_point, 15)
                    start_circ_point = self.point_between(middle_spline_point, start_circ_point, 85)
                    
                    # Add to full trajectory 
                    full_trajectory_points.extend([cord for cord in circ_coords1])
                    # Create smoothed trajectory
                    end_smoothing_point.a = circ_coords1[-1].a; end_smoothing_point.b = circ_coords1[-1].b; end_smoothing_point.c = circ_coords1[-1].c
                    smoothed_trajectory = Spline(robot_data, system=self).add_point(end_smoothing_point, end_circ_point, middle_spline_point, start_circ_point, start_smoothing_point)._create_catmull_rom_spline_points()
                    full_trajectory_points += smoothed_trajectory
                    circ_coords2.reverse()
                    full_trajectory_points.extend([cord for cord in circ_coords2])

        return full_trajectory_points