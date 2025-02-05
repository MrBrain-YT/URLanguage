# import robot_modules.auth  as auth
import auth
from data_types import AnglePos, RobotData, XYZPos, Spline
from utils.vizualizer import Vizualization


system = auth.Auth("localhost", 5000, "15244dfbf0c9bd8378127e990c48e5a68b8c5a5786f34704bc528c9d91dbc84a")\
    .super_admin("SuperAdmin", "12345").system("localhost", 5000)
    
robot = RobotData("First", "654123")

""" New API test"""
# print(type(system.check_emergency(robot)))
    
""" Other commands """
# print(robot.xyz_to_angle("First", [[100, -100, 67.117],[200, 0, 67.117],[100, 100, 67.117]], "654123"))
# robot.set_program("First", "print('Test 1234')", "654123")

""" Data vizualization test """
" Smooth angle vizualization "
pos = AnglePos().from_list([200,40,0,150])
print(system.ptp(robot, pos))
p0 = XYZPos().from_list([201,150,100])
p1 = XYZPos().from_list([200,-50,100])
p2 = XYZPos().from_list([-200,310,100])
p3 = XYZPos().from_list([400,50,100])
p1.smooth_endPoint = p2
p1.smooth_distance = 200
p2.smooth_endPoint = p3
p2.smooth_distance = 200
p4 = XYZPos().from_list([43,9,-20])

lin1 = system.lin(robot, p1, start=p0)
# Current pos is p3
lin4 = system.lin(robot, p4, start=lin1.trjectory[-1])

trajectory1= []+lin1.trjectory+lin4.trjectory
Vizualization(trajectory=trajectory1).show_trajectory_plot()
" Spline vizualization "
# spl = Spline(robot_data=robot, system=system, num_points=10)
# p0 = XYZPos().from_list([201,150,100])
# p1 = XYZPos().from_list([200,-50,100])
# p2 = XYZPos().from_list([-200,310,100])
# p3 = XYZPos().from_list([400,50,100])
# spl.add_point(p0, p1, p2, p3)
# trajectory = spl.start_move()
# print(trajectory)
# Vizualization(trajectory=trajectory.trjectory).show_trajectory_plot()
" CIRC vizualization "
p1 = XYZPos().from_list([100, -100, 67.117])
p2 = XYZPos().from_list([200, 0, 67.117])
p3 = XYZPos().from_list([100, 100, 67.117])
trajectory2 = system.circ(robot, [p1,p2,p3], 20, speed_multiplier=1).trjectory
Vizualization(trajectory=trajectory2).show_trajectory_plot()

# Vizualization(trajectory=trajectory1+trajectory2).show_trajectory_plot()

""" PTP test """
# system.ptp(robot, AnglePos().from_list([100,140,-40,10]))
# pos = AnglePos().from_list([300,40,0,150])
# print(system.lin(robot, pos))
# robot.ptp_lin("First", [100,140,-40,10], "654123")
# robot.ptp("First", [200,120,-90,120], "654123")
# robot.ptp([10,0,0,-10])
# robot.ptp([200,60,30,20])
# print(robot.ptp([0,-100,-20,100]))

""" Drawing cube """
# p1 = robot.xyz_to_angle("First", [[100, -100, 67.117]], "654123") # рисуем квадрат
# p2 = robot.xyz_to_angle("First", [[200, 0, 67.117]], "654123")
# p3 = robot.xyz_to_angle("First", [100, 100, 67.117], "654123")
# p4 = robot.xyz_to_angle("First", [100, 100, 67.117], "654123")
# p5 = robot.xyz_to_angle("First", [100, 0, 67.117], "654123")
# robot.ptp("First", p1, "654123")
# robot.ptp("First", p2, "654123")
# robot.lin("First", p3, "654123")
# robot.lin("First", p4, "654123")
# robot.lin("First", p5, "654123")

""" XYZ test """
# robot.move_xyz([300, 0, 67.117])
# robot.move_xyz([300, 0, 67.117+200])
# robot.move_xyz([300, 0, 67.117-200])
# ang = robot.angle_to_xyz([180,60,30, 20])
# print(ang)
# one = [200,100,67.117]
# two = [250,0,67.117]
# three = [200,-100,67.117]
# robot.circ([one, two, three], 10)
# print(robot.xyz_to_angle([300, 0, 67.117+200]))
# print(robot.xyz_to_angle([300, 0, 67.117-200]))
# robot.move_xyz([300, 0, 67.117])
# robot.move_xyz([-200, -200, 67.117])

""" LIN test """
# robot.lin("First", "654123", [100, -100, 67.117], [200, 0, 67.117], 100)
# robot.lin([180,-30,-30,40], 100)
# robot.lin([200,60,30,20])
# robot.lin([0,-100,-20,100])