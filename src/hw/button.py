from typing import Callable

from config import CFG
from controller import controller as cont

if CFG["web"]["host"] != "localhost":
	import RPi.GPIO as GPIO


_BUTTONS = {
	"rewind": (23, lambda _: cont.rewind()),
	"play/pause": (24, lambda _: cont.scan_play_pause()),
	"fast-forward": (25, lambda _: cont.fast_forward()),
	"help": (8, lambda _: cont.help()),
	"stop": (7, lambda _: cont.stop_scan())
}


def setup_buttons() -> None:
	GPIO.setmode(GPIO.BCM)

	for key in _BUTTONS.keys():
		_setup_button(*_BUTTONS[key])


def _setup_button(pin: int, callback: Callable) -> None:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(pin, GPIO.RISING, callback=callback, bouncetime=300)
