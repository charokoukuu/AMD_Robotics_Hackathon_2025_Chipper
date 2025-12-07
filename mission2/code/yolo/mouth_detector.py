import threading
import time
import cv2
from ultralytics import YOLO
from pathlib import Path


class MouthDetector:
    def __init__(
        self,
        model_path: str = "mouth_classification/mouth_cls_model/weights/best.pt",
        camera_index: int = 5,
        camera_width: int = 320,
        camera_height: int = 240,
    ):
        self.model_path = model_path
        self.camera_index = camera_index
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.model = None
        self.cap = None

        self._load_model()

    def _load_model(self):
        model_path_obj = Path(self.model_path)
        if not model_path_obj.exists():
            print(f"Model not found: {self.model_path}")
            print(f"Current directory: {Path.cwd()}")
            return False

        self.model = YOLO(str(model_path_obj))
        print(f"Model loaded from: {model_path_obj}")
        print(f"Opening camera index: {self.camera_index}")
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        if not self.cap.isOpened():
            print(f"Failed to open camera {self.camera_index}")
        else:
            print(
                f"Camera {self.camera_index} opened successfully ({self.camera_width}x{self.camera_height})"
            )
        return True

    def detect_mouth_state(
        self, events: dict, recording_started: threading.Event, on_chip_confirmed=None
    ):
        if self.model is None:
            self._fallback_timer(events, recording_started)
            return

        chip_first_detected_time = None
        chip_confirmed = False
        chip_confirmed_time = None
        last_logged_state = None
        log_interval = 0.5  # 0.5秒ごとにログ出力

        while not events.get("stop_monitor", False):
            if not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            try:
                results = self.model(frame, verbose=False)

                if hasattr(results[0], "probs"):
                    probs = results[0].probs
                    top_class = probs.top1
                    confidence = probs.top1conf.item()
                    class_name = self.model.names[top_class].lower()

                    # リアルタイムログ出力
                    current_state = f"{class_name} ({confidence:.2f})"
                    if current_state != last_logged_state:
                        print(f"[状態] {current_state}")
                        last_logged_state = current_state

                    # 映像に状態を表示
                    status_text = f"{class_name.upper()} ({confidence:.2f})"
                    color = (
                        (0, 255, 0)
                        if "open" in class_name
                        else (0, 165, 255) if "chip" in class_name else (0, 0, 255)
                    )
                    cv2.putText(
                        frame,
                        status_text,
                        (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        color,
                        3,
                    )

                    if recording_started.is_set():
                        cv2.putText(
                            frame,
                            "RECORDING",
                            (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.5,
                            (0, 0, 255),
                            3,
                        )

                    if "open" in class_name and not recording_started.is_set():
                        print(f"[OPEN detected] confidence: {confidence:.2f}")
                        recording_started.set()
                        chip_first_detected_time = None
                        chip_confirmed = False

                    elif "chip" in class_name and recording_started.is_set():
                        if chip_first_detected_time is None:
                            chip_first_detected_time = time.time()
                            print(f"[CHIP detected] confidence: {confidence:.2f}")
                        elif not chip_confirmed:
                            elapsed = time.time() - chip_first_detected_time
                            if elapsed >= 3:
                                chip_confirmed = True
                                chip_confirmed_time = time.time()
                                print("[CHIP confirmed]")
                                if on_chip_confirmed:
                                    on_chip_confirmed()

                    elif recording_started.is_set() and "chip" not in class_name:
                        if chip_first_detected_time is not None and not chip_confirmed:
                            chip_first_detected_time = None

                    if chip_confirmed and chip_confirmed_time is not None:
                        elapsed_since_confirmed = time.time() - chip_confirmed_time
                        if elapsed_since_confirmed >= 2:
                            print("[Stop recording]")
                            events["exit_early"] = True
                            recording_started.clear()
                            chip_first_detected_time = None
                            chip_confirmed = False
                            chip_confirmed_time = None

                # 映像を表示
                cv2.imshow("Mouth Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            except Exception as e:
                print(f"Detection error: {e}")

            time.sleep(0.1)

        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def _fallback_timer(self, events: dict, recording_started: threading.Event):
        time.sleep(3)
        recording_started.set()
        time.sleep(2)
        events["exit_early"] = True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mouth Detection Demo")
    parser.add_argument("--camera", type=int, default=4, help="Camera index")
    parser.add_argument(
        "--model",
        type=str,
        default="mouth_classification/mouth_cls_model/weights/best.pt",
        help="Model path",
    )
    args = parser.parse_args()

    detector = MouthDetector(model_path=args.model, camera_index=args.camera)

    events = {"stop_monitor": False}
    recording_started = threading.Event()

    print("Press 'q' in the window to quit")
    print("Waiting for mouth detection...")

    detector.detect_mouth_state(events, recording_started)
