from threading import Thread
from time import sleep
from typing import Callable

from config import CFG
from controller import controller as cont

if CFG["web"]["host"] != "localhost":
	import RPi.GPIO as GPIO
	from hw.control import mc


_BUTTONS = {
	"rewind": (23, lambda _: cont.rewind()),
	"play/pause": (24, lambda _: cont.scan_play_pause()),
	"fast-forward": (25, lambda _: cont.fast_forward()),
	"help": (8, lambda _: cont.help()),
	"stop": (7, lambda _: cont.stop_scan())
}


def setup_buttons() -> None:
	GPIO.setmode(GPIO.BCM)

	# buttons
	for key in _BUTTONS.keys():
		_setup_button(*_BUTTONS[key])

	# volume dial
	Thread(target=_check_volume_dial, daemon=True).start()


def _setup_button(pin: int, callback: Callable) -> None:
	GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(pin, GPIO.RISING, callback=callback, bouncetime=500)


def _check_volume_dial() -> None:
	while True:
		if (diff := mc.read_encoder(4)) != 0:
			cont.volume += diff * 0.03

		sleep(1)
