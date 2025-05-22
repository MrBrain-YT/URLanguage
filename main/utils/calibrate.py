import os
import sys
import inspect
import math

import numpy as np
from scipy.optimize import least_squares

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from data_types import XYZPos

def find_tool_offset(flange_positions, flange_rotations_deg) -> np.ndarray:
    """
    Находит вектор смещения инструмента, используя 4 позиции и вращения фланца.
    
    Параметры:
    flange_positions - список из 4 позиций фланца (каждая как [x, y, z])
    flange_rotations_deg - список из 4 вращений фланца в градусах (каждое как [rx, ry, rz])
    
    Возвращает:
    tool_offset - вектор смещения инструмента [x, y, z]
    """
    # Преобразование градусов в радианы
    flange_rotations_rad = np.radians(flange_rotations_deg)
    
    # Функция для создания матрицы вращения из углов Эйлера (ZYX последовательность)
    def rotation_matrix(angles):
        rx, ry, rz = angles
        
        # Матрица вращения вокруг X
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx), np.cos(rx)]
        ])
        
        # Матрица вращения вокруг Y
        Ry = np.array([
            [np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])
        
        # Матрица вращения вокруг Z
        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz), np.cos(rz), 0],
            [0, 0, 1]
        ])
        
        # Комбинированная матрица вращения (ZYX порядок)
        R = Rz @ Ry @ Rx
        return R
    
    # Функция ошибки для оптимизации
    def error_function(tool_offset):
        error = []
        # Предполагаем, что точка инструмента должна быть постоянной во всех 4 позициях
        tool_positions = []
        
        for pos, rot in zip(flange_positions, flange_rotations_rad):
            R = rotation_matrix(rot)
            # Вычисляем положение инструмента: позиция фланца + повернутое смещение
            tool_pos = pos + R @ tool_offset
            tool_positions.append(tool_pos)
        
        # Вычисляем ошибки как расстояния между всеми парами точек
        for i in range(len(tool_positions)):
            for j in range(i+1, len(tool_positions)):
                error.append(np.linalg.norm(tool_positions[i] - tool_positions[j]))
                
        return np.array(error)
    
    # Начальное предположение для смещения инструмента
    initial_guess = np.array([0.0, 0.0, 100.0])  # Предполагаем, что инструмент направлен вдоль Z
    
    # Оптимизация для нахождения смещения с минимальной ошибкой
    result = least_squares(error_function, initial_guess)
    
    return result.x

def calibration_tool(calibration_positions:list[XYZPos]) -> list[float]:
    cp = calibration_positions
    flange_positions = [
        np.array([cp[0].x, cp[0].y, cp[0].z]),
        np.array([cp[1].x, cp[1].y, cp[1].z]),
        np.array([cp[2].x, cp[2].y, cp[2].z]),
        np.array([cp[3].x, cp[3].y, cp[3].z])
    ]
    flange_rotations_deg = [
        np.array([cp[0].a, cp[0].b, cp[0].c]),
        np.array([cp[1].a, cp[1].b, cp[1].c]),
        np.array([cp[2].a, cp[2].b, cp[2].c]),
        np.array([cp[3].a, cp[3].b, cp[3].c])
    ]
    tool_offset = find_tool_offset(flange_positions, flange_rotations_deg).tolist()
    result = [round(tool_offset[0], 4), round(tool_offset[1], 4), -round(tool_offset[2], 4),]
    return result


def angle_between_points(A:XYZPos, B:XYZPos, C:XYZPos, is_c:bool=None) -> float:
    A = A.export_to(list)[0:3]
    B = B.export_to(list)[0:3]
    C = C.export_to(list)[0:3]
    
    # Векторы BA и BC
    BA = [a - b for a, b in zip(A, B)]
    BC = [c - b for c, b in zip(C, B)]

    # Скалярное произведение векторов
    dot_product = sum(a * b for a, b in zip(BA, BC))

    # Модули векторов
    magnitude_BA = math.sqrt(sum(a**2 for a in BA))
    magnitude_BC = math.sqrt(sum(b**2 for b in BC))

    # Косинус угла между векторами
    cos_theta = dot_product / (magnitude_BA * magnitude_BC)

    # Ограничение значения для acos (на случай погрешностей)
    cos_theta = max(min(cos_theta, 1.0), -1.0)

    # Угол в радианах и перевод в градусы
    angle_rad = math.acos(cos_theta)
    angle_deg = math.degrees(angle_rad)
    # Определение знака угла
    if is_c:
        if C[1] < 0:
            angle_deg = -angle_deg
    else:
        if C[2] < B[2]:
            angle_deg = -angle_deg
                
    return angle_deg

def calibration_base(calibration_positions:list[XYZPos]) -> dict:
    cp = calibration_positions
    base_start_point = cp[0]
    base_x_point = cp[1]
    base_y_point = cp[2]
    
    additional_x_point = XYZPos().from_list([base_x_point.x, base_x_point.y, base_start_point.z])
    additional_y_point = XYZPos().from_list([base_y_point.x, base_y_point.y, base_start_point.z])
    calibrating_x_point = XYZPos().from_list([10000, 0, base_x_point.x])
    global_zero_point = XYZPos().from_list([0, 0, base_x_point.x])
    
    b_angle = angle_between_points(additional_x_point, base_start_point, base_x_point)
    c_angle = angle_between_points(additional_y_point, base_start_point, base_y_point)
    
    a_angle = angle_between_points(calibrating_x_point, global_zero_point, base_x_point, is_c=True)
    result = {
        "x": base_start_point.x,
        "y": base_start_point.y,
        "z": base_start_point.z,
        "a": round(a_angle, 6),
        "b": round(b_angle, 6),
        "c": round(c_angle, 6)
    }
    return result