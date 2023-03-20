from argparse import ArgumentParser

from config import CFG
from controller import controller as cont
from ocr.camera import init_camera
from server import server


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

	if parser.parse_args().test:
		cont.test_mode = True
	else:
		pass
		#init_camera()

	# TODO start listening for button presses

	server.run(host=CFG["web"]["host"], port=CFG["web"]["port"], debug=False)#CFG["web"]["host"] == "localhost")
