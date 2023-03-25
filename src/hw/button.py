from typing import Callable

from config import CFG
from controller import controller as cont

if CFG["web"]["host"] != "localhost":
	import RPi.GPIO as GPIO


_BUTTONS = {
	"rewind": (23, cont.rewind),
	"play/pause": (24, cont.scan_play_pause),
	"fast-forward": (25, cont.fast_forward),
	"stop": (8, cont.stop_scan),
	"help": (7, cont.help)
}


def setup_buttons() -> None:
	GPIO.setmode(GPIO.BCM)

	for pin, callback in _BUTTONS.values():
		_setup_button(pin, callback)


def _setup_button(pin: int, callback: Callable) -> None:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(pin, GPIO.RISING)
	GPIO.add_event_callback(pin, callback)
