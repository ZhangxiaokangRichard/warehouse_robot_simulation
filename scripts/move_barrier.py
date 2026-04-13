#!/usr/bin/env python3
"""
Move Barrier Node - Controls dynamic obstacles in Gazebo
Moves barriers along predefined quadrilateral trajectories
"""

import rospy
import math
from gazebo_msgs.srv import SetModelState
from gazebo_msgs.msg import ModelState
from geometry_msgs.msg import Pose, Twist, Point, Quaternion


class MoveBarrier:
    def __init__(self):
        rospy.init_node('move_barrier', anonymous=False)

        rospy.loginfo("Move Barrier node initialized. Waiting for Gazebo service...")

        # Wait for service to be available with longer timeout
        service_name = '/gazebo/set_model_state'
        try:
            rospy.wait_for_service(service_name, timeout=30)
            rospy.loginfo(f"Service {service_name} is available")
        except rospy.ROSException as e:
            rospy.logerr(f"Service {service_name} not available after 30 seconds: {e}")
            rospy.logwarn("Continuing anyway, will retry when updating barriers...")

        # Create service client for setting model state
        self.set_model_state_service = rospy.ServiceProxy(service_name, SetModelState)

        # Load barrier configurations from parameters
        self.barriers = self._load_barriers_config()

        if not self.barriers:
            rospy.logerr("No barriers configured. Exiting.")
            return

        rospy.loginfo(f"Successfully loaded {len(self.barriers)} barriers configuration")

        # Initialize barrier states
        self.barrier_states = {}
        for barrier_name, config in self.barriers.items():
            self.barrier_states[barrier_name] = {
                'current_waypoint': 0,
                'progress': 0.0,  # 0.0 to 1.0
                'time_start': rospy.Time.now()
            }
            rospy.loginfo(f"  - {barrier_name}: diameter={config['diameter']}m, height={config['height']}m, speed={config['speed']}m/s")

        # Control parameters
        self.update_rate = rospy.get_param('~update_rate', 20)  # Hz
        self.rate = rospy.Rate(self.update_rate)

    def _load_barriers_config(self):
        """Load barrier configurations from ROS parameters"""
        barriers = {}

        # Get barrier names from parameter (comma-separated string)
        barrier_names_str = rospy.get_param('~barrier_names', 'barrier_1,barrier_2,barrier_3')
        barrier_names = [name.strip() for name in barrier_names_str.split(',')]

        for barrier_name in barrier_names:
            param_prefix = f'~barriers/{barrier_name}'

            try:
                # Load barrier parameters
                start_x = rospy.get_param(f'{param_prefix}/start_position/x', 0.0)
                start_y = rospy.get_param(f'{param_prefix}/start_position/y', 0.0)
                start_pos = [start_x, start_y]

                path_points = rospy.get_param(f'{param_prefix}/path')
                diameter = rospy.get_param(f'{param_prefix}/diameter', 0.6)
                height = rospy.get_param(f'{param_prefix}/height', 1.8)
                speed = rospy.get_param(f'{param_prefix}/speed', 1.6)  # m/s

                barriers[barrier_name] = {
                    'start_position': start_pos,
                    'path_points': path_points,  # List of [x, y] coordinates
                    'diameter': diameter,
                    'height': height,
                    'speed': speed,
                }

                rospy.loginfo(f"Loaded barrier '{barrier_name}': diameter={diameter}m, height={height}m, speed={speed}m/s")

            except (KeyError, TypeError) as e:
                rospy.logwarn(f"Missing parameter for barrier '{barrier_name}': {e}")
                continue

        return barriers

    def _calculate_trajectory_point(self, path_points, total_distance, current_distance):
        """
        Calculate position and orientation along the trajectory

        Args:
            path_points: List of [x, y] coordinates
            total_distance: Total path distance
            current_distance: Current distance traveled

        Returns:
            (x, y, yaw) tuple
        """
        # Normalize path to cyclic loop
        current_distance = current_distance % total_distance

        cumulative_distance = 0.0
        for i in range(len(path_points)):
            p1 = path_points[i]
            p2 = path_points[(i + 1) % len(path_points)]

            segment_distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

            if cumulative_distance + segment_distance >= current_distance:
                # We are on this segment
                ratio = (current_distance - cumulative_distance) / segment_distance if segment_distance > 0 else 0

                # Interpolate position
                x = p1[0] + ratio * (p2[0] - p1[0])
                y = p1[1] + ratio * (p2[1] - p1[1])

                # Calculate yaw (direction)
                yaw = math.atan2(p2[1] - p1[1], p2[0] - p1[0])

                return x, y, yaw

            cumulative_distance += segment_distance

        # Fallback: return last point
        return path_points[-1][0], path_points[-1][1], 0.0

    def _calculate_total_path_distance(self, path_points):
        """Calculate total distance of the path"""
        total_distance = 0.0
        for i in range(len(path_points)):
            p1 = path_points[i]
            p2 = path_points[(i + 1) % len(path_points)]
            total_distance += math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        return total_distance

    def _quaternion_from_yaw(self, yaw):
        """Convert yaw angle to quaternion"""
        half_yaw = yaw / 2.0
        return Quaternion(
            x=0.0,
            y=0.0,
            z=math.sin(half_yaw),
            w=math.cos(half_yaw)
        )

    def update_barrier_position(self, barrier_name, config, state):
        """Update the position of a single barrier"""
        current_time = rospy.Time.now()
        elapsed_time = (current_time - state['time_start']).to_sec()

        # Calculate distance traveled
        distance_traveled = config['speed'] * elapsed_time

        # Calculate path parameters
        path_points = config['path_points']
        total_distance = self._calculate_total_path_distance(path_points)

        if total_distance == 0:
            rospy.logwarn(f"Barrier '{barrier_name}' has zero path distance")
            return

        # Get current position along path
        x, y, yaw = self._calculate_trajectory_point(path_points, total_distance, distance_traveled)

        z = config['height'] / 2.0  # Center of cylinder

        # Create model state message
        model_state = ModelState()
        model_state.model_name = barrier_name
        model_state.pose.position = Point(x=x, y=y, z=z)
        model_state.pose.orientation = self._quaternion_from_yaw(yaw)
        model_state.twist = Twist()  # Zero velocity
        model_state.reference_frame = 'world'

        try:
            self.set_model_state_service(model_state)
        except rospy.ServiceException as e:
            rospy.logdebug(f"Failed to set state for barrier '{barrier_name}': {e}")
        except Exception as e:
            rospy.logdebug(f"Exception setting state for barrier '{barrier_name}': {e}")

    def run(self):
        """Main loop to update barrier positions"""
        rospy.loginfo("Move Barrier node started. Publishing barrier positions...")

        service_ready = False
        reconnect_attempts = 0
        max_reconnect_attempts = 5

        while not rospy.is_shutdown():
            # Try to ensure service is available
            if not service_ready and reconnect_attempts < max_reconnect_attempts:
                try:
                    rospy.wait_for_service('/gazebo/set_model_state', timeout=2)
                    service_ready = True
                    rospy.loginfo("Gazebo set_model_state service is now available")
                except rospy.ROSException:
                    reconnect_attempts += 1
                    rospy.logdebug(f"Waiting for Gazebo service (attempt {reconnect_attempts}/{max_reconnect_attempts})")
                    self.rate.sleep()
                    continue

            # Update barrier positions
            if service_ready:
                for barrier_name, config in self.barriers.items():
                    state = self.barrier_states[barrier_name]
                    self.update_barrier_position(barrier_name, config, state)

            self.rate.sleep()

        rospy.loginfo("Move Barrier node shutting down")


def main():
    try:
        move_barrier = MoveBarrier()
        move_barrier.run()
    except rospy.ROSInterruptException:
        pass
    except rospy.ROSException as e:
        rospy.logerr(f"ROS Exception: {e}")


if __name__ == '__main__':
    main()
