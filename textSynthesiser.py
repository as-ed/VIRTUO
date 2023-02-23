from TTS.api import TTS  # https://github.com/coqui-ai/TTS
from textblob import TextBlob
# instructions from https://pyimagesearch.com/2021/11/29/using-spellchecking-to-improve-tesseract-ocr-accuracy/
from spellchecker import SpellChecker
# nltk split text into sentences
from typing import Tuple


def readText(text, voice):
    voices = [
        'tts_models/en/ljspeech/tacotron2-DDC',
        'tts_models/en/ljspeech/tacotron2-DDC_ph',
        'tts_models/en/ljspeech/fast_pitch'
    ]

    if voice >= len(voices):
        tts = TTS(voices[1])
        print("Error: Invalid Voice Selected")
    else:
        tts = TTS(voices[voice])
        # os.remove("speech/output" + str(voice) + ".wav")
        # tts.tts_to_file(text=text,file_path="speech/output" + str(voice) + ".wav")

    return tts.tts(text)


def autoCorrect(text, language):  # language is just English for now, also removes all punctuation
    spell = SpellChecker()
    textArray = text.split(" ")
    result = ""

    for word in textArray:
        if word == "":
            continue
        elif word[0].isupper() or (not word[len(word) - 1].isalpha()):
            result = result + word + " "
            continue
        elif len(spell.unknown([word])) == 1:
            w = spell.correction(word)
            if w is not None:
                result = result + w + " "
            else:
                result = result + word + " "
        else:
            result = result + word + " "

    return result


def _post_processing(text: str, prev_sentence: str) -> Tuple[str, str]:
    newText = ""
    lastSentence = ""

    # extract last sentence
    for i in range(len(text) - 1, 0, -1):
        if text[i] == ".":
            lastSentence = text[(i + 1):]
            text = text[:(i + 1)]
            break

    text = " \n" + prev_sentence + " " + text

    # remove line breaks
    # remove hyphens that split words
    # replace '|' (pipe) with 'I'

    for i in range(1, len(text)):
        if text[i] == "\n":
            if text[i - 1] == "-":
                newText = newText[:-1]
            else:
                newText = newText + " "
        elif text[i] == "|":
            newText = newText + "I"
        else:
            newText = newText + text[i]

    # autocorrect

    newText = autoCorrect(newText, 0)

    return newText, lastSentence