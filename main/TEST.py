import auth
from data_types import AnglePos, RobotData, XYZPos, Spline, StaticData
from utils.vizualizer import Vizualization
from utils.triggers import TriggerHandler
from utils.calibrate import calibration_tool, calibration_base
import __robot

# __robot.TRAJECTORY_SEND_SWITCH = False

# system = auth.Auth("ursystem.local", 5000, "15244dfbf0c9bd8378127e990c48e5a68b8c5a5786f34704bc528c9d91dbc84a")\
#     .super_admin("SuperAdmin", "12345").system("ursystem.local", 5000) #, symulate=True
    
# robot = RobotData("First", "654123")
# robot2 = RobotData("NewRobot", "000000")

""" New API test"""
# print(system.get_robots())
# print(system.check_emergency(robot))

""" Bases test """
" create base and send manual calibration data "
# print(system.get_bases())
# print(system.create_base("one"))
# invalid_base_data = {"x": 0, "y": 0, "z": 0}
# base_data = {"x": 0, "y": 150, "z": 0,
#              "a": 0, "b": 0, "c": 45}
# print(system.set_base_data("one", base_data))
# print(system.set_robot_base(robot, "test"))
# print(system.delete_base("one"))
" send auto calibrated data "
positions_list = [
    XYZPos().from_list([0.0, 0.0, 0.0]),
    XYZPos().from_list([-10.0, 10.0, 0.0]),
    XYZPos().from_list([-10.0, -10.0, 0.0])
]
base_data = calibration_base(positions_list)
# print(system.set_base_data("test", base_data))
# p_start = XYZPos().from_list([0, 0, 0, 0, 0, 0])
# p1 = XYZPos().from_list([0, 100, 0, 90, 0, 0])
# print(system.lin(robot, p1, StaticData.CoordinatesSystem.BASE, start=p_start))
    
""" Other commands """
# print(robot.xyz_to_angle("First", [[100, -100, 67.117],[200, 0, 67.117],[100, 100, 67.117]], "654123"))
# robot.set_program("First", "print('Test 1234')", "654123")
# print(system.add_user("test", 54321, StaticData.Roles.USER))
# print(system.delete_user("test"))
# print(system.get_robot_log(robot, timestamp=1745249304)["data"])
# print(system.get_system_log(timestamp=1745249304)["data"])
# print(system.add_robot(robot2, "54321", 4))
# print(system.delete_robot(robot2))
" Tools comands "
# print(system.add_tool("gripper"))
# calibration_data = {
#     "x": 0,
#     "y": 0,
#     "z": 0,
# }
# print(system.set_calibrated_data("gripper", calibration_data))
# print(system.set_robot_tool(robot, "gripper"))
# p_start = XYZPos().from_list([0,0,0, 0, 0, 0])
# p1 = XYZPos().from_list([0, 100, 0, 180, 0, 0])
# print(tool_angle := system.xyz_to_angle(robot, p1, StaticData.CoordinatesSystem.TOOL))
# print(system.xyz_to_angle(robot, p1, StaticData.CoordinatesSystem.FLANGE))
# print(system.angle_to_xyz(robot, [tool_angle]))
# print(system.lin(robot, p1, StaticData.CoordinatesSystem.FLANGE, start=p_start))
# print(system.lin(robot, p1, StaticData.CoordinatesSystem.TOOL, start=p_start).trjectory[-1])
" Tools calibration test "
p1 = XYZPos().from_list([0.0, 200.0, 200.0,   0.0,   0.0,   -90.0])
p2 = XYZPos().from_list([10.0, 190.0, 200.0,  0.0,   90.0,   0.0])
p3 = XYZPos().from_list([0.0, 180.0, 200.0,   0.0,  0.0,   90.0])
p4 = XYZPos().from_list([-10.0, 190.0, 200.0,  0.0,   -90.0,  0.0])
Vizualization([p1,p2,p3,p4]).show_plotly_trajectory_plot()
print(calibration_tool([p1,p2,p3,p4]))

# p1 = XYZPos().from_list([0.0, 200.0, 200.0,   0.0,   0.0,   0.0])
# p2 = XYZPos().from_list([-10.0, 190.0, 200.0,  90.0,   0.0,   0.0])
# p3 = XYZPos().from_list([0.0, 180.0, 200.0,   180.0,  0.0,   0.0])
# p4 = XYZPos().from_list([0.0, 190.0, 210.0,  0.0,   0.0,  90.0])
# Vizualization([p1,p2,p3,p4]).show_plotly_trajectory_plot()
# print(calibration_tool([p1,p2,p3,p4]))

# p1 = XYZPos().from_list([0.0, 200.0, 200.0,   0.0,   0.0,   0.0])
# p2 = XYZPos().from_list([10.0, 190.0, 200.0,  90.0,   0.0,   0.0])
# p3 = XYZPos().from_list([20.0, 200.0, 200.0,   180.0,  0.0,   0.0])
# p4 = XYZPos().from_list([10.0, 200.0, 210.0,  0.0,   90.0,  0.0])
# Vizualization([p1,p2,p3,p4]).show_plotly_trajectory_plot()
# print(calibration_tool([p1,p2,p3,p4]))

""" Data vizualization test """
" Smooth angle vizualization "
# pos = AnglePos().from_list([100,40,-40,30])
# pos2 = AnglePos().from_list([100,190,0,40])
# pos3 = AnglePos().from_list([-20,30,70,40])
# pos4 = AnglePos().from_list([0,90,-20,0])
# print(system.ptp(robot, pos))
# print(system.ptp(robot, pos2))
# print(system.ptp(robot, pos3))
# print(system.ptp(robot, pos4))
# p0 = XYZPos().from_list([201,150,100])
# p1 = XYZPos().from_list([200,-50,100])
# p2 = XYZPos().from_list([-200,310,100])
# p3 = XYZPos().from_list([400,50,100])
# p1.smooth_endPoint = p2
# p1.smooth_distance = 200
# p2.smooth_endPoint = p3
# p2.smooth_distance = 200
# p4 = XYZPos().from_list([43,9,-20])

# lin1 = system.lin(robot, p1, start=p0)
# # Current pos is p3
# lin4 = system.lin(robot, p4, start=lin1.trjectory[-1])

# trajectory1= []+lin1.trjectory+lin4.trjectory
# Vizualization(trajectory=trajectory1).show_mathplotlib_trajectory_plot()
" Spline vizualization "
# spl = Spline(robot_data=robot, coordinate_system=StaticData.CoordinatesSystem.FLANGE, system=system, num_points=100)
# p0 = XYZPos().from_list([0,150,100, 90, 0, 0])
# p1 = XYZPos().from_list([200,-50,-100])
# p2 = XYZPos().from_list([-200,310,0, -90, 180, 0])
# p3 = XYZPos().from_list([400,50,50])
# spl.add_point(p0, p1, p2, p3)
# trajectory = spl.start_move().trjectory
# Vizualization(trajectory=trajectory).show_mathplotlib_trajectory_plot()
# print(trajectory)
" CIRC vizualization "
' CIRC to CIRC '
# p1 = XYZPos().from_list([100, -100, 67.117])
# p2 = XYZPos().from_list([200, 0, 67.117, 0, 0, 90])
# p3 = XYZPos().from_list([100, 100, 67.117])
# p6 = XYZPos().from_list([100, -100, 0, 180, 0, 0])
# p5 = XYZPos().from_list([200, 0, 0])
# p4 = XYZPos().from_list([100, 100, 0])
# p6.circ_angle = 90
# p3.smooth_endPoint = [p4, p5, p6]
# p3.smooth_distance = 20
# trajectory = system.circ(robot, [p1,p2,p3], 20, speed_multiplier=1, arc_angle=240).trjectory
# Vizualization(trajectory=trajectory).show_mathplotlib_trajectory_plot()
' CIRC to LIN '
# p1 = XYZPos().from_list([100, -100, 67.117])
# p2 = XYZPos().from_list([200, 0, 67.117])
# p3 = XYZPos().from_list([100, 100, 67.117])
# p4 = XYZPos().from_list([200, 100, 0])
# p3.smooth_endPoint = p4
# p3.smooth_distance = 30
# trajectory = system.circ(robot, [p1,p2,p3], 300, arc_angle=3600).trjectory
# Vizualization(trajectory=trajectory).show_mathplotlib_trajectory_plot()
' LIN to LIN '
# p_start = XYZPos().from_list([200, 200, 100])
# p1 = XYZPos().from_list([100, 100, 67.117])
# p2 = XYZPos().from_list([200, 0, 67.117])
# p3 = XYZPos().from_list([100, -100, 35])
# p4 = XYZPos().from_list([150, -100, 0])
# p2.smooth_endPoint = p3
# p2.smooth_distance = 50
# trajectory = system.lin(robot, p1, 20, speed_multiplier=1, start=p_start).trjectory
# trajectory2 = system.lin(robot, p2, 20, speed_multiplier=1, start=trajectory[-1]).trjectory
# trajectory3 = system.lin(robot, p4, 20, speed_multiplier=1, start=trajectory2[-1]).trjectory
# trajectory_full = trajectory + trajectory2 + trajectory3
# Vizualization(trajectory=trajectory_full).show_mathplotlib_trajectory_plot()
' LIN to CIRC using CIRC function '
# p1 = XYZPos().from_list([100, -100, 67.117])
# p2 = XYZPos().from_list([200, 0, 67.117, 180, 0, 0])
# p3 = XYZPos().from_list([100, 100, 67.117])
# p4 = XYZPos().from_list([100, -100, -60, 90, 0,0])
# p5 = XYZPos().from_list([100, -100, -61, 0, 200, 0])
# p6 = XYZPos().from_list([200, 0, -60])
# p7 = XYZPos().from_list([100, 100, -60])
# p3.smooth_endPoint = p4
# p3.smooth_distance = 30
# p4.smooth_endPoint = [p5, p6, p7]
# p4.smooth_distance = 30
# trajectory = system.circ(robot, [p1, p2, p3], 50, speed_multiplier=1, arc_angle=240).trjectory
# Vizualization(trajectory=trajectory).show_mathplotlib_trajectory_plot()
' LIN to CIRC using LIN function '
# p1 = XYZPos().from_list([100, -100, 67.117])
# p2 = XYZPos().from_list([200, 0, 67.117])
# p3 = XYZPos().from_list([100, 100, 67.117])
# p4 = XYZPos().from_list([100, -100, -60])
# p5 = XYZPos().from_list([100, -100, -61])
# p6 = XYZPos().from_list([200, 0, -60])
# p7 = XYZPos().from_list([100, 100, -60])
# p1.smooth_endPoint = p2
# p1.smooth_distance = 30
# p2.smooth_endPoint = p3
# p2.smooth_distance = 30
# p3.smooth_endPoint = p4
# p3.smooth_distance = 30
# p7.circ_angle = 300
# p4.smooth_endPoint = [p5, p6, p7]
# p4.smooth_distance = 60
# trajectory = system.lin(robot, p1, 20, speed_multiplier=1).trjectory
# # trajectory2 = system.lin(robot, p3, 20, speed_multiplier=1).trjectory
# Vizualization(trajectory=trajectory).show_plotly_trajectory_plot() # +trajectory2
" show all trajectory"
# Vizualization(trajectory=trajectory1+trajectory2).show_mathplotlib_trajectory_plot()

""" ABC Visualize test """
# p_start = XYZPos().from_list([200, 200, 100, 90, 0, 0])
# p1 = XYZPos().from_list([100, 100, 67.117, 90, 0, 90])
# p2 = XYZPos().from_list([200, 0, 67.117, 90, 0, 0])
# p3 = XYZPos().from_list([100, -100, 35, 0, 0, 0])
# p4 = XYZPos().from_list([150, -100, 0, 0, 0, 0])
# p2.smooth_endPoint = p3
# p2.smooth_distance = 50
# trajectory = system.lin(robot, p1, 20, speed_multiplier=1, start=p_start).trjectory
# trajectory2 = system.lin(robot, p2, 20, speed_multiplier=1, start=trajectory[-1]).trjectory
# trajectory3 = system.lin(robot, p4, 20, speed_multiplier=1, start=trajectory2[-1]).trjectory
# trajectory_full = trajectory + trajectory2 + trajectory3
# Vizualization(trajectory=trajectory_full).show_plotly_trajectory_plot()
# Vizualization(system.lin(robot, p2, num_points=25 ,start=XYZPos().from_list([100, 0, 67.117])).trjectory).show_mathplotlib_trajectory_plot()


""" PTP test """
# system.ptp(robot, AnglePos().from_list([100,140,-40,10]))
# system.ptp(robot, AnglePos().from_list([0,140,-40,10]))

' CIRC test '
# p1 = XYZPos().from_list([50, 100, 67.117])
# p2 = XYZPos().from_list([150, 0, 67.117, 180, 0, 0])
# p3 = XYZPos().from_list([50, -100, 67.117, 0, 90, 0])
# Vizualization(system.circ(robot, [p1,p2,p3], 50,arc_angle=300, speed_multiplier=0.6).trjectory).show_mathplotlib_trajectory_plot()

""" Drawing cube """
# p1 = system.xyz_to_angle(robot, XYZPos().from_list([100, 0, 67.117])) # рисуем квадрат
# p2 = XYZPos().from_list([200, 0, 67.117, 90, 0, 0])
# p3 = XYZPos().from_list([200, 100, 67.117])
# p4 = XYZPos().from_list([100, 100, 67.117])
# p5 = XYZPos().from_list([100, 0, 67.117])
# system.ptp(robot, p1)
# system.lin(robot, p2, start=XYZPos().from_list([100, 0, 67.117]))
# system.lin(robot, p3, start=p2)
# system.lin(robot, p4, start=p3)
# system.lin(robot, p5, start=p4)

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

""" Triggers test """
" LIN "
# def hello_trigger_handler():
#     print("Hello")

# TH = TriggerHandler(robot_data=robot, system=system)
# TH.add_trigger("hello", hello_trigger_handler)

# p_start = XYZPos().from_list([200, 200, 100])
# p1 = XYZPos().from_list([100, 100, 67.117])
# p2 = XYZPos().from_list([200, 0, 67.117])
# p3 = XYZPos().from_list([100, -100, 35])
# p4 = XYZPos().from_list([150, -100, 0])
# p2.smooth_endPoint = p3
# p2.smooth_distance = 50
# triggers = {
#         "hello" : 5,
#         "test" : 150
#     }
# trajectory = system.lin(robot, p1, 20, speed_multiplier=1, start=p_start).trjectory
# TH.start_handling()
# trajectory2 = system.lin(robot, p2, 20, speed_multiplier=1, start=trajectory[-1], triggers=triggers).trjectory
# trajectory3 = system.lin(robot, p4, 20, speed_multiplier=1, start=trajectory2[-1]).trjectory
# TH.end_handling()

" CIRC "
# def hello_trigger_handler():
#     print("Hello")
#     system.set_position_id(robot, "")

# TH = TriggerHandler(robot_data=robot, system=system)
# TH.add_trigger("hello", hello_trigger_handler)

# triggers = {
#         "hello" : 5,
#         "test" : 150
#     }

# p1 = XYZPos().from_list([50, 100, 67.117])
# p2 = XYZPos().from_list([150, 0, 67.117, 180, 0, 0])
# p3 = XYZPos().from_list([50, -100, 67.117, 0, 90, 0])
# TH.start_handling()
# Vizualization(system.circ(robot, [p1,p2,p3], 50, arc_angle=300, speed_multiplier=0.3, triggers=triggers).trjectory).show_mathplotlib_trajectory_plot()
# TH.end_handling()