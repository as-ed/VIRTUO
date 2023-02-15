

def flip_page() -> bool:
	return manual_flipper()


def manual_flipper() -> bool:
	return input("Flip page and press Enter ('q' to stop) ... ").lower() != "q"
