from datetime import datetime
import json
from json import JSONDecodeError
import os
from queue import SimpleQueue
import re
from threading import Thread, Event, Lock
from time import sleep
from typing import List, Optional, Any, Dict, Union

from audio.audio_player import AudioPlayer
from audio.tts import TTS
from config import CFG, settings
from hw.flipper import flip_page
from ocr.camera import Camera, take_photo, init_camera
from ocr.img_to_text import get_text


class _Controller:

	TEXT_FILE = "book.txt"
	METADATA_FILE = "metadata.json"

	def __init__(self) -> None:
		self._scanning = None
		self._listening = False
		self._player = AudioPlayer(settings["volume"])
		self._help_player = AudioPlayer(settings["volume"])
		self._tts = TTS(settings["voice"], settings["offline_voice"])
		self._metadata = {}
		self.metadata_lock = Lock()
		self._stop_event = Event()
		self._scan_thread = None
		self._scan_start_stop_lock = Lock()
		self.audio_queue = SimpleQueue()
		self.test_mode = False
		self.cams_inited = False
		self._page_flip_error = 0
		self._manual_flip_confirm = Event()

		self._books = []
		for book_dir in os.scandir(CFG["book_location"]):
			if not book_dir.is_dir():
				continue

			book = {"id": book_dir.name}

			with self.metadata_lock, open(os.path.join(book_dir.path, _Controller.METADATA_FILE)) as f:
				try:
					metadata = json.load(f)
				except JSONDecodeError:
					continue

			book["title"] = metadata["title"] if "title" in metadata else ""
			book["author"] = metadata["author"] if "author" in metadata else ""
			book["time"] = datetime.fromtimestamp(metadata["scan_time"]).strftime("%Y-%m-%d\u00a0\u00a0\u00a0%H:%M")
			book["pages"] = metadata["pages"]

			self._books.append(book)

		self._books.sort(key=lambda b: b["time"])

	def scan(self, listen: bool, book: str = None) -> Optional[str]:
		if not self.cams_inited:
			init_camera()
			self.cams_inited = True

		with self._scan_start_stop_lock:
			if self._scanning is None:
				# not already scanning book
				if book is None:
					# create new book
					book = self._new_book()
					listened_up_to = 0
				else:
					with self.metadata_lock, open(os.path.join(CFG["book_location"], book, _Controller.METADATA_FILE)) as f:
						self._metadata = json.load(f)
						listened_up_to = 0 if self._metadata["listened_up_to"] < 5 else self._metadata["listened_up_to"] - 5

				# start scanning thread
				self._scanning = book
				self._listening = listen
				self._scan_thread = Thread(target=self._scan, args=(book,), name="Book scan thread")
				self._help_player.stop()
				self._player.play(book, listened_up_to if listen else None)
				self._scan_thread.start()

				return book
			elif book is None:
				try:
					os.remove(os.path.join(CFG["book_location"], self._scanning, "book.pdf"))
				except FileNotFoundError:
					pass

				try:
					os.remove(os.path.join(CFG["book_location"], self._scanning, "book.epub"))
				except FileNotFoundError:
					pass

				try:
					os.remove(os.path.join(CFG["book_location"], self._scanning, "book.mp3"))
				except FileNotFoundError:
					pass

				listened_up_to = 0 if self._metadata["listened_up_to"] < 5 else self._metadata["listened_up_to"] - 5

				if not self._listening and listen:
					self._listening = listen
					self._help_player.stop()
					self._player.seek(listened_up_to)
				elif self.playing:
					self._listening = listen
					with self.metadata_lock, open(os.path.join(CFG["book_location"], self._scanning, _Controller.METADATA_FILE), "w") as f:
						self._metadata["listened_up_to"] = self._player.total_pos
						json.dump(self._metadata, f)
					self._player.stop()

				return self._scanning

	def stop_scan(self) -> bool:
		self._help_player.stop()

		if self._scanning is not None:
			self._stop_event.set()
			self._scan_thread.join()

			self._stop_event.clear()
			self._scan_thread = None

			return True

		return False

	def scan_play_pause(self) -> None:
		if self._page_flip_error != 0:
			self.clear_page_flip_error()
			return

		if self._scanning is None or not self._listening:
			self.scan(True)
		else:
			self.toggle_pause()

	def toggle_pause(self) -> bool:
		return self._player.play_pause() and self._player.active

	def pause(self) -> None:
		self._player.pause()

	def rewind(self) -> None:
		self._player.rewind()

	def fast_forward(self) -> None:
		self._player.fast_forward()

	def seek(self, pos) -> None:
		self._player.seek(pos)

	def set_book_attribute(self, book: str, attribute: str, value: Any) -> bool:
		if not os.path.isdir(os.path.join(CFG["book_location"], book)):
			return False

		path = os.path.join(CFG["book_location"], book, "metadata.json")

		with self.metadata_lock:
			with open(path) as f:
				metadata = json.load(f)

			metadata[attribute] = value

			with open(path, "w") as f:
				json.dump(metadata, f)

			if attribute in ("title", "author"):
				[b for b in self._books if b["id"] == book][0][attribute] = value

		return True

	def help(self) -> None:
		self._help_output("static/help.mp3")

	def clear_page_flip_error(self) -> None:
		self._manual_flip_confirm.set()

	def last_page(self, book: str) -> int:
		with self.metadata_lock, open(os.path.join(CFG["book_location"], book, _Controller.METADATA_FILE)) as f:
			return metadata["last_page"] if "last_page" in (metadata := json.load(f)) else -1

	def add_wifi(self, ssid: str, password: str) -> None:
		with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as f:
			f.write(_WPA_NETWORK.format(ssid, password))

	@property
	def books(self) -> List[Dict]:
		return self._books

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
	def playback_pos(self) -> float:
		return self._player.total_pos

	@property
	def page_flip_error(self) -> int:
		return self._page_flip_error

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
		self._help_player.volume = volume
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

	def _help_output(self, file: str) -> None:

		if was_playing := self.playing:
			self.pause()

		sleep(1)
		self._help_player.play_file(file)
		sleep(1)

		if was_playing:
			self.seek(self.playback_pos - 5)
			self.toggle_pause()

	def _new_book(self) -> str:
		now = datetime.now()
		date = datetime.isoformat(now)[:10]
		num = len(list(filter(lambda b: re.match(date + r" - (\d*)", b), os.listdir(CFG["book_location"])))) + 1
		book_dir = f"{date} - {num}"
		book_path = os.path.join(CFG["book_location"], book_dir)
		os.makedirs(os.path.join(book_path, "audio"))

		open(os.path.join(book_path, _Controller.TEXT_FILE), "w").close()

		with self.metadata_lock, open(os.path.join(book_path, _Controller.METADATA_FILE), "w") as f:
			self._metadata = {"scan_time": datetime.timestamp(now), "pages": 0, "last_sentence": "", "listened_up_to": 0}
			json.dump(self._metadata, f)

		self._books.append({"id": book_dir, "title": "", "author": "", "time": now.strftime("%Y-%m-%d\u00a0\u00a0\u00a0%H:%M"), "pages": 0})

		return book_dir

	def _scan(self, book: str) -> None:
		book_path = os.path.join(CFG["book_location"], book)

		cameras = (Camera.left, Camera.right)
		last_page = False
		page_nr = None
		last_edge_pos = 1
		current_book_dict = [b for b in self._books if b["id"] == book][0]

		while not last_page and not self._stop_event.is_set():
			# OCR
			cam = cameras[self._metadata["pages"] % 2]

			for i in range(2):
				ocr_result = get_text(None if self.test_mode else take_photo(cam), book_path, cam, self._metadata["pages"], self._metadata["last_sentence"], self.test_mode)

				# check if end of book reached
				if ocr_result is None:
					text = " " + self._metadata["last_sentence"]
					self._metadata["last_sentence"] = ""
					last_page = True
					break

				text, self._metadata["last_sentence"], new_page_nr, edge_pos = ocr_result

				# check if page flip was successful
				if cam == Camera.left:
					if page_nr is None or new_page_nr == page_nr + 1:
						page_nr = new_page_nr
						break

					# check for error in OCR page number detection
					if new_page_nr < page_nr or new_page_nr > page_nr + 5 or (new_page_nr - page_nr) % 2 == 0:
						page_nr += 1
						break

					# no page flipped
					if new_page_nr == page_nr:
						flip_page(last_edge_pos)
						continue

					# multiple pages flipped at once
					num_pages = (new_page_nr - page_nr) // 2
					self._help_output(f"static/flip_back_{num_pages}.mp3")
					self._manual_flip_confirm.clear()
					self._page_flip_error = num_pages
					self._manual_flip_confirm.wait()
					self._page_flip_error = 0
				else:
					if page_nr is not None:
						page_nr += 1

					last_edge_pos = 1 if edge_pos is None else edge_pos
					flip_page(last_edge_pos)
					break

			# TTS
			audio, fmt = self._tts.synthesize(text)
			self._player.add_audio(audio, fmt, self._metadata["pages"], self._listening)

			# write book text
			with open(os.path.join(book_path, _Controller.TEXT_FILE), "a") as f:
				f.write(text)

			# update metadata
			self._metadata["pages"] = current_book_dict["pages"] = self._metadata["pages"] + 1
			with self.metadata_lock, open(os.path.join(book_path, _Controller.METADATA_FILE), "w") as f:
				json.dump(self._metadata, f)

		# wait until stop or playback is done
		while not self._stop_event.is_set() and self._listening and not self._player.eop_reached:
			sleep(0.5)

		with self._scan_start_stop_lock:
			self._scanning = None
			self._listening = False

			if self.playing:
				self._metadata["listened_up_to"] = self._player.total_pos
				with self.metadata_lock, open(os.path.join(book_path, _Controller.METADATA_FILE), "w") as f:
					json.dump(self._metadata, f)

			self._metadata = {}
			self._player.quit()


controller = _Controller()


_HELP_TEXT = "I am Virtuo, your accessible book scanning robot. I can scan your books and read them out to you. To have a book read to you just place it on top of the book tray and slide it forwards until it hits the stop. When placing the book on the tray, rotate it so that the top side faces towards you and the front cover is on the right side when opened. Open it up, slide the clipper mechanism over the book cover to secure it and flip down the clippers. Then open it up to the page where you want to start listening and press the play button. You can control the playback using the rewind and fast-forward buttons and the play button for pausing and resuming. To adjust the volume you can use the dial on the right hand side and to stop the scan or reset the robot to scan another book just press the reset button. You can access and manage a list of all your scanned books and access more advanced options like changing the voice or continuing previous scans, using the web interface. To access it, just connect any device with a web browser to the same WiFi network as the robot and visit http://virtuo.local, that is Victor, India, Romeo, Tango, Uniform, Oscar, dot, Lima, Oscar, Charlie, Alpha, Lima."

_WPA_NETWORK = """
network={{
	ssid="{}"
	psk="{}"
	scan_ssid=1
}}
"""
