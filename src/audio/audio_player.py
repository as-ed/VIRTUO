import io
import os
from queue import SimpleQueue
from typing import Union, List

from mpv import MPV
import numpy as np
import soundfile as sf


# TODO store MP3, rewind, fast-forward


class _AudioPlayer:
	_DEFAULT_VOLUME = 0.5
	_SENTINEL = object()

	def __init__(self) -> None:
		self._player = MPV(ytdl=False)
		self._stream = None
		self._stream_queue = SimpleQueue()
		self._current_playback = []
		self._current_playback_rate = None

		self.volume = _AudioPlayer._DEFAULT_VOLUME

	def play(self, audio: Union[str, bytes], timestamp: float = 0, background: bool = True) -> None:
		self.stop()
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
		# encode audio as FLAC
		data, rate = sf.read(io.BytesIO(audio))
		audio_bytes = io.BytesIO()
		sf.write(audio_bytes, data, samplerate=rate, format="FLAC")
		audio_bytes.seek(0)
		self._stream_queue.put(audio_bytes)

		# store audio
		self._current_playback.append(data)
		self._current_playback_rate = rate

	def play_pause(self) -> bool:
		self._player.cycle("pause")

		return not self._player.pause

	def stop(self, store_audio_path: str = None) -> None:
		self._player.stop()

		if store_audio_path is not None and self._current_playback != []:
			sf.write(os.path.join(store_audio_path, "book.mp3"), np.concatenate(self._current_playback), samplerate=self._current_playback_rate, format="MP3")

		self._current_playback = []

	def store_as_mp3(self, path: str, audio: List[bytes]):
		_, rate = sf.read(io.BytesIO(audio[0]))
		data = np.concatenate([sf.read(a)[0] for a in audio])
		sf.write(os.path.join(path, "book.mp3"), data, samplerate=rate, format="MP3")

	@property
	def volume(self) -> float:
		return self._player.volume / 100

	@volume.setter
	def volume(self, volume: float) -> None:
		self._player.volume = volume * 100


player = _AudioPlayer()
