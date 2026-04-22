.PHONY: install install-dev run test db-up db-down db-wait db-migrate db-reset

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload

test:
	pytest -q

db-up:
	docker compose -f docker-compose.mysql.yml up -d

db-down:
	docker compose -f docker-compose.mysql.yml down

db-wait:
	@echo "Esperando MySQL..."
	@for i in $$(seq 1 60); do \
		if docker compose -f docker-compose.mysql.yml exec -T mysql mysqladmin ping -h 127.0.0.1 -uroot -proot123 --silent; then \
			echo "MySQL disponible"; \
			exit 0; \
		fi; \
		sleep 2; \
	done; \
	echo "MySQL no respondió a tiempo"; \
	exit 1

db-migrate:
	python scripts/migrate.py

db-reset: db-down
	docker volume rm cultivos_cultivos_mysql_data >/dev/null 2>&1 || true
	$(MAKE) db-up
	$(MAKE) db-wait
	$(MAKE) db-migrate
