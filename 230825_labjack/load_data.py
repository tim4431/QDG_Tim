from time_util import *
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Union
import logging


def load_data(fileDateStr, span: str = "1D"):
    # load data from csv file
    data = pd.read_csv(fileDateStr + ".csv", parse_dates=["Timestamp"])
    # Convert Temperature (C) to Fahrenheit for plotting (optional)
    # data["Temperature (F)"] = (data["Temperature (C)"] * 9 / 5) + 32
    timedata = data["Timestamp"]
    tempdata = data["Temperature (C)"]
    if span == "1D":
        return timedata, tempdata
    elif span == "1H":
        length = int(3600 / RECORD_INTERVAL_S)
        return timedata.tail(length), tempdata.tail(length)


def plot_data(fileDateStr, span: str = "1D"):
    timedata, tempdata = load_data(fileDateStr, span=span)  # type: ignore

    plt.figure(figsize=(10, 6))
    plt.plot(
        timedata,
        tempdata,
        marker="o",
        linestyle="-",
        color="b",
        label="Temperature (°C)",
    )
    # add a horizontal line at 26 C
    plt.axhline(
        y=TEMPERATURE_THRESHOLD,
        color="r",
        linestyle="--",
        label="Threshold ({:d} °C)".format(TEMPERATURE_THRESHOLD),
    )
    #
    plt.xlabel("Timestamp")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature vs. Time")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    img_fileName = "{:s}_{:s}_temperature.png".format(fileDateStr, span)
    logging.info("Saving image to: " + img_fileName)
    try:
        plt.savefig(
            img_fileName,
            bbox_inches="tight",
            dpi=100,
        )
        logging.info("Image saved")
    except Exception as e:
        logging.error("Error: " + str(e))
    #
    return img_fileName


if __name__ == "__main__":
    _, _, fileDateStr = get_time_date()
    img_fileName = plot_data(fileDateStr, span="1D")
    print(img_fileName)
