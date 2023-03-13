import json
from typing import Any

import yaml


class _Settings:

	def __init__(self) -> None:
		with open("settings.yml") as s:
			self._settings = yaml.safe_load(s)

	def __repr__(self) -> str:
		return repr(self._settings)

	def __getitem__(self, item) -> Any:
		return self._settings[item]

	def __setitem__(self, key, value) -> None:
		self._settings[key] = value

		with open("settings.yml", "w") as s:
			yaml.safe_dump(self._settings, s)


# config
with open("config.yml") as cfg:
	CFG = yaml.safe_load(cfg)
	CFG["credentials"] = {}

with open("google_cloud_credentials.json", encoding="UTF-8") as credentials:
	CFG["credentials"]["google_cloud"] = json.loads(credentials.read())

settings = _Settings()
