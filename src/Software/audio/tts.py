from google.oauth2 import service_account
import google.cloud.texttospeech as gtts

from config import CFG

_default_voice = CFG["audio"]["voices"]["google_tts"][CFG["audio"]["voices"]["google_default"]]
_VOICE_PARAMS = gtts.VoiceSelectionParams(language_code=_default_voice["language"], name=_default_voice["voice_name"])
_AUDIO_CONFIG = gtts.AudioConfig(audio_encoding=gtts.AudioEncoding.LINEAR16, speaking_rate=CFG["audio"]["voices"]["google_speaking_rate"])

_gtts_client = gtts.TextToSpeechClient(credentials=service_account.Credentials.from_service_account_info(CFG["credentials"]["google_cloud"]))


def tts(text: str) -> bytes:
	# use Google Cloud TTS to synthesis speech
	text_input = gtts.SynthesisInput(text=text)
	response = _gtts_client.synthesize_speech(input=text_input, voice=_VOICE_PARAMS, audio_config=_AUDIO_CONFIG)
	return response.audio_content
