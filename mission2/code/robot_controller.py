import time
from lerobot.robots.so101_follower.so101_follower import SO101Follower
from ble_controller import BLEController


class RobotController:
    HOME_POSITION = {
        "shoulder_pan.pos": -54.05,
        "shoulder_lift.pos": -86.62,
        "elbow_flex.pos": 99.82,
        "wrist_flex.pos": 32.17,
        "wrist_roll.pos": -2.72,
        "gripper.pos": 68.19,
    }

    def __init__(self, robot: SO101Follower, ble_controller: BLEController):
        self.robot = robot
        self.ble = ble_controller

    def move_to_home(self, steps: int = 15):
        current_obs = self.robot.get_observation()
        current_pos = {k: v for k, v in current_obs.items() if k.endswith(".pos")}

        for step in range(1, steps + 1):
            interpolated_position = {}
            for key, target_val in self.HOME_POSITION.items():
                current_val = current_pos.get(key, 0)
                interpolated_val = current_val + (target_val - current_val) * (
                    step / steps
                )
                interpolated_position[key] = interpolated_val

            self.robot.send_action(interpolated_position)
            time.sleep(0.1)
