from dataclasses import dataclass, field
from typing import Union
import threading
import webbrowser
import os

import matplotlib.pyplot as plt
from plotly import graph_objects as go


from data_types import XYZPos

@dataclass
class Vizualization():
    trajectory:Union[list[XYZPos], XYZPos] = field(default_factory=list)
    
    def add_trajectory(self, trajectory:Union[list[XYZPos], XYZPos]):
        if isinstance(trajectory, XYZPos):
            self.trajectory.append(trajectory)
        else:
            self.trajectory.extend(trajectory)
       
    def show_mathplotlib_trajectory_plot(self):
        if not self.trajectory or self.trajectory == []:
            print("No trajectory data to plot.")
            return

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x_vals = [point.x for point in self.trajectory]
        y_vals = [point.y for point in self.trajectory]
        z_vals = [point.z for point in self.trajectory]

        ax.plot(x_vals, y_vals, z_vals, marker='o')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Trajectory Visualization')

        plt.show()
        
    def _create_plotly_plot(self):
        if not self.trajectory or self.trajectory == []:
            print("No trajectory data to plot.")
            return None

        x_vals = [point.x for point in self.trajectory]
        y_vals = [point.y for point in self.trajectory]
        z_vals = [point.z for point in self.trajectory]

        fig = go.Figure(data=[
            go.Scatter3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                mode='lines+markers',
                marker=dict(size=4),
                line=dict(width=2),
                name='Trajectory'
            )
        ])

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

    def show_plotly_trajectory_plot(self) -> None:
        """
        Показывает интерактивный график траектории с помощью Plotly.
        """
        fig = self._create_plotly_plot()
        if fig is None:
            return None
        else:

            # Запускаем в отдельном потоке
            plot_thread = threading.Thread(target=fig.show)
            plot_thread.daemon = False  # Делаем поток демоном, чтобы он завершился при закрытии основного приложения
            plot_thread.start()

        
