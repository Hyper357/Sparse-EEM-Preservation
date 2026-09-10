import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]/'src'))
from dual_endpoint_analysis import random_configs, validate_config

def test_random_fixed_sets_are_unique_and_feasible():
    grid=list(range(300,701,5)); sets=random_configs(grid,4,500,42,20)
    assert len(sets)==500 and len({tuple(x) for x in sets})==500
    for x in sets: validate_config(grid,x,20)
