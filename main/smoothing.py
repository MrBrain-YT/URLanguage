import numpy as np
from scipy.interpolate import CubicSpline

from data_types import XYZPos

# Функция для нормализации вектора
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
        return v
    return v / norm

# Функция для вычисления точки на биссектрисе угла
def bisector_point(A, B, C, distance):
    # Векторы от C к A и от C к B
    vector_CA = A - C
    vector_CB = B - C
    
    # Нормализуем векторы
    norm_CA = normalize(vector_CA)
    norm_CB = normalize(vector_CB)
    
    # Биссектриса будет равна нормализованной сумме этих векторов
    bisector = normalize(norm_CA + norm_CB)
    
    # Точка на биссектрисе на расстоянии distance / 3 от точки C
    point_on_bisector = C + bisector * (distance / 3)
    return point_on_bisector

# Функция для вычисления точек на отрезках на расстоянии distance от точки C
def points_on_segments(A, B, C, distance):
    # Вектор от C к A и от C к B
    vector_CA = A - C
    vector_CB = B - C
    
    # Нормализуем векторы
    norm_CA = normalize(vector_CA)
    norm_CB = normalize(vector_CB)
    
    # Точки на отрезках на расстоянии distance от точки C
    point_A_dist = C + norm_CA * distance
    point_B_dist = C + norm_CB * distance
    
    return point_A_dist, point_B_dist

# Функция для построения плавной кривой с использованием сплайна
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

def get_smothed_arc_points(current_robot_position:XYZPos, target_point:XYZPos, num_points:int=25):
    A = np.array(current_robot_position.export_to(export_type=list))  # Точка A (start point)
    B = np.array(target_point.smooth_endPoint.export_to(export_type=list))  # Точка B (end point)
    C = np.array(target_point.export_to(export_type=list))  # Точка C (angle point)

    distance = target_point.smooth_distance  # Расстояние, на которое сдвигаются точки
    # Находим точку на биссектрисе на расстоянии distance / 3 от точки C
    bisector = bisector_point(A, B, C, distance)
    # Находим точки на отрезках на расстоянии distance от угла
    point_A_dist, point_B_dist = points_on_segments(A, B, C, distance)
    # Строим дугу с использованием сплайна через точку на биссектрисе
    smoothed_arc_points = spline_arc(bisector, point_A_dist, point_B_dist, num_points=num_points)
    converted_points = []
    for point in smoothed_arc_points:
        converted_points.append(XYZPos.from_list(point))
    
    if target_point.smooth_endPoint is None:
        converted_points.append(target_point)
    return converted_points
