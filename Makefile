local-install:
	pipenv install
	pipenv run playwright install

dev-run:
	pipenv run python app.py

local-run:
	pipenv run gunicorn app:app --workers 3

docker-build:
	docker build -t bluesky-mirror .

docker-run: docker-build
	docker run -p 8000:8000 bluesky-mirror

docker-dev-run: docker-build
	docker run -p 8000:8000 -v $(PWD):/app bluesky-mirror python app.py

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