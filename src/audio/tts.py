from typing import Optional, List, Generator

from google.oauth2 import service_account
import google.cloud.texttospeech as gtts
from nltk.tokenize import sent_tokenize
import requests
from requests import ConnectionError, Timeout

from config import CFG

from subprocess import call
import wave
import os


class _TTS:

	def __init__(self) -> None:
		self._voice = None
		self._language = None
		self._offline = None
		self._gtts_voice_params = None
		self.set_voice(0)
		self._gtts_client = gtts.TextToSpeechClient(credentials=service_account.Credentials.from_service_account_info(CFG["credentials"]["google_cloud"]))
		self._gtts_audio_config = gtts.AudioConfig(audio_encoding=gtts.AudioEncoding.LINEAR16)

	def synthesize(self, text: str) -> bytes:
		"""
		Synthesizes speech from given text.

		:param text: Text to synthesize, must not be longer than 5000 characters.
		:return: Wave audio data.
		"""
		if self._offline or not self._test_connection() or (audio := self._gtts(text)) is None:
			audio = self._picotts(text)

		return audio

	def synthesize_long(self, text: str) -> Generator[bytes, None, None]:
		if len(text) <= 5000:
			yield self.synthesize(text)
			return

		current_chunk = ""

		for sentence in sent_tokenize(text):
			while len(current_chunk) + len(sentence) <= 5000:
				current_chunk += sentence

			yield self.synthesize(current_chunk)
			current_chunk = sentence

	def _gtts(self, text: str) -> Optional[bytes]:
		text_input = gtts.SynthesisInput(text=text)
		try:
			response = self._gtts_client.synthesize_speech(input=text_input, voice=self._gtts_voice_params, audio_config=self._gtts_audio_config, timeout=10)
			return response.audio_content
		except Exception:
			pass

	def _test_connection(self) -> bool:
		try:
			requests.head("http://1.1.1.1", timeout=2)
			return True
		except (ConnectionError, Timeout):
			return False

	def _picotts(self, text: str) -> bytes:

		f = open("input.txt", "w")
		f.write(text)
		f.close()

		call(["pico2wave -l en-GB -w output.wav \"" + text + "\""], shell=True)

		while not os.path.exists("output.wav"):
			time.sleep(5)

		frames = wave.open("output.wav").readframes(100000000000000000)
		os.remove("output.wav")

		return frames

	def set_voice(self, index: int) -> None:
		self._voice = CFG["audio"]["voices"][index]["voice_name"]
		self._language = CFG["audio"]["voices"][index]["language"]
		self._offline = CFG["audio"]["voices"][index]["offline"]

		if not self._offline:
			self._gtts_voice_params = gtts.VoiceSelectionParams(language_code=self._language, name=self._voice)


tts = _TTS()
