.PHONY: first_build build clean pytest doc jupyter mlflow trend-search adjust-ait


first_build:
	rm -f log/.gitkeep notebooks/.gitkeep
	git init
	mkdir -p data/raw data/processed mlruns
	dvc commit
	docker compose build
	git add .
	git commit -m "first commit"
	git branch -M main
	git remote add origin https://github.com/githubjacky/notorious.git
	git push -u origin main


build:
	docker compose build


down:
	docker compose down


clean:
	docker rmi --force 0jacky/notorious:latest


pytest:
	docker compose run --rm pytest


doc:
	docker compose run --rm doc


jupyter:
	docker compose run --rm --service-ports jupyter-lab


mlflow:
	docker compose run --rm --service-ports mlflow-ui


trend-search:
	docker compose run --rm trend-search


adjust-ait:
	docker compose run --rm trend-search
