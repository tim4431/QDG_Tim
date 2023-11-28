import csv


import numpy as np

def load_LUT(target_wavelengths):
    file_path = "./DJ133_LUT_0v0.csv"
    data = np.genfromtxt(file_path, delimiter=',', skip_header=1)
    IDX = data[:,0]
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
            val = [int(IDX[nearest_index]),int(FM_DAC[nearest_index]), int(BM_DAC[nearest_index]),\
                    int(PH_DAC[nearest_index]), int(SOA_DAC[nearest_index]),float(WL_Target[nearest_index])]
            vals.append(val)
    return vals


def load_DAC(wavelength_list):
    vals = load_LUT(wavelength_list)
    DAC = [val[1:5] for val in vals]
    return DAC

def save_LUT(file_path, lut):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['IDX', 'FM_DAC', 'BM_DAC', 'PH_DAC', 'SOA_DAC', 'WL_Target'])
        for i,val in enumerate(lut):
            val[0] = i
            writer.writerow(val)

if __name__ == "__main__":
    wavelength_list = [1310, 1315,1320]
    lut = load_LUT(wavelength_list)
    save_LUT("./DJ133_LUT_temp.csv", lut)