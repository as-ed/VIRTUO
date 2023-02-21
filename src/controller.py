from datetime import datetime
import json
import os
import re
from threading import Thread, Event, Lock
from typing import List

from audio.audio_player import player
from audio.tts import tts
from config import CFG, settings
from hw.flipper import flip_page
from ocr.camera import Camera, take_photo
from ocr.img_to_text import get_text


_scanning = Lock()
_playing = False
_stop_scan_event = Event()


def scan(play_audio: bool = False) -> bool:
	def scan() -> None:
		global _playing

		# create book directory
		date = datetime.isoformat(datetime.now())[:10]
		num = len(list(filter(lambda b: re.match(date + r" - (\d*)", b), os.listdir(CFG["book_location"])))) + 1
		book_dir = os.path.join(CFG["book_location"], f"{date} - {num}")
		os.makedirs(book_dir)

		# scan book
		with open(os.path.join(book_dir, "book.txt"), "a") as book, open(os.path.join(book_dir, "metadata.json"), "w") as metadata:
			page_nr = 0
			cameras = (Camera.left, Camera.right)
			last_sentence = ""
			metadata_dict = {"scan_time": datetime.timestamp(datetime.now()), "pages": 0}

			while not _stop_scan_event.is_set():
				# OCR
				cam = cameras[page_nr % 2]
				text, last_sentence = get_text(take_photo(cam), book_dir, page_nr, last_sentence)

				# TTS
				if play_audio:
					audio = tts.synthesize(text)
					if page_nr == 0:
						_playing = True
						player.play(audio, book_dir)
					else:
						player.add_audio(audio)

				# page flipping
				if cam == Camera.right:
					if not flip_page():
						break

				# write book text
				book.write(text + last_sentence)

				# update metadata
				page_nr += 1
				metadata_dict["pages"] = page_nr
				metadata.seek(0)
				json.dump(metadata_dict, metadata)

				# flush data to disk
				book.flush()
				metadata.flush()
				os.fsync(book.fileno())
				os.fsync(metadata.fileno())

		_scanning.release()
		_playing = False
		player.stop()

	if _scanning.acquire(False):
		_stop_scan_event.clear()
		Thread(target=scan, name="Book scan thread", daemon=True).start()
		return True
	else:
		return False


def stop_scan() -> None:
	_stop_scan_event.set()


def toggle_pause() -> bool:
	return player.play_pause() and _playing


def set_volume(volume: float) -> bool:
	if 0 <= volume <= 1:
		player.volume = settings["volume"] = volume
		return True
	else:
		return False


def rewind() -> None:
	player.rewind()


def fast_forward() -> None:
	player.fast_forward()


def get_voices() -> List[str]:
	return [voice["name"] for voice in CFG["audio"]["voices"]]


def get_current_voice() -> str:
	return settings["voice"] if "voice" in settings else CFG["audio"]["voices"][0]["name"]


def set_voice(voice: str) -> bool:
	if voice in [v["name"] for v in CFG["audio"]["voices"]]:
		tts.set_voice(_get_voice_index(voice))
		settings["voice"] = voice
		return True
	else:
		return False


def restore_settings() -> None:
	if "volume" in settings:
		player.volume = settings["volume"]

	if "voice" in settings:
		tts.set_voice(_get_voice_index(settings["voice"]))


def _get_voice_index(voice: str) -> int:
	return [i for i, v in enumerate(CFG["audio"]["voices"]) if v["name"] == voice][0]
