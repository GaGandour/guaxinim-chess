.PHONY: lint-python
lint-python:
	black . --line-length 120

freeze:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt