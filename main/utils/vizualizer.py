from dataclasses import dataclass, field
from typing import Union
import threading
import os
import sys
import inspect

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from plotly import graph_objects as go
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from data_types import XYZPos

@dataclass
class Vizualization():
    trajectory: Union[list[XYZPos], XYZPos] = field(default_factory=list)
    angle_line_factor: float = 0.05  # Фактор, определяющий длину линии относительно диапазона

    def add_trajectory(self, trajectory: Union[list[XYZPos], XYZPos]):
        if isinstance(trajectory, XYZPos):
            self.trajectory.append(trajectory)
        else:
            self.trajectory.extend(trajectory)

    def _calculate_adaptive_line_length(self):
        """Вычисляет адаптивную длину линии на основе диапазона координат."""
        if not self.trajectory:
            return 1.0  # Значение по умолчанию, если траектория пуста

        all_coords = np.array([[point.x, point.y, point.z] for point in self.trajectory])
        min_vals = np.min(all_coords, axis=0)
        max_vals = np.max(all_coords, axis=0)
        ranges = max_vals - min_vals

        # Используем максимальный диапазон среди X, Y, Z
        max_range = np.max(ranges)
        if max_range == 0:
            return 1.0  # Избегаем деления на ноль, если все точки совпадают

        return max_range * self.angle_line_factor

    def show_mathplotlib_trajectory_plot(self):
        if not self.trajectory:
            print("No trajectory data to plot.")
            return

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x_vals = [point.x for point in self.trajectory]
        y_vals = [point.y for point in self.trajectory]
        z_vals = [point.z for point in self.trajectory]

        ax.plot(x_vals, y_vals, z_vals, marker='o', label='Trajectory')

        adaptive_length = self._calculate_adaptive_line_length()
        for point in self.trajectory:
            self._plot_direction_matplotlib(ax, point, adaptive_length)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Trajectory Visualization')
        ax.legend()
        plt.show()

    def _plot_direction_matplotlib(self, ax: Axes3D, point: XYZPos, length: float):
        """Отображает линию, показывающую направление, для одной точки с заданной длиной."""
        x, y, z = point.x, point.y, point.z
        a, b, c = point.a, point.b, point.c

        direction_local = np.array([0, 0, 1])

        rotation_x = np.array([[1, 0, 0],
                               [0, np.cos(np.radians(a)), -np.sin(np.radians(a))],
                               [0, np.sin(np.radians(a)), np.cos(np.radians(a))]])

        rotation_y = np.array([[np.cos(np.radians(b)), 0, np.sin(np.radians(b))],
                               [0, 1, 0],
                               [-np.sin(np.radians(b)), 0, np.cos(np.radians(b))]])

        rotation_z = np.array([[np.cos(np.radians(c)), -np.sin(np.radians(c)), 0],
                               [np.sin(np.radians(c)), np.cos(np.radians(c)), 0],
                               [0, 0, 1]])

        direction_rotated = np.dot(rotation_z, np.dot(rotation_y, np.dot(rotation_x, direction_local)))

        end_point = np.array([x, y, z]) + direction_rotated * length

        ax.plot([x, end_point[0]], [y, end_point[1]], [z, end_point[2]], color='red', linewidth=1)

    def _create_plotly_plot(self):
        if not self.trajectory:
            print("No trajectory data to plot.")
            return None

        x_vals = [point.x for point in self.trajectory]
        y_vals = [point.y for point in self.trajectory]
        z_vals = [point.z for point in self.trajectory]

        scatter_trace = go.Scatter3d(
            x=x_vals,
            y=y_vals,
            z=z_vals,
            mode='lines+markers',
            marker=dict(size=4),
            line=dict(width=2),
            name='Trajectory'
        )

        direction_traces = []
        adaptive_length = self._calculate_adaptive_line_length()
        for point in self.trajectory:
            trace = self._create_direction_plotly_trace(point, adaptive_length)
            if trace:
                direction_traces.append(trace)

        fig = go.Figure(data=[scatter_trace] + direction_traces)

        fig.update_layout(
            title='Trajectory Visualization',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='cube'
            ),
            showlegend=True
        )

        return fig

    def _create_direction_plotly_trace(self, point: XYZPos, length: float):
        """Создает trace для Plotly, показывающий направление для одной точки с заданной длиной."""
        x, y, z = point.x, point.y, point.z
        a, b, c = point.a, point.b, point.c

        direction_local = np.array([0, 0, 1])

        rotation_x = np.array([[1, 0, 0],
                               [0, np.cos(np.radians(a)), -np.sin(np.radians(a))],
                               [0, np.sin(np.radians(a)), np.cos(np.radians(a))]])

        rotation_y = np.array([[np.cos(np.radians(b)), 0, np.sin(np.radians(b))],
                               [0, 1, 0],
                               [-np.sin(np.radians(b)), 0, np.cos(np.radians(b))]])

        rotation_z = np.array([[np.cos(np.radians(c)), -np.sin(np.radians(c)), 0],
                               [np.sin(np.radians(c)), np.cos(np.radians(c)), 0],
                               [0, 0, 1]])

        direction_rotated = np.dot(rotation_z, np.dot(rotation_y, np.dot(rotation_x, direction_local)))

        end_point = np.array([x, y, z]) + direction_rotated * length

        return go.Scatter3d(
            x=[x, end_point[0]],
            y=[y, end_point[1]],
            z=[z, end_point[2]],
            mode='lines',
            line=dict(color='red', width=2),
            name=f'Direction ({x:.2f}, {y:.2f}, {z:.2f})',
            showlegend=False
        )

    def show_plotly_trajectory_plot(self) -> None:
        """
        Показывает интерактивный график траектории с направлением с помощью Plotly с адаптивной длиной линий.
        """
        fig = self._create_plotly_plot()
        if fig is None:
            return None
        else:
            plot_thread = threading.Thread(target=fig.show)
            plot_thread.daemon = False
            plot_thread.start()

if __name__ == '__main__':
    # Пример использования с большой траекторией
    large_trajectory = [XYZPos(x=i, y=i*0.5, z=i*2, a=10*i, b=5*i, c=2*i) for i in range(50)]
    large_visualization = Vizualization(trajectory=large_trajectory)
    large_visualization.show_mathplotlib_trajectory_plot()
    large_visualization.show_plotly_trajectory_plot()

    # Пример использования с маленькой траекторией
    small_trajectory = [
        XYZPos(x=0, y=0, z=0, a=0, b=0, c=0),
        XYZPos(x=0.1, y=0, z=0, a=45, b=0, c=0),
        XYZPos(x=0.1, y=0.1, z=0, a=0, b=30, c=0),
    ]
    small_visualization = Vizualization(trajectory=small_trajectory)
    small_visualization.show_mathplotlib_trajectory_plot()
    small_visualization.show_plotly_trajectory_plot()