all: pre-commit

pre-commit:
	pre-commit run --all-files

.PHONY: all pre-commit
