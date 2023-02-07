import cv2
from enum import Enum
import numpy as np

from config import CFG


class Camera(Enum):
	left = CFG["camera"]["left"]
	right = CFG["camera"]["right"]


def take_photo(camera: Camera) -> np.ndarray:
	cam = cv2.VideoCapture(camera.value)
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, CFG["camera"]["width"])
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CFG["camera"]["height"])
	for _ in range(int(cam.get(cv2.CAP_PROP_FPS) * CFG["camera"]["af_time"])):
		cam.read()
	_, img = cam.read()
	cam.release()
	return img
