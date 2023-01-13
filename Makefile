# -*- mode: makefile -*-

COMPOSE = docker-compose -p demo_stream_urls_server -f docker/docker-compose.yml
BUILD = COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 $(COMPOSE) build
RUN = $(COMPOSE) run --rm

.PHONY: down
down:
	$(COMPOSE) down --volumes --rmi=local

.PHONY: up-redis
up-redis:
	$(COMPOSE) up redis

.PHONY: build-app
build-app:
	$(BUILD) app

.PHONY: up
up: build-app
	$(COMPOSE) up api refresh-token

.PHONY: sh
sh: build-app
	$(RUN) app sh
