import json
import hashlib
import uuid
from copy import deepcopy
import os
from const_var import DEFAULT_PARA


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
    uuid = _generate_uuid(data)
    data["uuid"] = uuid
    # Save the JSON object to a file
    setup_wd(uuid)
    json_filename = uuid_to_jsonname(uuid)
    with open(json_filename, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)
    return uuid


def load_json(uuid):
    json_filename = uuid_to_jsonname(uuid)
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)
        # check if uuid is correct
        if "uuid" in data:
            if uuid != data["uuid"]:
                raise ValueError("uuid is not correct, file is modified")
            data.pop("uuid")
        return data


if __name__ == "__main__":
    # Sample JSON data
    data = {
        "lambda_0": 1.326e-6,
        "FWHM": 0.0833e-6,
        "alpha": 0.02,
        "penalty": (0.05, 50e-9),
        "maxiter": 90,
        "SOURCE_typ": "gaussian",
    }
    uuid = save_json(data)
    print(uuid_to_wd(uuid))
    print(uuid)
    print(uuid_to_jsonname(uuid))
    data = load_json(uuid)
    print(data)
