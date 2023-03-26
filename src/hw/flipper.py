from config import CFG

if CFG["web"]["host"] != "localhost":
	from hw.control import turn_page


def flip_page() -> None:
	if CFG["web"]["host"] != "localhost":
		turn_page(verbose=False)
