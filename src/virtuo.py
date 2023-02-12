from datetime import datetime
import os
from threading import Thread

from config import CFG
from hw.flipper import flip_page
from ocr.camera import Camera, take_photo
from audio.audio_player import player
from audio.tts import tts
from ocr.img_to_text import get_text


def start_listeners() -> None:
	print("Controls:\nDigitize book: 'B'\nPlay/Pause: 'S'\nRewind 10s: 'A'\nFast-forward 10s: 'D'\nVolume up 10%: 'W'\nVolume down 10%: 'X'\nQuit: 'Q'\n")

	started = False

	while True:
		if (i := input("Cmd: ").lower()) == "b":
			# digitize book
			scan_book()
		elif i == "s":
			# play/pause
			if not started:
				scan_book(True)
				started = True
			else:
				player.play_pause()
		elif i == "a":
			# rewind
			pass
		elif i == "d":
			# fast-forward
			pass
		elif i == "w":
			# volume up
			player.volume_plus()
		elif i == "x":
			# volume down
			player.volume_minus()
		elif i == "q":
			# quit
			break


def scan_book(play_audio: bool = False) -> None:
	def scan() -> None:
		book_dir = os.path.join(CFG["book_location"], datetime.isoformat(datetime.now()))
		os.makedirs(book_dir)

		with open(os.path.join(book_dir, "book.txt"), "a") as f:
			page_nr = 0
			cameras = (Camera.left, Camera.right)
			last_sentence = ""

			while True:
				cam = cameras[page_nr % 2]
				text, last_sentence = get_text(take_photo(cam), book_dir, page_nr, last_sentence)
				f.write(text + last_sentence)

				if play_audio:
					audio = tts(text)
					if page_nr == 0:
						player.play(audio, background=True)
					else:
						player.add_audio(audio)

				if cam == Camera.right:
					if not flip_page():
						break

				page_nr += 1

	#Thread(target=scan, name="Book scan thread", daemon=True).start()
	scan()


if __name__ == "__main__":
	start_listeners()
