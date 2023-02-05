import cv2
from enum import Enum
import numpy as np

from config import CFG


class Camera(Enum):
	left = cv2.VideoCapture(CFG["camera"]["left"])
	right = cv2.VideoCapture(CFG["camera"]["right"])


def take_photo(camera: Camera) -> np.ndarray:
	_, img = camera.value.read()
	camera.value.release()
	return img
