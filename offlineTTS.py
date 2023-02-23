from subprocess import call

import wave
import os

import logging
import subprocess
import tempfile

text1 = "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, " \
		"and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part " \
		"of the world. It is a way I have of driving off the spleen and regulating the circulation. Whenever I find " \
		"myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find " \
		"myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet; and " \
		"especially whenever my hypos get such an upper hand of me, that it requires a strong moral principle to " \
		"prevent me from deliberately stepping into the street, and methodically knocking people’s hats off—then, " \
		"I account it high time to get to sea as soon as I can. This is my substitute for pistol and ball. With a " \
		"philosophical flourish Cato throws himself upon his sword; I quietly take to the ship. There is nothing " \
		"surprising in this. If they but knew it, almost all men in their degree, some time or other, cherish very " \
		"nearly the same feelings towards the ocean with me. "


def offlineTTS(text: str):
	f = open("input.txt", "w")
	f.write(text)
	f.close()

	call(["pico2wave -l en-GB -w output.wav \"" + text + "\""], shell=True)

	while not os.path.exists("output.wav"):
		time.sleep(5)

	frames = wave.open("output.wav").readframes(100000000000000000)
	os.remove("output.wav")
	
	return frames


def synth_wav(txt):
	wav = None

	with tempfile.NamedTemporaryFile(suffix='.wav') as f:
		txte = txt.encode('utf8')

		args = ['-w', f.name, txte]

		self._picotts_exe(args, sync=True)

		f.seek(0)
		wav = f.read()

		logging.debug('read %s, got %d bytes.' % (f.name, len(wav)))

	return wav


offlineTTS(text1)
