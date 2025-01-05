default: pre-commit fix

# Run Ruff to format files
fmt:
    uvx ruff format .

# Run Ruff to format/fix files
fix: fmt
    uvx ruff check . --fix

# Run pre-commit to check files
pre-commit:
    uvx pre-commit run --all-files
