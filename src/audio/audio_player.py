import io
import os
import shutil
from threading import Thread

import ffmpeg
from mpv import MPV
from pydub import AudioSegment


class _AudioPlayer:
	_DEFAULT_VOLUME = 0.5
	_SAMPLE_RATE = 24000
	_CHANNELS = 1

	def __init__(self) -> None:
		self._player = MPV(ytdl=False)
		self._current_book = None

		self.volume = _AudioPlayer._DEFAULT_VOLUME

	def play(self, audio: bytes, book: str) -> None:
		self.stop()
		if self._player.pause:
			self._player.cycle("pause")

		self._current_book = os.path.join(book, "book.raw")
		self.add_audio(audio, True)

		self._player.loadfile(self._current_book, keep_open="", keep_open_pause="no", demuxer="rawaudio", demuxer_rawaudio_format="s16le", demuxer_rawaudio_channels=1, demuxer_rawaudio_rate=24000)

	def add_audio(self, audio: bytes, overwrite: bool = False) -> None:
		self.write_to_raw_file(audio, self._current_book, overwrite)

		if self._player.eof_reached:
			self._player.seek(0)

	def write_to_raw_file(self, audio: bytes, file: str, overwrite: bool) -> None:
		with open(file, "wb" if overwrite else "ab") as f:
			AudioSegment.from_wav(io.BytesIO(audio)).set_channels(_AudioPlayer._CHANNELS).set_frame_rate(_AudioPlayer._SAMPLE_RATE).export(f, format="raw")

	def play_pause(self) -> bool:
		self._player.cycle("pause")

		return not self._player.pause

	def stop(self) -> None:
		self._player.stop()

		if self._current_book is not None:
			Thread(target=self.raw_to_mp3, args=(self._current_book,), daemon=True).start()

		self._current_book = None

	def raw_to_mp3(self, file: str) -> None:
		ffmpeg.input(file, f="s16le", ar=_AudioPlayer._SAMPLE_RATE, ac=_AudioPlayer._CHANNELS).output(file[:-3] + "mp3.part", f="mp3").run(overwrite_output=True)
		shutil.move(file[:-3] + "mp3.part", file[:-3] + "mp3")

	def rewind(self) -> None:
		self._player.seek(-10)

	def fast_forward(self) -> None:
		self._player.seek(10)

	@property
	def volume(self) -> float:
		return self._player.volume / 100

	@volume.setter
	def volume(self, volume: float) -> None:
		self._player.volume = volume * 100


player = _AudioPlayer()
