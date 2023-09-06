install:
	poetry install

lint:
	poetry run flake8 radio_cross

selfcheck:
	poetry check

check: selfcheck lint

build: check
	poetry build

isort:
	poetry run isort radio_cross

.PHONY: install lint selfcheck check build