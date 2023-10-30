import numpy as np
import matplotlib.pyplot as plt

intruction_str_List = []


def move_comp_str(compName: str, x, y):
    return "MOVE {:s} ({:d} {:d});".format(compName, round(x), round(y))


def move_comp(compName: str, x, y):
    global intruction_str_List
    intruction_str_List.append(move_comp_str(compName, x, y))


compNameDCU = ["U$11", "U$10", "U$9", "U$8"]
compNameDCB = ["U$5", "U$4", "U$3", "U$2"]
compNameMW = ["U$13", "U$1", "U$12", "U$6"]

H1Board = 1845
move_comp("J2", 3030, 1885)
move_comp("J1", 3030, -40)
DIS_SMA_1 = 322
DIS_SMA_2 = 880
X_SMA_1 = 2790
X_SMA_2 = 3140
move_comp("J4", DIS_SMA_1, H1Board / 2 + DIS_SMA_1 / 2)
move_comp("J3", DIS_SMA_1, H1Board / 2 - DIS_SMA_1 / 2)
move_comp("J6", DIS_SMA_2, H1Board / 2 + DIS_SMA_2 / 2)
move_comp("J5", DIS_SMA_2, H1Board / 2 - DIS_SMA_2 / 2)

# merge command
print(" ".join(intruction_str_List))
