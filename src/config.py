import json
import yaml


# config
with open("config.yml") as cfg:
	CFG = yaml.safe_load(cfg)
	CFG["credentials"] = {}

with open("google_cloud_credentials.json", encoding="UTF-8") as credentials:
	CFG["credentials"]["google_cloud"] = json.loads(credentials.read())

# settings
try:
	with open("settings.yml") as s:
		settings = yaml.safe_load(s)
except FileNotFoundError:
	settings = {}
