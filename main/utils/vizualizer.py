from dataclasses import dataclass, field
from typing import Union

import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

from data_types import XYZPos

@dataclass
class Vizualization():
    trajectory:Union[list[XYZPos], XYZPos] = field(default_factory=list)
    
    def add_trajectory(self, trajectory:Union[list[XYZPos], XYZPos]):
        if isinstance(trajectory, XYZPos):
            self.trajectory.append(trajectory)
        else:
            for point in trajectory:
                self.trajectory.append(point)
       
    def show_trajectory_plot(self):
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
        
