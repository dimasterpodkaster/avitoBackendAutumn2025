.PHONY: build up down logs test sh

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

logs:
	docker-compose logs -f web

test:
	docker-compose run --rm --entrypoint "" web python manage.py test

sh:
	docker-compose run --rm --entrypoint "" web sh
