from random import random


def flip_page(test_mode: bool = False) -> bool:
	if test_mode:
		return random() < 0.2

	return True
