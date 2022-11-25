build: export DOCKER_BUILDKIT=1
build:
	docker build -t flaska .
run:
	docker compose up -d
