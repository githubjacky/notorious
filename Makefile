.PHONY: build create-anchorbanks trend-search test 

build:
	poetry install

create-anchorbanks:
	poetry run python scripts/create_anchorbanks.py

# collect the gogle trend
trend-search:
	poetry run python scripts/trend_search.py

test:
	poetry run test


# docker
.PHONY: dbuild dcreate-anchorbanks dtrend-search dtest dclean

dbuild:
	docker compose build

dtest: dbuild
	docker compose run --rm pytest

dcreate-anchorbanks:
	docker compose run --rm create-anchorbanks

dtrend-search:
	docker compose run --rm trend-search

dclean:
	docker rmi 0jacky/notorious_cls:latest && \
	    docker system prune
	brew uninstall docker
