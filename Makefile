.PHONY: create-anchorbanks collect-trend dcreate-anchorbanks dcollect-trend


create-anchorbanks:
	poetry run python create_anchorbanks.py
# collect the gogle trend
collect-trend:
	poetry run python collect_trend.py


# docker
dcreate-anchorbanks:
	docker compose run --rm create-anchorbanks

dcollect-trend:
	docker compose run --rm collect-trend
