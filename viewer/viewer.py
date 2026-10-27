import math
import os
import socket
import threading
import time

import matplotlib.pyplot as plt
import roslibpy
from matplotlib.animation import FuncAnimation

HOST = os.environ.get('ROSBRIDGE_HOST', 'localhost')
PORT = int(os.environ.get('ROSBRIDGE_PORT', '9090'))

lock = threading.Lock()
xs, ys = [], []
latest = {'x': None, 'y': None, 'theta': 0.0}


def wait_for_port(host, port, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            time.sleep(1)
    return False


def pose_received(msg):
    with lock:
        latest.update(x=msg['x'], y=msg['y'], theta=msg['theta'])
        xs.append(msg['x'])
        ys.append(msg['y'])


def main():
    print(f'Waiting for rosbridge at {HOST}:{PORT}...')
    if not wait_for_port(HOST, PORT):
        raise SystemExit('rosbridge not reachable')

    ros = roslibpy.Ros(host=HOST, port=PORT)
    ros.run()
    if not ros.is_connected:
        raise SystemExit('Could not connect to rosbridge.')
    print('Connected to rosbridge.')

    sub = roslibpy.Topic(ros, '/turtle1/pose', 'turtlesim/msg/Pose',
                         throttle_rate=30, queue_length=1)
    sub.subscribe(pose_received)

    fig, ax = plt.subplots()
    ax.set_xlim(0, 11.09)
    ax.set_ylim(0, 11.09)
    ax.set_aspect('equal')
    ax.set_xlabel('X position')
    ax.set_ylabel('Y position')
    ax.set_title('Turtlesim pose visualization')
    ax.grid(True)
    (traj,) = ax.plot([], [], 'b-', label='Trajectory')
    (dot,) = ax.plot([], [], 'ro', label='Current position')
    (heading,) = ax.plot([], [], 'r-', linewidth=2)
    info = ax.text(0.02, 0.98, '', transform=ax.transAxes, va='top', fontsize=8)
    ax.legend(loc='upper right')

    def update(_):
        with lock:
            if latest['x'] is None:
                return traj, dot, heading, info
            x, y, th = latest['x'], latest['y'], latest['theta']
            traj.set_data(list(xs), list(ys))
        dot.set_data([x], [y])
        heading.set_data([x, x + 0.4 * math.cos(th)], [y, y + 0.4 * math.sin(th)])
        info.set_text(f'X: {x:.2f}\nY: {y:.2f}\nTheta: {th:.2f} rad')
        return traj, dot, heading, info

    anim = FuncAnimation(fig, update, interval=33, cache_frame_data=False)
    try:
        plt.show()
    finally:
        sub.unsubscribe()
        ros.terminate()


if __name__ == '__main__':
    main()
