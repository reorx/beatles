PY_CLI_VERSION ?= 0.5.0
convert:
	PY_CLI_VERSION=$(PY_CLI_VERSION) python3 converter.py

test-cli:
	cd beatles_song && pipenv run tox

publish-cli:
	cd beatles_song && pipenv run python setup.py sdist bdist_wheel upload
