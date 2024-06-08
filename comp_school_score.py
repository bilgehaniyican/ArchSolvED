import numpy as np
from solver.enums import ClimateRoomType, Facing
from solver.enums import Climate
from solver.solution import get_climate_scoring

with open("school.csv", "r") as fd:
    lines = fd.readlines()

units = np.zeros((len(ClimateRoomType), len(Facing)))
for i, line in enumerate(lines):
    for j, cell in enumerate(line.split(";")):
        units[i, j] = cell

for facing in Facing:
    for climate in Climate:
        scoring = get_climate_scoring(climate)
        score = scoring * units

        print(facing, climate, score[0].sum() / units[0].sum(), score.sum() / units.sum())

    units = np.roll(units, 1, 1)
