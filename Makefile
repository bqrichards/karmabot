all:

test:
	poetry run coverage run -m pytest

coverage:
	poetry run coverage html --omit="*/test/*"

clean:
	rm -rf htmlcov .coverage \
		__pycache__ **/*/__pycache__ \
		.pytest_cache **/*/.pytest_cache
