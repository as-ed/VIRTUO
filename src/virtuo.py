from config import CFG
from ocr.camera import init_camera
from server import server


if __name__ == "__main__":
	#restore_settings()
	#init_camera()
	# TODO start listening for button presses
	server.run(host=CFG["web"]["host"], port=CFG["web"]["port"], debug=CFG["web"]["host"] == "localhost")
