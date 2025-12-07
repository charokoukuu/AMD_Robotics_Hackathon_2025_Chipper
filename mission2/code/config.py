from datetime import datetime

FPS = 30
EPISODE_TIME_SEC = 60
TASK_DESCRIPTION = "potato system release"
HF_MODEL_ID = "charokoukuu/record-potato-release-6"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
HF_DATASET_ID = f"charokoukuu/eval_record-potato-release-{timestamp}"

ROBOT_PORT = "/dev/ttyACM1"
ROBOT_ID = "pullup_follower_arm"

CAMERA_FRONT_INDEX = 6
CAMERA_FRONT2_INDEX = 9
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

BLE_DEVICE_ADDRESS = "34:B7:DA:5E:81:15"
BLE_INITIAL_VALUE = 100
BLE_INCREMENT = 40

MOUTH_MODEL_PATH = "yolo/mouth_classification/mouth_cls_model/weights/best.pt"
MOUTH_CAMERA_INDEX = 5
MOUTH_CAMERA_WIDTH = 320
MOUTH_CAMERA_HEIGHT = 240
