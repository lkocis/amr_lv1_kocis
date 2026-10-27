import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

CENTER = 5.544
AMPLITUDE = 4.0
TWO_PI = 2.0 * math.pi


def curve(w: float):
    #x = 5.544 + 4 sin(w), y = 5.544 + 4 sin(w) cos(w), w in [0, 2pi].
    return (CENTER + AMPLITUDE * math.sin(w),
            CENTER + AMPLITUDE * math.sin(w) * math.cos(w))


def wrap_angle(a: float) -> float:
    return math.atan2(math.sin(a), math.cos(a))


class FigureController(Node):

    def __init__(self):
        super().__init__('figure_controller')
        self.lookahead = self.declare_parameter('lookahead', 0.6).value
        self.linear_speed = self.declare_parameter('linear_speed', 2.0).value
        self.k_rotate = self.declare_parameter('k_rotate', 4.0).value
        self.dw = self.declare_parameter('dw', 0.01).value  # korak parametra

        self.w = 0.0
        self.pose = None

        #Čvor objavljuje brzine na cmd_vel, a turtlesim ih čita
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.pose_cb, 10)
        self.create_timer(0.02, self.control_loop)  # 50 Hz

    def pose_cb(self, msg: Pose):
        self.pose = msg

    def control_loop(self):
        #Ako nije stigla prva poza, ne šalji ništa
        if self.pose is None:
            return
        p = self.pose

        # pomakni cilj naprijed po krivulji dok nije dovoljno daleko 
        #(Čvor pamti parametar self.w, a to je pozicija ciljne točke na krivulji. 
        #Dok je ta točka bliže od 0.6 kornjači, w se povećava u malim koracima.)
        for _ in range(2000):
            tx, ty = curve(self.w)
            if math.hypot(tx - p.x, ty - p.y) >= self.lookahead:
                break
            self.w = (self.w + self.dw) % TWO_PI #da kretanje bude beskonačno

        err = wrap_angle(math.atan2(ty - p.y, tx - p.x) - p.theta)
        cmd = Twist()
        if abs(err) > math.pi / 2:
            cmd.angular.z = self.k_rotate * err  # okreni se na mjestu
        else:
            cmd.linear.x = self.linear_speed
            cmd.angular.z = 2.0 * self.linear_speed * math.sin(err) / self.lookahead
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = FigureController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
