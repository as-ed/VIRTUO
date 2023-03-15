from datetime import datetime
import json
from json import JSONDecodeError
import os
from queue import SimpleQueue
import re
from threading import Thread, Event, Lock
from typing import List, Optional, Tuple, Any, Dict

from audio.audio_player import AudioPlayer
from audio.tts import TTS
from config import CFG, settings
from hw.flipper import flip_page
from ocr.camera import Camera, take_photo
from ocr.img_to_text import get_text


class _Controller:

	_TEXT_FILE = "book.txt"
	_METADATA_FILE = "metadata.json"

	def __init__(self) -> None:
		self._scanning = None
		self._listening = False
		self._player = AudioPlayer(settings["volume"])
		self._tts = TTS(settings["voice"], settings["offline_voice"])
		self._metadata_lock = Lock()
		self._stop_event = Event()
		self._scan_thread = None
		self._scan_start_stop_lock = Lock()
		self._tts_queue = SimpleQueue()

	def scan(self, listen: bool, book: str = None) -> Optional[Tuple[str, datetime]]:
		with self._scan_start_stop_lock:
			if self._scanning is None:
				# not already scanning book
				if book is None:
					# create new book
					book, time = self._new_book()
				else:
					with self._metadata_lock, open(os.path.join(CFG["book_location"], book, _Controller._METADATA_FILE)) as f:
						time = datetime.fromtimestamp(json.load(f)["scan_time"])

				# start scanning thread
				self._scan_thread = Thread(target=self._scan, args=(book,), name="Book scan thread")
				self._listening = listen
				self._scan_thread.start()
				Thread(target=self._generate_audio, name="TTS thread").start()

				return book, time
			elif book is None:
				self._listening = listen

				with self._metadata_lock, open(os.path.join(CFG["book_location"], self._scanning, _Controller._METADATA_FILE)) as f:
					time = datetime.fromtimestamp(json.load(f)["scan_time"])

				return self._scanning, time

	def stop_scan(self) -> Optional[Tuple[str, int]]:
		with self._scan_start_stop_lock:
			if self._scanning is not None:
				self._stop_event.set()
				self._scan_thread.join()

				self._stop_event.clear()
				self._scan_thread = None

				book = self._scanning
				with self._metadata_lock, open(os.path.join(CFG["book_location"], book, _Controller._METADATA_FILE)) as f:
					pages = json.load(f)["pages"]

				self._scanning = None
				self._listening = False

				if self.playing:
					self._player.stop()

				return book, pages

	def books(self) -> List[Dict]:
		books = []
		for book_dir in os.scandir(CFG["book_location"]):
			if not book_dir.is_dir():
				continue

			book = {"id": book_dir.name}

			with self._metadata_lock, open(os.path.join(book_dir.path, _Controller._METADATA_FILE)) as f:
				try:
					metadata = json.load(f)
				except JSONDecodeError:
					continue

			book["title"] = metadata["title"] if "title" in metadata else ""
			book["author"] = metadata["author"] if "author" in metadata else ""
			book["time"] = datetime.fromtimestamp(metadata["scan_time"])
			book["pages"] = metadata["pages"]

			books.append(book)

		return books

	def toggle_pause(self) -> bool:
		return self._player.play_pause() and self._player.active

	def rewind(self) -> None:
		self._player.rewind()

	def fast_forward(self) -> None:
		self._player.fast_forward()

	def set_book_attribute(self, book: str, attribute: str, value: Any) -> bool:
		if not os.path.isdir(os.path.join(CFG["book_location"], book)):
			return False

		path = os.path.join(CFG["book_location"], book, "metadata.json")

		with self._metadata_lock:
			with open(path) as f:
				metadata = json.load(f)

			metadata[attribute] = value

			with open(path, "w") as f:
				json.dump(metadata, f)

		return True

	def last_page(self, book: str) -> int:
		with self._metadata_lock, open(os.path.join(CFG["book_location"], book, _Controller._METADATA_FILE)) as f:
			return metadata["last_page"] if "last_page" in (metadata := json.load(f)) else -1

	@property
	def scanning(self) -> Optional[str]:
		return self._scanning

	@property
	def listening(self) -> bool:
		return self._listening

	@property
	def playing(self) -> bool:
		return self._player.active

	@property
	def paused(self) -> bool:
		return self._player.paused

	@property
	def volume(self) -> float:
		return self._player.volume

	@volume.setter
	def volume(self, volume: float) -> None:
		if volume < 0:
			volume = 0
		elif volume > 1:
			volume = 1

		self._player.volume = volume
		settings["volume"] = volume

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

	def _new_book(self) -> Tuple[str, datetime]:
		now = datetime.now()
		date = datetime.isoformat(now)[:10]
		num = len(list(filter(lambda b: re.match(date + r" - (\d*)", b), os.listdir(CFG["book_location"])))) + 1
		book_dir = f"{date} - {num}"
		book_path = os.path.join(CFG["book_location"], book_dir)
		os.makedirs(book_path)

		open(os.path.join(book_path, _Controller._TEXT_FILE), "w").close()

		with self._metadata_lock, open(os.path.join(book_path, _Controller._METADATA_FILE), "w") as f:
			json.dump({"scan_time": datetime.timestamp(now), "pages": 0, "last_sentence": ""}, f)

		return book_dir, now

	def _scan(self, book: str) -> None:
		book_path = os.path.join(CFG["book_location"], book)

		with self._metadata_lock, open(os.path.join(book_path, _Controller._METADATA_FILE)) as f:
			metadata = json.load(f)

		cameras = (Camera.left, Camera.right)

		while not self._stop_event.is_set():
			# OCR
			cam = cameras[metadata["pages"] % 2]
			text, metadata["last_sentence"] = get_text(take_photo(cam), book_path, metadata["pages"], metadata["last_sentence"])

			# page flipping
			if cam == Camera.right:
				if not flip_page():
					break

			# write book text
			with open(os.path.join(book_path, _Controller._TEXT_FILE), "a") as f:
				f.write(text)

			# update metadata
			metadata["pages"] += 1
			with self._metadata_lock, open(os.path.join(book_path, _Controller._METADATA_FILE), "w") as f:
				json.dump(metadata, f)

	def _generate_audio(self) -> None:
		pass


controller = _Controller()
