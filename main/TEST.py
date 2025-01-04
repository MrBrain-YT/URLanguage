# import robot_modules.auth  as auth
import auth
from data_types import AnglePos, RobotData

system = auth.Auth("localhost", 5000, "15244dfbf0c9bd8378127e990c48e5a68b8c5a5786f34704bc528c9d91dbc84a")\
    .super_admin("SuperAdmin", "12345").system("localhost", 5000)
    
""" Other commands """
# print(robot.xyz_to_angle("First", [[100, -100, 67.117],[200, 0, 67.117],[100, 100, 67.117]], "654123"))
# robot.set_program("First", "print('Test 1234')", "654123")
    
""" PTP test """
pos = AnglePos().from_list([300,40,0,150])
robot = RobotData("First", "654123")

print(system.ptp_lin(robot, pos))
# robot.ptp_lin("First", [100,140,-40,10], "654123")
# robot.ptp("First", [200,120,-90,120], "654123")
# robot.ptp([10,0,0,-10])
# robot.ptp([200,60,30,20])
# print(robot.ptp([0,-100,-20,100]))

""" CIRC test """
# robot.circ("First", "654123", [[100, -100, 67.117],[200, 0, 67.117],[100, 100, 67.117]], 20, speed_multiplier=1)
# robot.ptp("First", [100,140,-40,10], "654123")

""" Drawing cube """
# p1 = robot.xyz_to_angle("First", [[100, -100, 67.117]], "654123") # рисуем квадрат
# p2 = robot.xyz_to_angle("First", [[200, 0, 67.117]], "654123")
# p3 = robot.xyz_to_angle("First", [100, 100, 67.117], "654123")
# p4 = robot.xyz_to_angle("First", [100, 100, 67.117], "654123")
# p5 = robot.xyz_to_angle("First", [100, 0, 67.117], "654123")


# robot.ptp_lin("First", p1, "654123")
# robot.ptp_lin("First", p2, "654123")
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