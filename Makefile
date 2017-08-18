init:
	pipenv install --dev
	pipenv run pip install -e .

test:
	pipenv run py.test --capture=no --cov-report term-missing --cov-report html --cov=djoser testproject/
	pipenv run flake8 .

migrate:
	pipenv run python testproject/manage.py migrate

runserver:
	pipenv run python testproject/manage.py runserver

