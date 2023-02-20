from typing import Optional, List

from google.oauth2 import service_account
import google.cloud.texttospeech as gtts
import requests
from requests import ConnectionError, Timeout

from config import CFG


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
		:return: The audio data
		"""
		if self._offline or not self._test_connection() or (audio := self._gtts(text)) is None:
			audio = self._picotts(text)

		return audio

	def synthesize_long(self, text: str) -> List[bytes]:
		# TODO implement
		pass

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
		# TODO add Pico TTS
		pass

	def set_voice(self, index: int) -> None:
		self._voice = CFG["audio"]["voices"][index]["voice_name"]
		self._language = CFG["audio"]["voices"][index]["language"]
		self._offline = CFG["audio"]["voices"][index]["offline"]

		if not self._offline:
			self._gtts_voice_params = gtts.VoiceSelectionParams(language_code=self._language, name=self._voice)


tts = _TTS()
