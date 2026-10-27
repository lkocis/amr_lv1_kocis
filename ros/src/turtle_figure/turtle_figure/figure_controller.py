import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class FigureNode(Node):
    def __init__(self):
        super().__init__('figure_node')

        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.timer = self.create_timer(0.02, self.control_loop)

        self.pose = None
        self.omega = 0.0          # trenutni parametar krivulje, [0, 2*pi]
        self.omega_step = 0.1     # za koliko se pomice ciljna tocka
        self.reach_dist = 0.4     # udaljenost na kojoj se cilj smatra dostignutim
        self.linear_speed = 2.0   # brzina voznje naprijed

    def pose_callback(self, msg):
        self.pose = msg

    def target(self):
        # za trenutni omega vrati x i y koordinate ciljne tocke na krivulji
        x = 5.544 + 4 * math.sin(self.omega)
        y = 5.544 + 4 * math.sin(self.omega) * math.cos(self.omega)
        return x, y

    def control_loop(self):
        if self.pose is None:
            return

        tx, ty = self.target()
        dx = tx - self.pose.x           # dx i dy su razlike po osima
        dy = ty - self.pose.y
        distance = math.hypot(dx, dy)   # hypot iz dx i dy daje udaljenost (Pitagora)

        # Ako je blize od 0.4, pomakni cilj naprijed (za 0.1). 
        # Kad omega prijeđe 2π, vrati ga prema nuli, osmica se crta beskonacno.
        if distance < self.reach_dist:
            self.omega += self.omega_step
            if self.omega > 2 * math.pi:
                self.omega -= 2 * math.pi   
            return

        angle_to_target = math.atan2(dy, dx)                  # kut prema ciljnoj tocki
        error = angle_to_target - self.pose.theta             # theta je trenutni kut, error je koliko se treba okrenuti.
        error = math.atan2(math.sin(error), math.cos(error))  # normalizacija na [-pi, pi]

        msg = Twist()
        msg.angular.z = 6.0 * error
        # Ako je greska manja od 1 rad, vozi punom brzinom 2.0. Ako je velika, uspori na 0.5 
        if abs(error) < 1.0:
            msg.linear.x = self.linear_speed
        else:
            msg.linear.x = 0.5
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FigureNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()