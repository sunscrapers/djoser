init:
	pipenv install --dev
	pipenv run pip install -e .

test:
	pipenv run coverage run --source=djoser testproject/manage.py test testapp

migrate:
	pipenv run python testproject/manage.py migrate

runserver:
	pipenv run python testproject/manage.py runserver

