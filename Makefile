APP = app-name
APP_DEV = $(APP)-test

IMAGE = $(APP)
IMAGE_TEST = $(APP_DEV)

CONTAINER = $(APP)
CONTAINER_TEST = $(APP_DEV)

RUN = docker run -d -p 8080:8080 --name $(CONTAINER) $(IMAGE)
RUN_DEV = docker run --rm -t $(IMAGE_TEST)

PIP_COMPILE = pip-compile
PIP_SYNC = pip-sync

PYLINT = pylint
PYLINTFLAGS = -rn
PYTHONFILES := $(shell find . -not -path "./.venv/*" -type f -name '*.py')

PYTEST = pytest

FLAKE8 = flake8
AUTOPEP8 = autopep8

ISORT = isort
ISORTFLAGS = -fss

init:
	( \
		virtualenv -p python3 .venv; \
		source .venv/bin/activate; \
		pip install -U pip; \
		pip install pip-tools; \
		pip-sync requirements-dev.txt requirements.txt; \
		rm -rf .git; \
		git init .; \
		git add .; \
		git commit -m 'Initial commit'; \
	)

compile:
	$(PIP_COMPILE) requirements.in
	$(PIP_COMPILE) requirements-dev.in

sync: compile
	$(PIP_SYNC) requirements.txt

sync-dev: compile
	$(PIP_SYNC) requirements.txt requirements-dev.txt

flake8:
	$(FLAKE8) $(PYTHONFILES)

autopep8:
	$(AUTOPEP8) -a -i $(PYTHONFILES)

pylint:
	$(PYLINT) $(PYLINTFLAGS) $(PYTHONFILES)

pytest:
	$(PYTEST) .

cov:
	$(PYTEST) --cov-report term-missing --cov=.

check: pylint cov flake8

isort:
	$(ISORT) $(ISORTFLAGS) $(PYTHONFILES)

build:
	docker build -t $(IMAGE) .

build-dev:
	docker build -t $(IMAGE_TEST) -f Dockerfile.test .

run: build
	env DEBUG=1 $(RUN)

stop:
	docker stop $(CONTAINER_TEST)
	docker rm $(CONTAINER_TEST)

run-dev: build-dev
	$(RUN_DEV)

stop-dev:
	docker rm -f $(CONTAINER_TEST)
