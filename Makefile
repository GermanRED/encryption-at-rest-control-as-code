.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: types
types:
	uvx mypy_boto3_builder ./vendored --download-static-stubs --product types-boto3-custom --output-type wheel --services rds s3
	uv add --dev ./vendored/types_boto3_custom-*.whl

.PHONY: test
test: ## run the test suite
	uv run pytest -v

.PHONY: export
export: ## prints to screen the assets in csv format
	uv run export
