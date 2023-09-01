from time_util import *
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def load_data(fileDateStr):
    # load data from csv file
    # before curtime, up to 1 hour
    # return a list of data

    data = pd.read_csv(fileDateStr + ".csv", parse_dates=["Timestamp"])
    # Convert Temperature (C) to Fahrenheit for plotting (optional)
    # data["Temperature (F)"] = (data["Temperature (C)"] * 9 / 5) + 32
    return data["Timestamp"], data["Temperature (C)"]


def plot_data(fileDateStr):
    timedata, tempdata = load_data(fileDateStr)

    plt.figure(figsize=(10, 6))
    plt.plot(
        timedata,
        tempdata,
        marker="o",
        linestyle="-",
        color="b",
        label="Temperature (°C)",
    )
    plt.xlabel("Timestamp")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature vs. Time")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show the plot
    plt.show()


if __name__ == "__main__":
    _, _, fileDateStr = get_time_date()
    plot_data(fileDateStr)
