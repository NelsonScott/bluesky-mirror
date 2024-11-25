run:
	pipenv run gunicorn app:app --workers 3

dev-run:
	pipenv run python app.py

install-render:
	apt-get update && apt-get install -y \
		libgstreamer-gl1.0-0 \
		libgstreamer-plugins-bad1.0-0 \
		libenchant-2-2 \
		libsecret-1-0 \
		libmanette-0.2-0 \
		libgles2-mesa
	pipenv install
	pipenv run playwright install

test:
	pipenv run pytest