from time_util import *
import csv


def load_data(fileDateStr):
    # load data from csv file
    # before curtime, up to 1 hour
    # return a list of data

    csv_file = open_csv(fileDateStr)
    csv_reader = csv.DictReader(csv_file)
    #
    # time at col 1
    # temperature at col 3
    timedata = []
    tempdata = []
    for row in csv_reader:
        timedata.append(row["Timestamp"])
        tempdata.append(row["Temperature (C)"])
    csv_file.close()
    #
    return timedata, tempdata


if __name__ == "__main__":
    _, _, fileDateStr = get_time_date()
    timedata, tempdata = load_data(fileDateStr)
    print(timedata)
    print(tempdata)
