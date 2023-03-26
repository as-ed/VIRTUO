import requests
from requests import ConnectionError, Timeout


def test_connection() -> bool:
	try:
		requests.head("http://1.1.1.1", timeout=2)
		return True
	except (ConnectionError, Timeout):
		return False
