from __future__ import annotations

from queue import SimpleQueue
from threading import Event, Thread

import cv2
from enum import Enum
import numpy as np

from config import CFG

if CFG["web"]["host"] == "localhost":
	from typing import Union, Tuple, Optional
	from pynput.keyboard import Key, KeyCode, Listener


capture_thread_input: SimpleQueue[Optional[Tuple[Camera, float, SimpleQueue]]] = SimpleQueue()


class Camera(Enum):
	left = CFG["camera"]["left"]
	right = CFG["camera"]["right"]


def init_camera() -> None:
	capture_thread_input.put((Camera.left, CFG["camera"]["init_time"], SimpleQueue()))


def take_photo(camera: Camera) -> np.ndarray:
	return_queue = SimpleQueue()
	capture_thread_input.put((camera, CFG["camera"]["photo_delay"], return_queue))
	return return_queue.get()


def _capture(camera: Camera, calibration_delay: float) -> cv2.VideoCapture:
	cam = cv2.VideoCapture(camera.value)

	# set camera properties
	cam.set(cv2.CAP_PROP_FRAME_WIDTH, CFG["camera"]["width"])
	cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CFG["camera"]["height"])
	cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
	cam.set(cv2.CAP_PROP_FOCUS, CFG["camera"]["focus"])

	# wait for calibration delay
	if CFG["web"]["host"] == "localhost":
		stop = Event()

		def on_press(key: Union[Key, KeyCode, None]) -> None:
			if hasattr(key, "char") and key.char == "f":
				stop.set()

		key_listener = Listener(on_press=on_press)
		key_listener.start()
		cv2.namedWindow("preview", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_NORMAL)
		cv2.resizeWindow("preview", 854, 480)
		while not stop.is_set():
			cv2.imshow("preview", cam.read()[1])
			cv2.waitKey(20)

		cv2.destroyWindow("preview")
		key_listener.stop()
	else:
		for _ in range(int(cam.get(cv2.CAP_PROP_FPS) * calibration_delay)):
			cam.read()

	_, img = cam.read()
	cam.release()
	return img


def _capture_thread() -> None:
	while (args := capture_thread_input.get()) is not None:
		camera, delay, return_queue = args
		return_queue.put(_capture(camera, delay))


Thread(target=_capture_thread, name="Capture thread").start()
