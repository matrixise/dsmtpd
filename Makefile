.PHONY: build

build:
	python3 -m build

check-dist:
	twine check dist/*

upload:
	twine upload dist/*

test:
	pytest