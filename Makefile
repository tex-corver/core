project_path = $(shell pwd)
config_path = $(project_path)/.configs
port = 8002
service := $(shell basename $(project_path))

REGISTRY_SERVER := $(REGISTRY_SERVER)
REGISTRY_USERNAME := $(REGISTRY_USERNAME)
REGISTRY_PASSWORD := $(REGISTRY_PASSWORD)
commit_sha := $(shell git rev-parse HEAD)
ref_name := $(shell git rev-parse --abbrev-ref HEAD)
IMAGE := $(REGISTRY_SERVER)\/docker\/$(service):$(ref_name)\.
NEW_IMAGE_TAG := $(REGISTRY_SERVER)/docker/$(service):$(ref_name).$(commit_sha)


.PHONY: test
test: 
	CONFIG_PATH=$(config_path) pytest -c $(project_path)/pyproject.toml $(o) $(project_path)/tests/$(p)