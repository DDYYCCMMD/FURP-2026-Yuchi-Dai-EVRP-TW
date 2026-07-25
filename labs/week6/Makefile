PYTHON ?= python
ROOT := ../..

.PHONY: check-config run-evrptw run-vrptw test

check-config:
	cd $(ROOT) && $(PYTHON) -m labs.week6.src.run_week6_alns --check-config

run-evrptw:
	cd $(ROOT) && $(PYTHON) -m labs.week6.src.run_week6_alns --mode evrptw

run-vrptw:
	cd $(ROOT) && $(PYTHON) -m labs.week6.src.run_week6_alns --mode vrptw

test:
	cd $(ROOT) && $(PYTHON) -m pytest -q labs/week6/tests

