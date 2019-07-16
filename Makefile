init:
	pipenv install --dev
	pipenv run pip install -e .

build:
	python setup.py compile_catalog
	python setup.py bdist_wheel

test:
	pipenv run py.test --capture=no --cov-report term-missing --cov-report html --cov=djoser testproject/

migrate:
	pipenv run python testproject/manage.py migrate

runserver:
	pipenv run python testproject/manage.py runserver

