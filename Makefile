project_path = $(shell pwd)
config_path = $(project_path)/.configs
port = 8002
python_version = 3.12.3
service := $(shell basename $(project_path))

REGISTRY_SERVER := $(REGISTRY_SERVER)
REGISTRY_USERNAME := $(REGISTRY_USERNAME)
REGISTRY_PASSWORD := $(REGISTRY_PASSWORD)
commit_sha := $(shell git rev-parse HEAD)
ref_name := $(shell git rev-parse --abbrev-ref HEAD)
IMAGE := $(REGISTRY_SERVER)\/docker\/$(service):$(ref_name)\.
NEW_IMAGE_TAG := $(REGISTRY_SERVER)/docker/$(service):$(ref_name).$(commit_sha)


.PHONY: _test
_test:
	CONFIG_PATH=$(config_path) pytest \
		-c $(project_path)/pyproject.toml \
		$(o) \
		$(project_path)/tests/$(p)

.PHONY: test
test: 
	$(MAKE) _test p="$(p)" o=" \
		-x \
		-s \
		-vvv \
		-p no:warnings \
		--strict-markers \
		--tb=short \
		--cov=src \
		--cov-branch \
		--cov-report=term-missing \
		--cov-fail-under=80 \
		$(o) \
		"

.PHONY: local-test
local-test:
	$(MAKE) _test p="$(p)" o="$(o)"
