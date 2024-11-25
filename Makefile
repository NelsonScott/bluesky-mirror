run:
	pipenv run gunicorn app:app --workers 3

dev-run:
	pipenv run python app.py

install:
	pipenv run playwright install-deps
	pipenv install
	pipenv run playwright install

test:
	pipenv run pytest