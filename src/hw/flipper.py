from config import CFG

if CFG["web"]["host"] != "localhost":
	from hw.control import turn_page, load_book, reset, stop, led_strip_on, led_strip_off, flatten


def flip_page() -> None:
	if CFG["web"]["host"] != "localhost":
		turn_page(verbose=False)


def load_position(bc_up=True) -> None:
	if CFG["web"]["host"] != "localhost":
		load_book(verbose=False, bc_up=bc_up)


def rest_position() -> None:
	if CFG["web"]["host"] != "localhost":
		reset()


def stop_motors() -> None:
	if CFG["web"]["host"] != "localhost":
		stop()


def turn_on_lights() -> None:
	if CFG["web"]["host"] != "localhost":
		led_strip_on()


def turn_off_lights() -> None:
	if CFG["web"]["host"] != "localhost":
		led_strip_off()


def flatten_page() -> None:
	if CFG["web"]["host"] != "localhost":
		flatten()
