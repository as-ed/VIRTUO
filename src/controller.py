from datetime import datetime
import json
import os
import re
from threading import Thread, Event, Lock
from typing import List, Optional, Tuple

from audio.audio_player import AudioPlayer
from audio.tts import TTS
from config import CFG, settings
from hw.flipper import flip_page
from ocr.camera import Camera, take_photo
from ocr.img_to_text import get_text


_scanning = Lock()
_playing = False
_stop_scan_event = Event()


class _Controller:

	def __init__(self) -> None:
		self._scanning = None
		self._player = AudioPlayer(settings["volume"])
		self._tts = TTS(settings["voice"], settings["offline_voice"])

	def scan(self, listen: bool, book: str = None) -> Optional[Tuple[str, datetime]]:
		return "abc", datetime.now()

	@property
	def scanning(self) -> Optional[str]:
		return self._scanning

	@property
	def listening(self) -> bool:
		return self._player.active

	@property
	def paused(self) -> bool:
		return self._player.paused

	@property
	def volume(self) -> float:
		return self._player.volume

	@volume.setter
	def volume(self, volume: float) -> float:
		if volume < 0:
			volume = 0
		elif volume > 1:
			volume = 1

		self._player.volume = volume
		settings["volume"] = volume

		return volume

	@property
	def voice(self) -> str:
		return CFG["audio"]["voices"][self._tts.voice]["name"]

	@voice.setter
	def voice(self, voice: str) -> None:
		if (ids := [i for i, v in enumerate(CFG["audio"]["voices"]) if v["name"] == voice]) == []:
			raise Exception(f"voice \"{voice}\" does not exist")

		self._tts.voice = ids[0]
		settings["voice"] = ids[0]

		if CFG["audio"]["voices"][ids[0]]["offline"]:
			self._tts.offline_voice = ids[0]
			settings["offline_voice"] = ids[0]

	@staticmethod
	def get_voices() -> List[str]:
		return [voice["name"] for voice in CFG["audio"]["voices"]]


controller = _Controller()

"""
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
			metadata.seek(0)
			json.dump(metadata_dict, metadata)
			metadata.flush()

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


def get_volume() -> float:
	return player.volume


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


def set_book_attribute(book, attribute, value) -> bool:
	if not os.path.isdir(os.path.join(CFG["book_location"], book)):
		return False

	path = os.path.join(CFG["book_location"], book, "metadata.json")

	with open(path) as f:
		metadata = json.load(f)

	metadata[attribute] = value

	with open(path, "w") as f:
		json.dump(metadata, f)

	return True


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
	return [i for i, v in enumerate(CFG["audio"]["voices"]) if v["name"] == voice][0]"""
