import numpy as np
import matplotlib.pyplot as plt

intruction_str_List = []


def move_comp_str(compName: str, x, y):
    return "MOVE {:s} ({:d} {:d});".format(compName, round(x), round(y))


def move_comp(compName: str, x, y):
    global intruction_str_List
    intruction_str_List.append(move_comp_str(compName, x, y))


compNameDCB = ["U$14", "U$7", "U$2", "U$3", "U$4", "U$5"]
compNameDCU = ["U$16", "U$15", "U$8", "U$9", "U$10", "U$11"]
compNameMW = ["U$13", "U$1", "U$12", "U$6"]

H1Board = 1845
HMID = H1Board / 2
move_comp("J2", 3440, H1Board + 150)
move_comp("J1", 3440, -150)
DIS_SMA_1 = 430
DIS_SMA_2 = 1100
X_SMA_1 = 2910
X_SMA_2 = 3360
move_comp("J4", X_SMA_1, HMID + DIS_SMA_1 / 2)
move_comp("J3", X_SMA_1, HMID - DIS_SMA_1 / 2)
move_comp("J6", X_SMA_2, HMID + DIS_SMA_2 / 2)
move_comp("J5", X_SMA_2, HMID - DIS_SMA_2 / 2)
MW_SPACING = 100
for i in range(4):
    move_comp(compNameMW[i], 445, HMID + MW_SPACING * (1.5 - i))
DC_SPACING = 40
for i in range(5):
    move_comp(compNameDCU[i], 40 + i * DC_SPACING, 1170)
    move_comp(compNameDCB[i], 40 + i * DC_SPACING, 670)
for i in range(5,6):
    move_comp(compNameDCU[i], 40 +5*60+40+(i-5) * DC_SPACING, 1170)
    move_comp(compNameDCB[i], 40 +5*60+40+(i-5) * DC_SPACING, 670)
# merge command
print(" ".join(intruction_str_List))
