.PHONY: build test create-anchorbank trend-search return_ri_rj ri-reg

build:
	poetry install

test:
	poetry run pytest

create-anchorbank:
	poetry run python scripts/create_anchorbanks.py process=tren_search

# collect the gogle trend
trend-search:
	poetry run python scripts/trend_search.py process=trend_search

return-ri-rj:
	poetry run python scripts/return_ri_rj.py process=return_ri_rj

ri-reg:
	poetry run python scripts/create_ri_for_regression.py process=create_ri_for_regression
	



# docker
.PHONY: dbuild dtest dcreate-anchorbank dtrend-search dreturn-ri-rj dri-reg dclean

dbuild:
	docker compose build

dtest: dbuild
	docker compose run --rm pytest

dcreate-anchorbank:
	docker compose run --rm create-anchorbanks

dtrend-search:
	docker compose run --rm trend-search

dreturn-ri-rj:
	docker compose run --rm return-ri-rj

dri-reg:
	docker compose run --rm create-ri-for-regression


dclean:
	docker rmi 0jacky/notorious_cls:latest
	# docker rmi 0jacky/notorious_cls:latest && \
	#     docker system prune


.PHONY: djupyter

# command for developer
djupyter:
	docker compose run --rm --service-ports jupyter-lab
