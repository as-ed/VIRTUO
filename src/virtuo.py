from argparse import ArgumentParser
from signal import signal, SIGINT
import sys

from config import CFG
from controller import controller as cont
from hw.button import setup_buttons
from hw.flipper import load_position, rest_position, stop_motors, turn_on_lights
from ocr.camera import init_camera
from server import server


def _sigint_handler(*_) -> None:
	rest_position()
	stop_motors()
	sys.exit(0)


if __name__ == "__main__":
	parser = ArgumentParser(
		prog="VIRTUO",
		usage="virtuo.py [options]",
		description="Start the VIRTUO application")
	parser.add_argument(
		"-v",
		"--version",
		action="version",
		version="%(prog)s version 0.1")
	parser.add_argument(
		"-t",
		"--test",
		action="store_true",
		help="Enable testing mode. Uses hardcoded text instead of scanning pages.")

	signal(SIGINT, _sigint_handler)

	args = parser.parse_args()

	if args.test:
		cont.test_mode = True
	else:
		rest_position()

		if init_camera():
			cont.cams_inited = True
		else:
			print("Cameras not connected")

		load_position()

		if CFG["web"]["host"] != "localhost":
			setup_buttons()

	server.run(host=CFG["web"]["host"], port=CFG["web"]["port"], debug=args.test)
