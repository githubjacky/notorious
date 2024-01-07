.PHONY: create-anchorbanks trend-search dcreate-anchorbanks dtrend-search


create-anchorbanks:
	poetry run python scripts/create_anchorbanks.py
# collect the gogle trend
trend-search:
	poetry run python scripts/trend_search.py


# docker
dcreate-anchorbanks:
	docker compose run --rm create-anchorbanks

dtrend-search:
	docker compose run --rm trend-search
