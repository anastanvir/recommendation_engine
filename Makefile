.PHONY: help build up down logs restart clean test db-shell redis-shell hti-data hti-seed

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
	@echo ""
	@echo "HTI Data Generation:"
	@echo "  hti-data    - Generate 6 months of HTI super app test data (1200 users, 600 businesses)"
	@echo "  hti-seed    - Quick seed with sample HTI data for testing"

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
	docker-compose exec postgres psql -U recommender -d recommender_db -f /docker-entrypoint-initdb.d/init.sql

health:
	curl http://localhost:8000/health

# HTI Super App Data Generation
hti-data:
	@echo "Generating 6 months of HTI super app test data..."
	@echo "This will create 1200 users, 600 businesses, and ~500K+ interactions"
	docker-compose exec recommender python scripts/hti_social_marketplace_generator.py

hti-seed:
	@echo "Loading HTI sample seed data..."
	docker-compose exec postgres psql -U recommender -d recommender_db -f /app/scripts/hti_seed_data.sql

# Test recommendation endpoints
test-recs:
	@echo "Testing recommendation endpoints..."
	@echo "\n--- User 1 (Social Butterfly) ---"
	curl -s http://localhost:8000/recommend/1 | python -m json.tool
	@echo "\n--- User 4 (Shopper) ---"
	curl -s http://localhost:8000/recommend/4 | python -m json.tool
	@echo "\n--- User 7 (Professional) ---"
	curl -s http://localhost:8000/recommend/7 | python -m json.tool