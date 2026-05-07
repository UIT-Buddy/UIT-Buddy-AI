.PHONY: up \
        down \
        logs \
        install \
        run

up:  ## Start Neo4j + supporting containers
	podman compose -f docker-compose-ai.yml up -d

down:  ## Stop and remove all containers and volumes
	podman compose -f docker-compose-ai.yml down -v

logs:  ## Tail logs from all containers
	podman compose -f docker-compose-ai.yml logs -f

install:  ## Install Python dependencies
	pip install -r requirements.txt
run:  ## Start FastAPI server (production)
	python server.py
