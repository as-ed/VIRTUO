import os
import re
from typing import Tuple, Optional, List, Union

import cv2
from google.oauth2 import service_account
from google.cloud import vision_v1
from nltk.tokenize import sent_tokenize
import numpy as np
import pytesseract
from pytesseract import Output, TesseractError
from spellchecker import SpellChecker

from config import CFG
from ocr.camera import Camera, take_photo
from ocr.page_dewarp import dewarp
from util import test_connection


_test_page = -1
_ocr_client = vision_v1.ImageAnnotatorClient(credentials=service_account.Credentials.from_service_account_info(CFG["credentials"]["google_cloud"]))


def get_text(img: np.ndarray, book_loc: Optional[str], side: Camera, page_nr: int = 0, prev_sentence: str = "", test_mode: bool = False) -> Optional[Tuple[str, str, Optional[int]]]:
	"""
	Converts image to text.
	:param img: image as a numpy array of RGB values
	:param book_loc: location where the digitized book is stored
	:param page_nr: number of the current page
	:param prev_sentence: last sentence of the previous page
	:return: tuple of (page text except last sentence, last (potentially incomplete) sentence, page number), `None` if the end of the book is reached.
	"""
	global _test_page

	if test_mode:
		_test_page = (_test_page + 1) % len(_TEST_TEXT)
		text, last_sentence = _post_processing(_TEST_TEXT[_test_page], prev_sentence)
		return text, last_sentence, _test_page

	_save_img(img, book_loc, f"{page_nr}_original")

	img = _rotate_crop(img, side)
	_save_img(img, book_loc, f"{page_nr}_static_crop")

	# check for QR code at book end
	if side == Camera.right and _is_last_page(img):
		return

	# check if page is empty
	if (dewarped := _pre_processing(img, side, book_loc, page_nr)) is None:
		return "", "", None

	if test_connection() and (response := _google_ocr_request(dewarped)) is not None:
		print("Using Google OCR")
		blocks = _parse_google_ocr_response(response)
		main_text = _get_google_ocr_page_main_body(blocks)
		real_page_nr = _get_google_ocr_page_number(blocks)
	else:
		bboxes = _extract_bboxes(dewarped)
		main_body = _extract_main_body(dewarped, bboxes, book_loc, page_nr)
		_save_img(main_body, book_loc, page_nr)
		main_text = _ocr(main_body)
		real_page_nr = None

	text, last_sentence = _post_processing(main_text, prev_sentence)

	return text, last_sentence, real_page_nr


def upside_down() -> bool:
	osd = None
	try:
		osd = pytesseract.image_to_osd(_rotate_crop(take_photo(Camera.right), Camera.right), output_type=Output.DICT)
	except TesseractError:
		pass

	if osd is None or osd["orientation_conf"] < 5:
		try:
			osd = pytesseract.image_to_osd(_rotate_crop(take_photo(Camera.left), Camera.left), output_type=Output.DICT)
		except TesseractError:
			return False

	return osd["orientation_conf"] >= 5 and osd["orientation"] == 180


def _get_left_page_boundary(img: np.ndarray) -> Optional[int]:
	grayscaled = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

	mask = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 27, 21)

	mask = cv2.dilate(mask, np.ones((7, 1), np.uint8), iterations=1)
	# mask = cv2.dilate(mask, np.ones((1, 3), np.uint8), iterations=5)

	img_area = mask.shape[1] * mask.shape[0]
	contours = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[-2]
	contour_boxes = [ cv2.boundingRect(contour) for contour in contours ]
	# Filter by area
	contour_boxes = list(
		filter(
			lambda cbox: img_area * 0.85 > cbox[2] * cbox[3] > img_area * 0.05, contour_boxes
		)
	)
	# Filter by starting x position
	contour_boxes = list(filter(lambda cbox: cbox[0] > 10, contour_boxes))
	contour_boxes.sort(key=lambda box: box[0])

	if len(contour_boxes) > 0:
		return contour_boxes[0][0]/img.shape[1]


def _google_ocr_request(img: np.ndarray):
	success, encoded_image = cv2.imencode(".png", img)
	content = encoded_image.tobytes()

	if not success:
		return

	image = vision_v1.Image(content=content)

	try:
		response = _ocr_client.document_text_detection(image=image, image_context={"language_hints": ["en"]}, timeout=30)

		if response.error.message:
			return

		return response
	except Exception:
		pass


def _parse_google_ocr_response(response):
	breaks = vision_v1.types.TextAnnotation.DetectedBreak.BreakType
	blocks = []

	for pages in response.full_text_annotation.pages:
		for block in pages.blocks:
			block_text = ""
			for paragraph in block.paragraphs:
				for word in paragraph.words:
					for symbol in word.symbols:
						word_text = symbol.text
						if symbol.property.detected_break.type_:
							break_text = ""
							if (
								symbol.property.detected_break.type_ == breaks.SPACE
								or symbol.property.detected_break.type_ == breaks.LINE_BREAK
								or symbol.property.detected_break.type_
								== breaks.EOL_SURE_SPACE
								or symbol.property.detected_break.type_
								== breaks.EOL_SURE_SPACE
							):
								break_text = " "
							elif symbol.property.detected_break.type_ == breaks.HYPHEN:
								break_text = "-"
							else:
								break_text = ""
							if symbol.property.detected_break.is_prefix:
								word_text = break_text + word_text
							else:
								word_text = word_text + break_text
						block_text += word_text
			blocks.append(block_text)

	return blocks


def _get_google_ocr_page_number(blocks: List[str]) -> Optional[int]:
	for text in blocks:
		if re.match(r"^\d+$", text.strip()):
			return int(text)


def _get_google_ocr_page_title(blocks: List[str]) -> Optional[str]:
	for text in blocks:
		if len(text) < 25:
			return text


def _get_google_ocr_page_main_body(blocks: List[str]) -> str:
	output = ""

	for text in blocks:
		if len(text) >= 25:
			output += text

	return output


def _is_last_page(img: np.ndarray) -> bool:
	qr_detector = cv2.QRCodeDetector()
	data, _, _ = qr_detector.detectAndDecode(img)

	return data == "http://virtuo.local"


def _extract_main_body(dewarped: np.ndarray, bboxes: List[Tuple[int]], book_loc: str, page_nr: int) -> np.ndarray:
	mask = np.zeros(dewarped.shape, dtype=np.uint8)

	if len(bboxes) == 0:
		return dewarped

	for x, y, w, h in bboxes:
		if w * h > 25000:
			cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)

	min_x1 = min(bboxes, key=lambda bbox: bbox[0])[0]
	max_x2_bbox = max(bboxes, key=lambda bbox: bbox[0] + bbox[2])
	max_x2 = max_x2_bbox[0] + max_x2_bbox[2]
	min_y1 = min(bboxes, key=lambda bbox: bbox[1])[1]
	max_y2_bbox = max(bboxes, key=lambda bbox: bbox[1] + bbox[3])
	max_y2 = max_y2_bbox[1] + max_y2_bbox[3]

	_save_img(mask, book_loc, f"{page_nr}_mask")

	return (mask & dewarped)[max(0, min_y1 - 20) : max_y2 + 20, max(0, min_x1 - 20) : max_x2 + 20]


def _rotate_crop(img: np.ndarray, side: Camera):
	if side == Camera.left:
		rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
	else:
		rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

	return rotated[
		CFG["camera"]["crop"][side.name]["top"]:-CFG["camera"]["crop"][side.name]["bottom"],
		CFG["camera"]["crop"][side.name]["left"]:-CFG["camera"]["crop"][side.name]["right"]]


def _pre_processing(img: np.ndarray, side: Camera, book_loc: str, page_nr: int) -> Optional[np.ndarray]:
	dewarped = dewarp(img, side, page_nr)

	if dewarped is not None:
		_save_img(dewarped, book_loc, f"{page_nr}_dewarped")

	return dewarped


def _extract_bboxes(img: np.ndarray) -> List[Tuple[int]]:
	boxes = pytesseract.image_to_boxes(img, output_type=Output.DICT)

	mask = np.zeros(img.shape, dtype=np.uint8)

	for i in range(len(boxes["left"])):
		left = boxes["left"][i]
		bottom = boxes["bottom"][i]
		right = boxes["right"][i]
		top = boxes["top"][i]

		area = abs((right - left) * (top - bottom))

		if area < 2000:
			cv2.rectangle(mask, (left, bottom), (right, top), (255, 0, 255), 5)

	mask = cv2.flip(mask, flipCode=0)

	dilated = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=17)

	contours, _ = cv2.findContours(
		dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
	)

	return list(map(cv2.boundingRect, contours))


def _save_img(img: np.ndarray, book_loc: str, page_nr: Union[int, str]) -> None:
	path = os.path.join(book_loc, "pages")
	os.makedirs(path, exist_ok=True)
	cv2.imwrite(os.path.join(path, f"{page_nr}.png"), img)


def _ocr(img: np.ndarray) -> str:
	return pytesseract.image_to_string(img)


def _post_processing(text: str, prev_sentence: str) -> Tuple[str, str]:
	# remove white space at start and end
	new_text = re.sub(r"^\s*", "", text)
	new_text = re.sub(r"\s*$", "", new_text)

	# remove hyphens that split words
	new_text = new_text.replace("-\n", "")

	# remove single line breaks
	new_text = re.sub("(^|[^\n])\n($|[^\n])", r"\1 \2", new_text)

	# convert multi line break to single line break
	new_text = re.sub("\n+", "\n", new_text)

	# convert "|" (pipe) to "I"
	new_text = new_text.replace("|", "I")

	# limit characters
	new_text = re.sub("[\u201d\u201c]", '"', new_text)
	new_text = re.sub("[\u2018\u2019]", "'", new_text)
	new_text = re.sub("[\u058a\u05be\u1806\u2010\u2011\u2012\u2013\u2014]", "-", new_text)
	new_text = re.sub("[^\\s\\w.,;'\"!?:&()-]", " ", new_text)

	# convert multi white space to single space
	new_text = re.sub("[ \t]+", " ", new_text)

	# append previous sentence
	if len(prev_sentence) > 0 and prev_sentence[-1] == "-":
		new_text = prev_sentence[:-1] + new_text
	else:
		new_text = prev_sentence + " " + new_text

	# extract last sentence
	sentences = sent_tokenize(new_text)
	new_text = " ".join(sentences[:-1])
	last_sentence = sentences[-1]

	# autocorrect
	new_text = _auto_correct(new_text)

	return new_text, last_sentence


def _auto_correct(text):
	spell_checker = SpellChecker()
	text_array = text.split(" ")
	result = ""

	for word in text_array:
		if word == "":
			continue
		elif word[0].isupper() or (not word[len(word) - 1].isalpha()):
			result = result + word + " "
			continue
		elif len(spell_checker.unknown([word])) == 1:
			w = spell_checker.correction(word)
			if w is not None:
				result = result + w + " "
			else:
				result = result + word + " "
		else:
			result = result + word + " "

	return result


_TEST_TEXT = [
	"""Loomings.

Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation. Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet; and especially whenever my hypos get such an upper hand of me, that it requires a strong moral principle to prevent me from deliberately stepping into the street, and methodically knocking people's hats off—then, I account it high time to get to sea as soon as I can. This is my substitute for pistol and ball. With a philosophical flourish Cato throws himself upon his sword; I quietly take to the ship. There is nothing surprising in this. If they but knew it, almost all men in their degree, some time or other, cherish very nearly the same feelings towards the ocean with me.

There now is your insular city of the Manhattoes, belted round by wharves as Indian isles by coral reefs—commerce surrounds it with her surf. Right and left, the streets take you waterward. Its extreme downtown is the battery, where that noble mole is washed by waves, and cooled by breezes, which a few hours previous were out of sight of land. Look at the crowds of water-gazers there.""",
	""" Circumambulate the city of a dreamy Sabbath afternoon. Go from Corlears Hook to Coenties Slip, and from thence, by Whitehall, northward. What do you see?—Posted like silent sentinels all around the town, stand thousands upon thousands of mortal men fixed in ocean reveries. Some leaning against the spiles; some seated upon the pier-heads; some looking over the bulwarks of ships from China; some high aloft in the rigging, as if striving to get a still better seaward peep. But these are all landsmen; of week days pent up in lath and plaster—tied to counters, nailed to benches, clinched to desks. How then is this? Are the green fields gone? What do they here?

But look! here come more crowds, pacing straight for the water, and seemingly bound for a dive. Strange! Nothing will content them but the extremest limit of the land; loitering under the shady lee of yonder warehouses will not suffice. No. They must get just as nigh the water as they possibly can without falling in. And there they stand—miles of them—leagues. Inlanders all, they come from lanes and alleys, streets and avenues—north, east, south, and west. Yet here they all unite. Tell me, does the magnetic virtue of the needles of the compasses of all those ships attract them thither?""",
	""" Once more. Say you are in the country; in some high land of lakes. Take almost any path you please, and ten to one it carries you down in a dale, and leaves you there by a pool in the stream. There is magic in it. Let the most absent-minded of men be plunged in his deepest reveries—stand that man on his legs, set his feet a-going, and he will infallibly lead you to water, if water there be in all that region. Should you ever be athirst in the great American desert, try this experiment, if your caravan happen to be supplied with a metaphysical professor. Yes, as every one knows, meditation and water are wedded for ever.

But here is an artist. He desires to paint you the dreamiest, shadiest, quietest, most enchanting bit of romantic landscape in all the valley of the Saco. What is the chief element he employs? There stand his trees, each with a hollow trunk, as if a hermit and a crucifix were within; and here sleeps his meadow, and there sleep his cattle; and up from yonder cottage goes a sleepy smoke. Deep into distant woodlands winds a mazy way, reaching to overlapping spurs of mountains bathed in their hill-side blue. But though the picture lies thus tranced, and though this pine-tree shakes down its sighs like leaves upon this shepherd's head, yet all were vain, unless the shepherd's eye were fixed upon the magic stream before him. Go visit the Prairies in June, when for scores on scores of miles you wade knee-deep among Tiger-lilies—what is the one charm wanting?—Water—there is not a drop of water there! Were Niagara but a cataract of sand, would you travel your thousand miles to see it?""",
	"""Why did the poor poet of Tennessee, upon suddenly receiving two handfuls of silver, deliberate whether to buy him a coat, which he sadly needed, or invest his money in a pedestrian trip to Rockaway Beach? Why is almost every robust healthy boy with a robust healthy soul in him, at some time or other crazy to go to sea? Why upon your first voyage as a passenger, did you yourself feel such a mystical vibration, when first told that you and your ship were now out of sight of land? Why did the old Persians hold the sea holy? Why did the Greeks give it a separate deity, and own brother of Jove? Surely all this is not without meaning. And still deeper the meaning of that story of Narcissus, who because he could not grasp the tormenting, mild image he saw in the fountain, plunged into it and was drowned. But that same image, we ourselves see in all rivers and oceans. It is the image of the ungraspable phantom of life; and this is the key to it all.

Now, when I say that I am in the habit of going to sea whenever I begin to grow hazy about the eyes, and begin to be over conscious of my lungs, I do not mean to have it inferred that I ever go to sea as a passenger. For to go as a passenger you must needs have a purse, and a purse is but a rag unless you have something in it. Besides, passengers get sea-sick—grow quarrelsome—don't sleep of nights—do not enjoy themselves much, as a general thing;—no, I never go as a passenger; nor, though I am something of a salt, do I ever go to sea as a Commodore, or a Captain, or a Cook. I abandon the glory and distinction of such offices to those who like them. For my part, I abominate all honorable respectable toils, trials, and tribulations of every kind whatsoever. It is quite as much as I can do to take care of myself, without taking care of ships, barques, brigs, schooners, and what not.""",
	"""And as for going as cook,—though I confess there is considerable glory in that, a cook being a sort of officer on ship-board—yet, somehow, I never fancied broiling fowls;—though once broiled, judiciously buttered, and judgmatically salted and peppered, there is no one who will speak more respectfully, not to say reverentially, of a broiled fowl than I will. It is out of the idolatrous dotings of the old Egyptians upon broiled ibis and roasted river horse, that you see the mummies of those creatures in their huge bake-houses the pyramids.

No, when I go to sea, I go as a simple sailor, right before the mast, plumb down into the forecastle, aloft there to the royal mast-head. True, they rather order me about some, and make me jump from spar to spar, like a grasshopper in a May meadow. And at first, this sort of thing is unpleasant enough. It touches one's sense of honor, particularly if you come of an old established family in the land, the Van Rensselaers, or Randolphs, or Hardicanutes. And more than all, if just previous to putting your hand into the tar-pot, you have been lording it as a country schoolmaster, making the tallest boys stand in awe of you. The transition is a keen one, I assure you, from a schoolmaster to a sailor, and requires a strong decoction of Seneca and the Stoics to enable you to grin and bear it. But even this wears off in time.""",
	""" What of it, if some old hunks of a sea-captain orders me to get a broom and sweep down the decks? What does that indignity amount to, weighed, I mean, in the scales of the New Testament? Do you think the archangel Gabriel thinks anything the less of me, because I promptly and respectfully obey that old hunks in that particular instance? Who ain't a slave? Tell me that. Well, then, however the old sea-captains may order me about—however they may thump and punch me about, I have the satisfaction of knowing that it is all right; that everybody else is one way or other served in much the same way—either in a physical or metaphysical point of view, that is; and so the universal thump is passed round, and all hands should rub each other's shoulder-blades, and be content.

Again, I always go to sea as a sailor, because they make a point of paying me for my trouble, whereas they never pay passengers a single penny that I ever heard of. On the contrary, passengers themselves must pay. And there is all the difference in the world between paying and being paid. The act of paying is perhaps the most uncomfortable infliction that the two orchard thieves entailed upon us. But being paid,—what will compare with it? The urbane activity with which a man receives money is really marvellous, considering that we so earnestly believe money to be the root of all earthly ills, and that on no account can a monied man enter heaven. Ah! how cheerfully we consign ourselves to perdition!""",
	"""Finally, I always go to sea as a sailor, because of the wholesome exercise and pure air of the fore-castle deck. For as in this world, head winds are far more prevalent than winds from astern (that is, if you never violate the Pythagorean maxim), so for the most part the Commodore on the quarter-deck gets his atmosphere at second hand from the sailors on the forecastle. He thinks he breathes it first; but not so. In much the same way do the commonalty lead their leaders in many other things, at the same time that the leaders little suspect it. But wherefore it was that after having repeatedly smelt the sea as a merchant sailor, I should now take it into my head to go on a whaling voyage; this the invisible police officer of the Fates, who has the constant surveillance of me, and secretly dogs me, and influences me in some unaccountable way—he can better answer than any one else. And, doubtless, my going on this whaling voyage, formed part of the grand programme of Providence that was drawn up a long time ago. It came in as a sort of brief interlude and solo between more extensive performances. I take it that this part of the bill must have run something like this:

"Grand Contested Election for the Presidency of the United States. "WHALING VOYAGE BY ONE ISHMAEL. "BLOODY BATTLE IN AFFGHANISTAN.""",
	""" Though I cannot tell why it was exactly that those stage managers, the Fates, put me down for this shabby part of a whaling voyage, when others were set down for magnificent parts in high tragedies, and short and easy parts in genteel comedies, and jolly parts in farces—though I cannot tell why this was exactly; yet, now that I recall all the circumstances, I think I can see a little into the springs and motives which being cunningly presented to me under various disguises, induced me to set about performing the part I did, besides cajoling me into the delusion that it was a choice resulting from my own unbiased freewill and discriminating judgment.

Chief among these motives was the overwhelming idea of the great whale himself. Such a portentous and mysterious monster roused all my curiosity. Then the wild and distant seas where he rolled his island bulk; the undeliverable, nameless perils of the whale; these, with all the attending marvels of a thousand Patagonian sights and sounds, helped to sway me to my wish. With other men, perhaps, such things would not have been inducements; but as for me, I am tormented with an everlasting itch for things remote. I love to sail forbidden seas, and land on barbarous coasts. Not ignoring what is good, I am quick to perceive a horror, and could still be social with it—would they let me—since it is but well to be on friendly terms with all the inmates of the place one lodges in.

By reason of these things, then, the whaling voyage was welcome; the great flood-gates of the wonder-world swung open, and in the wild conceits that swayed me to my purpose, two and two there floated into my inmost soul, endless processions of the whale, and, mid most of them all, one grand hooded phantom, like a snow hill in the air."""]
