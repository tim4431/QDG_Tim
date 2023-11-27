import csv


def read_nearest_wavelength(file_path, target_wavelength):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        nearest_row = {}
        min_difference = float("inf")

        for row in reader:
            wavelength = float(row["WL Target"])
            difference = abs(wavelength - target_wavelength)
            if difference < min_difference:
                min_difference = difference
                nearest_row = row

        # return nearest_row
        # (Front Mirror, Back Mirror, Phase, SOA)
        FM_DAC = float(nearest_row["FM DAC"])
        BM_DAC = float(nearest_row["BM DAC"])
        PH_DAC = float(nearest_row["PH DAC"])
        SOA_DAC = float(nearest_row["SOA DAC"])
        WL_Target = float(nearest_row["WL Target"])
        if abs(WL_Target - target_wavelength) > 0.1:
            raise ValueError(
                "Nearest wavelength {:.4f} is too far from target wavelength {:.4f}"
            )
        else:
            print("Find nearest wavelength {:.4f}".format(WL_Target))
        return (FM_DAC, BM_DAC, PH_DAC, SOA_DAC)


def read_LUT(wavelength_list):
    lut = []
    file_path = "./DJ133_LUT_0v0.csv"
    for wavelength in wavelength_list:
        nearest_row = read_nearest_wavelength(file_path, wavelength)
        # print(nearest_row)
        lut.append(nearest_row)
    return lut


if __name__ == "__main__":
    wavelength_list = [1325, 1326, 1327]
    lut = read_LUT(wavelength_list)
    print(lut)
