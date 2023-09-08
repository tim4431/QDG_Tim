import sys
import os


def add_lumerical_path():
    # add lumerical api path
    pathList = [
        "C:\\Program Files\\Lumerical\\v221\\api\\python\\",
        "C:\\Program Files\\Lumerical\\FDTD\\api\\python\\",
        "D:\\software\\Lumerical\\Lumerical\\v221\\api\\python",
    ]
    for pathName in pathList:
        if os.path.exists(pathName):
            sys.path.append(pathName)
            break
    sys.path.append(os.path.dirname(__file__))  # Current directory
