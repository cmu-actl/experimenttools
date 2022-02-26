docs: docs/index.html

docs/index.html : experimenttools/*
	pdoc --html -o docs experimenttools
	mv docs/experimenttools/* docs/
	rmdir docs/experimenttools

test:
	python -m unittest
	python -m doctest experimenttools/*.py
