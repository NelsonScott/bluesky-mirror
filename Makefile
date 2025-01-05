local-install:
	pipenv install
	pipenv run playwright install

local-run:
	pipenv run python run.py

docker-build:
	docker build -t bluesky-mirror .

docker-run: docker-build
	docker run -d -p 8000:8000 --name bluesky-mirror bluesky-mirror

docker-dev-run: docker-build
	docker run -p 8000:8000 -v $(PWD):/app --name bluesky-mirror bluesky-mirror python run.py

# Flexible targets that use local or Docker based on an environment variable
install:
	@if [ "$$USE_DOCKER" = "true" ]; then \
		$(MAKE) docker-build; \
	else \
		$(MAKE) local-install; \
	fi

run:
	@if [ "$$USE_DOCKER" = "true" ]; then \
		$(MAKE) docker-run; \
	else \
		$(MAKE) local-run; \
	fi