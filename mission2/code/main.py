import threading
import asyncio

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors
from lerobot.processor import make_default_processors
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
from lerobot.robots.so101_follower.so101_follower import SO101Follower
from lerobot.scripts.lerobot_record import record_loop
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.visualization_utils import init_rerun

from config import (
    FPS,
    EPISODE_TIME_SEC,
    TASK_DESCRIPTION,
    HF_MODEL_ID,
    HF_DATASET_ID,
    ROBOT_PORT,
    ROBOT_ID,
    CAMERA_FRONT_INDEX,
    CAMERA_FRONT2_INDEX,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    BLE_DEVICE_ADDRESS,
    BLE_INITIAL_VALUE,
    BLE_INCREMENT,
    MOUTH_MODEL_PATH,
    MOUTH_CAMERA_INDEX,
    MOUTH_CAMERA_WIDTH,
    MOUTH_CAMERA_HEIGHT,
)
from yolo.mouth_detector import MouthDetector
from ble_controller import BLEController
from robot_controller import RobotController


class RecordingSystem:
    def __init__(self):
        self.ble_value = BLE_INITIAL_VALUE
        self.episode_count = 0
        self.ble = BLEController(BLE_DEVICE_ADDRESS)
        self.events = None
        self.robot = None
        self.mouth_detector = None
        self.robot_controller = None

    def setup_robot(self):
        camera_config = {
            "front": OpenCVCameraConfig(
                index_or_path=CAMERA_FRONT_INDEX,
                width=CAMERA_WIDTH,
                height=CAMERA_HEIGHT,
                fps=FPS,
            ),
            "front2": OpenCVCameraConfig(
                index_or_path=CAMERA_FRONT2_INDEX,
                width=CAMERA_WIDTH,
                height=CAMERA_HEIGHT,
                fps=FPS,
            ),
        }
        robot_config = SO101FollowerConfig(
            port=ROBOT_PORT, id=ROBOT_ID, cameras=camera_config
        )
        self.robot = SO101Follower(robot_config)
        self.robot.connect()
        self.robot_controller = RobotController(self.robot, self.ble)

    def setup_dataset(self):
        policy = ACTPolicy.from_pretrained(HF_MODEL_ID)

        action_features = hw_to_dataset_features(self.robot.action_features, "action")
        obs_features = hw_to_dataset_features(
            self.robot.observation_features, "observation"
        )
        dataset_features = {**action_features, **obs_features}

        dataset = LeRobotDataset.create(
            repo_id=HF_DATASET_ID,
            fps=FPS,
            features=dataset_features,
            robot_type=self.robot.name,
            use_videos=True,
            image_writer_threads=4,
        )

        preprocessor, postprocessor = make_pre_post_processors(
            policy_cfg=policy,
            pretrained_path=HF_MODEL_ID,
            dataset_stats=dataset.meta.stats,
        )

        return dataset, policy, preprocessor, postprocessor

    def on_chip_confirmed(self):
        self.ble_value += BLE_INCREMENT
        print(f"BLE: {self.ble_value}")
        asyncio.run(self.ble.send(str(self.ble_value)))

    def setup_monitoring(self, events, recording_started):
        self.mouth_detector = MouthDetector(
            MOUTH_MODEL_PATH,
            MOUTH_CAMERA_INDEX,
            MOUTH_CAMERA_WIDTH,
            MOUTH_CAMERA_HEIGHT,
        )
        self.events = events

        mouth_thread = threading.Thread(
            target=self.mouth_detector.detect_mouth_state,
            args=(events, recording_started, self.on_chip_confirmed),
            daemon=False,
        )
        mouth_thread.start()

    def run(self):
        self.setup_robot()
        dataset, policy, preprocessor, postprocessor = self.setup_dataset()

        _, events = init_keyboard_listener()
        init_rerun(session_name="recording")

        teleop_action_processor, robot_action_processor, robot_observation_processor = (
            make_default_processors()
        )

        recording_started = threading.Event()
        self.setup_monitoring(events, recording_started)

        asyncio.run(self.ble.send(str(self.ble_value)))
        print(f"BLE initialized: {self.ble_value}")

        try:
            while True:
                self.robot_controller.move_to_home()

                print("Waiting for OPEN...")
                recording_started.wait()

                self.episode_count += 1
                print(f"Episode {self.episode_count}")

                events["exit_early"] = False

                record_loop(
                    robot=self.robot,
                    events=events,
                    fps=FPS,
                    teleop_action_processor=teleop_action_processor,
                    robot_action_processor=robot_action_processor,
                    robot_observation_processor=robot_observation_processor,
                    policy=policy,
                    preprocessor=preprocessor,
                    postprocessor=postprocessor,
                    dataset=dataset,
                    control_time_s=EPISODE_TIME_SEC,
                    single_task=TASK_DESCRIPTION,
                    display_data=False,
                )

                print(f"Episode {self.episode_count} done")

        except KeyboardInterrupt:
            print("\nInterrupted")

        finally:
            events["stop_monitor"] = True
            self.robot.disconnect()
            print(f"Total: {self.episode_count} episodes")


if __name__ == "__main__":
    system = RecordingSystem()
    system.run()
