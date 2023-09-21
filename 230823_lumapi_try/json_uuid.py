import json
import hashlib
import uuid
from copy import deepcopy
import os
from const_var import DEFAULT_PARA
import numpy as np


def _generate_uuid(data):
    # pop out uuid term
    data_copy = deepcopy(data)
    if "uuid" in data_copy:
        data_copy.pop("uuid")
    #
    json_data = json.dumps(data_copy, sort_keys=True)
    md5_hash = hashlib.md5(json_data.encode()).hexdigest()
    return str(md5_hash[:4])


def uuid_to_wd(uuid):
    cwd = os.getcwd()
    if cwd.endswith(uuid):  # if cwd ends with uuid
        return cwd
    else:
        return os.path.join(cwd, uuid)


def setup_wd(uuid):
    wd = uuid_to_wd(uuid)
    if not os.path.exists(wd):
        os.mkdir(wd)
    return wd


def uuid_to_jsonname(uuid):
    return os.path.join(uuid_to_wd(uuid), uuid + ".json")


def uuid_to_logname(uuid):
    return os.path.join(uuid_to_wd(uuid), uuid + ".log")


def save_json(data):
    # Generate a uuid
    # uuid = _generate_uuid(_default_wrapper(data))
    uuid = _generate_uuid(data)
    data["uuid"] = uuid
    # Save the JSON object to a file
    setup_wd(uuid)
    json_filename = uuid_to_jsonname(uuid)
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)
    return uuid


# def _default_wrapper(data):
#     for key in DEFAULT_PARA.keys():
#         if key not in data:
#             data[key] = DEFAULT_PARA[key]
#     return data


def load_json(uuid):
    json_filename = uuid_to_jsonname(uuid)
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)
        # check if uuid is correct
        if "uuid" in data:
            # if uuid != data["uuid"]:
            #     raise ValueError("uuid is not correct, file is modified")
            data.pop("uuid")
        # return _default_wrapper(data)
        return data


def getprefixName(uuid) -> str:
    data = load_json(uuid)
    lambda_0 = data.get("lambda_0", None)
    FWHM = data.get("FWHM", None)
    assert (lambda_0 is not None) and (
        FWHM is not None
    ), "lambda_0 and FWHM must be specified"
    #
    prefixName = "{:s}_{:.1f}_bw={:.1f}".format(uuid, lambda_0 * 1e9, FWHM * 1e9)
    return prefixName


def getdataName(uuid) -> str:
    prefixName = getprefixName(uuid)
    wd = uuid_to_wd(uuid)
    return os.path.join(wd, prefixName)


def load_paras(uuid):
    dataName = getdataName(uuid)
    return np.loadtxt(dataName + "_paras.txt")


if __name__ == "__main__":
    uuid_to_wd("e199")
