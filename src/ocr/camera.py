import cv2
from enum import Enum
import numpy as np

from config import CFG


class Camera(Enum):
	left = CFG["camera"]["left"]
	right = CFG["camera"]["right"]


def init_camera() -> None:
	_start_capture(Camera.left, CFG["camera"]["init_time"]).release()


def take_photo(camera: Camera) -> np.ndarray:
	cam = _start_capture(camera)
	_, img = cam.read()
	cam.release()
	return img


def _start_capture(camera: Camera, calibration_delay: int = CFG["camera"]["photo_delay"]) -> cv2.VideoCapture:
	cam = cv2.VideoCapture(camera.value)

	# set camera properties
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, CFG["camera"]["width"])
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CFG["camera"]["height"])
	cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
	cam.set(cv2.CAP_PROP_FOCUS, CFG["camera"]["focus"])

	# wait for calibration delay
	for _ in range(int(cam.get(cv2.CAP_PROP_FPS) * calibration_delay)):
		cam.read()

	return cam
