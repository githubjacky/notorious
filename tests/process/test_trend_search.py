import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

from ncls.process import TrendSearch


def test_calibrate_instance():
    engine = TrendSearch(
        "predator",
        "",
        "",
        ["2016-06-01", "2018-12-31"],
    )
    engine.setup()
    engine.calibrate_instance('Alec Klein')  # test wheter the KeyError is raised
