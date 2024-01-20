.PHONY: build test create-anchorbank trend-search test 

build:
	poetry install

test:
	poetry run pytest

create-anchorbank:
	poetry run python scripts/create_anchorbanks.py

# collect the gogle trend
trend-search:
	poetry run python scripts/trend_search.py process=trend_search



# docker
.PHONY: dbuild dtest dcreate-anchorbank dtrend-search dtest dclean

dbuild:
	docker compose build

dtest: dbuild
	docker compose run --rm pytest

dcreate-anchorbank:
	docker compose run --rm create-anchorbanks

dtrend-search:
	docker compose run --rm trend-search

dclean:
	docker rmi 0jacky/notorious_cls:latest
	# docker rmi 0jacky/notorious_cls:latest && \
	#     docker system prune


# command for developer
djupyter:
	docker compose run --rm --service-ports jupyter-lab
