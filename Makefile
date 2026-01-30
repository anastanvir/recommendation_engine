.PHONY: help build up down logs restart clean test db-shell redis-shell seed

help:
	@echo "Available commands:"
	@echo "  build       - Build Docker images"
	@echo "  up          - Start all services"
	@echo "  up-dev      - Start services in development mode"
	@echo "  down        - Stop all services"
	@echo "  logs        - Show logs from all services"
	@echo "  restart     - Restart all services"
	@echo "  clean       - Remove all containers and volumes"
	@echo "  test        - Run tests"
	@echo "  db-shell    - Open PostgreSQL shell"
	@echo "  redis-shell - Open Redis CLI"
	@echo "  seed        - Seed database with test data"

build:
	docker-compose build --no-cache

up:
	docker-compose up -d

up-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f recommender

logs-db:
	docker-compose logs -f postgres

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec recommender python -m pytest

db-shell:
	docker-compose exec postgres psql -U recommender -d recommender_db

redis-shell:
	docker-compose exec redis redis-cli -a redispass123

migrate:
	docker-compose exec recommender alembic upgrade head

seed:
	@echo "Seeding database with test data..."
	docker-compose exec recommender python scripts/seed_data.py

seed-large:
	@echo "Seeding database with large dataset..."
	docker-compose exec recommender python scripts/seed_data.py --businesses 500 --users 1000 --days 90

health:
	curl http://localhost:8000/health

# Test recommendation endpoints
test-recs:
	@echo "Testing recommendation endpoints..."
	@echo "\n--- User 1 ---"
	curl -s http://localhost:8000/recommend/1 | python -m json.tool
	@echo "\n--- User 2 ---"
	curl -s http://localhost:8000/recommend/2 | python -m json.tool