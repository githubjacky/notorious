import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

from src.data.trend_search import TrendSearch
from src.data.utils import get_target_list


def test_calibrate_instance():
    engine = TrendSearch(
        get_target_list(),
        "",
        "",
        ["2016-06-01", "2018-12-31"],
    )
    engine.setup()
    engine.calibrate_instance('Alec Klein')  # test wheter the KeyError is raised
