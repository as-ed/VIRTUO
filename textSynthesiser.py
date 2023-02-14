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


thing = "\nI would like to add one final note on how topics were chosen for this book.\nMany chapters attempt to " \
        "embody the special sense of beauty that mathemati-\ncians experience when exploring complicated shapes in " \
        "accessible forms that\nanyone can = and touch. From a personal perspective, computer graphics is a\npowerful " \
        "vehicle for artistic expression. However it is notable that some artists\nand scientists have attempted to " \
        "squeeze some of this beauty out of dry formulas\nwithout the aid of a computer. One early example is Dutch " \
        "graphics artist M.C.\nEscher, who represented many complex and repeating geometrical forms by " \
        "hand.\nEscher’s preoccupation with symmetry is well known, and his periodic plane-\nfilling patterns have " \
        "been analyzed by many mathematicians. Escher’s 20th-cen-\ntury counterpart is Russian mathematician A. T. " \
        "Fomenko, whose algebraic\nsurfaces and crystal structures are hand-drawn in mystical and surreal settings\n(" \
        "Figure 1.1). Other fine examples of modern-day artists inspired by mathematics\nare John Robinson, " \
        "from the United Kingdom (Figure 1.4 and Figure 1.5), and\nHelaman Ferguson, a Professor at Brigham Young " \
        "University. Ferguson creates\nmathematically inspired stone sculptures as a way of conveying the beauty of " \
        "the-\norems. His pure white marble sculptures have rather exotic-sounding names like\n“trefoil knots” and " \
        "“horned spheres.” Some resemble the twisted computer\ngraphics forms displayed in the Color Plate section of " \
        "this book. If you are inter-\nested in other examples of physical sculpture inspired by geometrical " \
        "formulas\nyou should consult the sections “Scherk’s Surface” on page 363, “Products,\nClassroom Aids, Art, " \
        "Games, Distributors” on page 384, and “Notes for the\nCurious” on page 371. For instance, Stewart Dickson is " \
        "an artist who represents\nmathematical forms in plastic. The process he uses, called stereolithography," \
        "\nemploys laser-based tools and photosensitive liquid resins which harden as they\nform beautiful, " \
        "computer generated 3-D sculpture (Figure 1.2).\n\nAt this point you are set to proceed further in Computers " \
        "and the Imagina-\ntion. Grab a pencil and paper, and a calculator or personal computer if handy,\nand turn " \
        "the page. If you do not have an interest in computing, there are ample\nthought puzzles and artistic " \
        "graphics to stimulate your imagination. A quote by\nJohn Steinbeck, in collaboration with marine biologist " \
        "Edward Ricketts, sets the\n\ntone for the organization of this book.\n "

print(_post_processing(thing, ls))
