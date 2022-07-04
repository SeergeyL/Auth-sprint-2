make-migrations:
	sudo docker-compose exec web alembic revision --autogenerate

migrate:
	sudo docker-compose exec web alembic upgrade head

superuser:
	sudo docker-compose exec web flask superuser create --email admin@admin.ru --password 123456

test:
	sudo docker-compose -f docker-compose.test.yml up
