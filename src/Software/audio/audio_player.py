import io
from queue import SimpleQueue, Empty
from typing import Union, List

from mpv import MPV
import soundfile as sf


class _AudioPlayer:
	_DEFAULT_VOLUME = 1
	_SENTINEL = object()

	def __init__(self) -> None:
		self._player = MPV(ytdl=False)
		self._stream = None
		self._stream_queue = SimpleQueue()

		self._player.volume = _AudioPlayer._DEFAULT_VOLUME * 100

	def play(self, audio: Union[str, bytes], timestamp: float = 0, background: bool = True) -> None:
		self._player.stop()
		self._stream_queue.put(_AudioPlayer._SENTINEL)
		if self._player.pause:
			self._player.cycle("pause")

		if isinstance(audio, bytes):
			if self._stream is not None:
				self._stream.unregister()

			self._stream_queue = SimpleQueue()
			self.add_audio(audio)

			@self._player.python_stream("stream")
			def stream() -> bytes:
				while True:
					if (frames := self._stream_queue.get()) == _AudioPlayer._SENTINEL:
						return

					with frames as f:
						while data := f.read(1024**2):
							yield data
						yield b""
						yield b""

			self._stream = stream
			audio_loc = "python://stream"
		else:
			audio_loc = audio

		self._player.loadfile(audio_loc, keep_open="", keep_open_pause="no", no_video="", start=timestamp)

		if not background:
			self._player.wait_for_playback()

	def add_audio(self, audio: bytes) -> None:
		data, rate = sf.read(io.BytesIO(audio))
		audio_bytes = io.BytesIO()
		sf.write(audio_bytes, data, samplerate=rate, format="FLAC")
		audio_bytes.seek(0)
		self._stream_queue.put(audio_bytes)

	def play_pause(self) -> bool:
		self._player.cycle("pause")

		return not self._player.pause

	@property
	def volume(self) -> float:
		return self._player.volume / 100

	def volume_plus(self) -> bool:
		if self._player.volume >= 100:
			return False

		self._player.volume = 100 if self._player.volume >= 90 else self._player.volume + 10
		return True

	def volume_minus(self) -> bool:
		if self._player.volume <= 0:
			return False

		self._player.volume = 1 if self._player.volume <= 11 else self._player.volume - 10


player = _AudioPlayer()
