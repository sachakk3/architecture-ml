.PHONY: bot build

bot:
	docker compose run --rm bot

build:
	docker compose build bot