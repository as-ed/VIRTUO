from config import CFG

if CFG["web"]["host"] != "localhost":
	from hw.control import turn_page, load_book, reset


def flip_page() -> None:
	if CFG["web"]["host"] != "localhost":
		turn_page(verbose=False)


def load_position() -> None:
	if CFG["web"]["host"] != "localhost":
		load_book(verbose=False)


def rest_position() -> None:
	if CFG["web"]["host"] != "localhost":
		reset()
