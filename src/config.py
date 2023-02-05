import yaml


# config
with open("config.yml") as cfg:
	CFG = yaml.safe_load(cfg)
