.PHONY: collect_trend dcollect_trend


# collect the gogle trend
collect-trend:
	poetry run python collect_trend.py

# docker
dcollect-trend:
	docker compose run --rm collect-trend
