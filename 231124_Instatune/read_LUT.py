import csv


import numpy as np

def read_nearest_wavelength(file_path, target_wavelengths):
    data = np.genfromtxt(file_path, delimiter=',', skip_header=1)
    FM_DAC = data[:,1]
    BM_DAC = data[:,2]
    PH_DAC = data[:,3]
    SOA_DAC = data[:,4]
    WL_Target = data[:,5]

    vals=[]
    for target_wavelength in target_wavelengths:
        nearest_index = np.argmin(np.abs(WL_Target - target_wavelength))
        nearest_row = data[nearest_index]
        if np.abs(WL_Target[nearest_index] - target_wavelength) > 0.1:
            raise ValueError("Nearest wavelength {:.4f} is too far from target wavelength {:.4f}".format(WL_Target[nearest_index], target_wavelength))
        else:
            print("Find nearest wavelength {:.4f}".format(nearest_row[5]))
            val = (int(FM_DAC[nearest_index]), int(BM_DAC[nearest_index]), int(PH_DAC[nearest_index]), int(SOA_DAC[nearest_index]))
            vals.append(val)
    return vals


def read_LUT(wavelength_list):
    lut = []
    file_path = "./DJ133_LUT_0v0.csv"
    return read_nearest_wavelength(file_path, wavelength_list)


if __name__ == "__main__":
    wavelength_list = [1325, 1326, 1327]
    lut = read_LUT(wavelength_list)
    print(lut)
