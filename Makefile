all:

test:
	poetry run pytest

coverage:
	poetry run coverage html --omit="*/test/*"
