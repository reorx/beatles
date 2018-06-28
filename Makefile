convert:
	python3 converter.py

test-cli:
	cd beatles_song && pipenv run tox
