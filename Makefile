.PHONY: build

build:
	python3 setup.py build sdist bdist_wheel

check-dist:
	twine check dist/*

upload:
	twine upload dist/*

test:
	pytest
