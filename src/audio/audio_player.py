import io
import os
import shutil
from threading import Thread

import ffmpeg
from mpv import MPV
from mutagen.mp3 import EasyMP3
from pydub import AudioSegment


class AudioPlayer:
	_SAMPLE_RATE = 24000
	_CHANNELS = 1

	def __init__(self, volume: float) -> None:
		self._player = MPV(ytdl=False)
		self._current_book = None

		self.volume = volume

	def play(self, audio: bytes, fmt: str, book: str, page: int = 0) -> None:
		self.stop()
		if self._player.pause:
			self._player.cycle("pause")

		self._current_book = os.path.join(book)
		os.makedirs(self._current_book, exist_ok=True)
		self.add_audio(audio, fmt, page)

		self._player.loadfile(os.path.join(self._current_book, "audio", "0.mp3"), keep_open="", keep_open_pause="no")

	def add_audio(self, audio: bytes, fmt: str, page: int) -> None:
		self.write_to_file(audio, fmt, self._current_book, page)
		self._player.playlist_append(os.path.join(self._current_book, "audio", f"{page}.mp3"), keep_open="", keep_open_pause="no")

	def write_to_file(self, audio: bytes, fmt: str, book: str, page: int) -> None:
		path = os.path.join(book, "audio", f"{page}.mp3")

		if fmt == "mp3":
			with open(path, "wb") as f:
				f.write(audio)
		elif fmt == "wav":
			with open(path, "wb") as f:
				tmp = io.BytesIO()
				AudioSegment.from_wav(io.BytesIO(audio)).set_channels(AudioPlayer._CHANNELS).set_frame_rate(AudioPlayer._SAMPLE_RATE).export(tmp, format="mp3")
				tmp.seek(0)
				EasyMP3(tmp)
				f.write(tmp.read())
		else:
			raise Exception(f"invalid audio format \"{fmt}\"")

	def play_pause(self) -> bool:
		self._player.cycle("pause")

		return not self._player.pause

	def stop(self) -> None:
		self._player.stop()

		if self._current_book is not None:
			Thread(target=self.raw_to_mp3, args=(self._current_book,)).start()

		self._current_book = None

	def raw_to_mp3(self, file: str) -> None:
		ffmpeg.input(file, f="s16le", ar=AudioPlayer._SAMPLE_RATE, ac=AudioPlayer._CHANNELS).output(file[:-3] + "mp3.part", f="mp3").run(overwrite_output=True)
		shutil.move(file[:-3] + "mp3.part", file[:-3] + "mp3")

	def rewind(self) -> None:
		self._player.seek(-10)

	def fast_forward(self) -> None:
		self._player.seek(10)

	@property
	def active(self) -> bool:
		return self._player.playlist_pos >= 0

	@property
	def paused(self) -> bool:
		return self._player.pause

	@property
	def volume(self) -> float:
		return self._player.volume / 100

	@volume.setter
	def volume(self, volume: float) -> None:
		self._player.volume = volume * 100
