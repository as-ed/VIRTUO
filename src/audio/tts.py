from TTS.api import TTS

from config import CFG


def tts(text: str) -> bytes:
	return TTS(CFG["audio"]["voices"][CFG["audio"]["default_voice"]]["path"]).tts(text)
