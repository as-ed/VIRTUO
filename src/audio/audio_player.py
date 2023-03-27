import io
import os
import re
from tempfile import NamedTemporaryFile
from time import sleep

import ffmpeg
from mpv import MPV
from mutagen.mp3 import EasyMP3
from pydub import AudioSegment

from config import CFG


class AudioPlayer:

	_SAMPLE_RATE = 24000
	_CHANNELS = 1

	def __init__(self, volume: float) -> None:
		self._player = MPV(ytdl=False)
		self._current_book = None
		self._playlist_duration = [0.0]

		self.volume = volume

	def play(self, book: str, pos: float = None) -> None:
		self._player.stop()
		if self._player.pause:
			self._player.cycle("pause")

		self._current_book = os.path.join(CFG["book_location"], book)

		for mp3 in sorted(filter(lambda f: f.is_file(), os.scandir(os.path.join(self._current_book, "audio"))), key=lambda f: int(f.name[:-4])):
			self._add_to_playlist(mp3.name)

		if pos is not None:
			self.seek(pos)

	def play_file(self, file: str) -> None:
		self._player.play(file)
		self._player.wait_for_playback()

	def add_audio(self, audio: bytes, fmt: str, page: int, play: bool) -> None:
		self.write_to_file(audio, fmt, self._current_book, page)
		self._add_to_playlist(f"{page}.mp3", play)

	def _add_to_playlist(self, file: str, play: bool = False) -> None:
		path = os.path.join(self._current_book, "audio", file)

		_, out = ffmpeg.input(path).output("-", f="null").run(capture_stderr=True)
		match = re.search("time=(?P<hours>\\d{2}):(?P<minutes>\\d{2}):(?P<seconds>\\d{2}.\\d{2})[^\r]+$", out.decode())
		self._playlist_duration.append(self._playlist_duration[-1] + 3600 * int(match["hours"]) + 60 * int(match["minutes"]) + float(match["seconds"]))

		self._player.playlist_append(path, keep_open="", keep_open_pause="no")

		if play and self._player.playlist_count == 1:
			self._player.playlist_pos = 0

	@staticmethod
	def write_to_file(audio: bytes, fmt: str, book: str, page: int) -> None:
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

	def resume(self) -> None:
		if self._player.pause:
			self._player.cycle("pause")

	def pause(self) -> None:
		if not self._player.pause:
			self._player.cycle("pause")

	def stop(self) -> None:
		self._player.stop()#keep_playlist="yes")

	def quit(self) -> None:
		self._player.stop()
		self._current_book = None
		self._playlist_duration = [0.0]

	@staticmethod
	def join_mp3s(book: str) -> None:
		with NamedTemporaryFile("wt") as f:
			f.write("\n".join(f"file '{file.path}'" for file in sorted(os.scandir(os.path.join(book, "audio")), key=lambda file: int(file.name[:-4]))))
			f.flush()
			os.fsync(f.fileno())
			ffmpeg.input(f.name.encode(), f="concat", safe=0).output(os.path.join(book, "book.mp3"), c="copy").run(overwrite_output=True, quiet=True)

	def rewind(self) -> None:
		if self.file_pos >= 10:
			self._player.seek(-10)
		elif self._player.playlist_pos == 0:
			self._player.seek(0, "absolute")
		else:
			seek_amount = 10 - self.file_pos
			self._player.playlist_prev()
			self._safe_seek(self._current_file_duration() - seek_amount)

	def fast_forward(self) -> None:
		duration_remaining = self._current_file_duration() - self.file_pos

		if duration_remaining >= 10:
			self._player.seek(10)
		elif self._player.playlist_pos == self._player.playlist_count - 1:
			self._player.seek(duration_remaining + 1, "absolute")
		else:
			self._player.playlist_next()
			self._safe_seek(10 - duration_remaining)

	def seek(self, pos: float) -> None:
		if 0 <= pos < self._playlist_duration[-1]:
			self._player.playlist_pos = next(i - 1 for i, d in enumerate(self._playlist_duration) if d > pos)
			self._safe_seek(pos - self._playlist_duration[self._player.playlist_pos])

	def _safe_seek(self, pos: float) -> None:
		success = False
		while not success:
			try:
				while self._player.core_idle or self._player.seeking:
					sleep(0.01)
				self._player.seek(pos)
				success = True
			except SystemError:
				pass

	def _current_file_duration(self) -> float:
		return self._playlist_duration[self.playlist_pos + 1] - self._playlist_duration[self.playlist_pos]

	@property
	def active(self) -> bool:
		return (pos := self._player.playlist_pos) is not None and pos >= 0

	@property
	def paused(self) -> bool:
		return self._player.pause

	@property
	def volume(self) -> float:
		return self._player.volume / 100

	@volume.setter
	def volume(self, volume: float) -> None:
		self._player.volume = volume * 100

	@property
	def playlist_pos(self) -> int:
		return self._player.playlist_pos

	@property
	def file_pos(self) -> float:
		return self._player.time_pos

	@property
	def total_pos(self) -> float:
		return self._playlist_duration[self.playlist_pos] + self.file_pos if self.active else 0

	@property
	def eop_reached(self) -> bool:
		return self.playlist_pos == self._player.playlist_count - 1 and self._player.eof_reached
