from typing import Callable

from config import CFG
from controller import controller as cont

if CFG["web"]["host"] != "localhost":
	import RPi.GPIO as GPIO


_BUTTONS = {
	"rewind": (0, cont.rewind),
	"play/pause": (1, cont.scan_play_pause),
	"fast-forward": (2, cont.fast_forward),
	"stop": (3, cont.stop_scan),
	"help": (4, cont.help)
}


def setup_buttons() -> None:
	GPIO.setmode(GPIO.BCM)

	for pin, callback in _BUTTONS.values():
		_setup_button(pin, callback)


def _setup_button(pin: int, callback: Callable) -> None:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(pin, GPIO.RISING)
	GPIO.add_event_callback(pin, callback)
