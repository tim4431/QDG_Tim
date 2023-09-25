from lumapi_optimize import load_work
import matplotlib.pyplot as plt
from json_uuid import load_json, save_json, uuid_to_logname, uuid_to_wd
import os
import logging
from datetime import datetime
from setup_logger import create_logger, close_logger
import shutil
import numpy as np
from copy import deepcopy
from merge_data_transmission import merge_data_transmission
import time


def work_loader(workList, prefix, merge_data=False):
    cwd = os.getcwd()
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M%S")
    loader_dataName = os.path.join(cwd, "logs", dt_string + "_" + prefix)
    loader_logger = create_logger(loader_dataName + ".log")
    loader_logger.info("Work loader start")

    # >>> create work list <<<
    uuid_List = []
    for i, work in enumerate(workList):
        uuid = save_json(work)
        # add prefix
        # uuid = prefix + "_" + str(i) + "_" + uuid
        uuid_List.append(uuid)
        loader_logger.info("uuid: " + uuid + " created")
        loader_logger.info("work: " + str(work))

    # >>> load work <<<
    uuid_finished = []
    for uuid in uuid_List:
        try:
            logger = create_logger(uuid_to_logname(uuid))
            load_work(uuid, logger)
            loader_logger.info("uuid: " + uuid + " finished")
            uuid_finished.append(uuid)
        except KeyboardInterrupt:
            loader_logger.info("KeyboardInterrupt, stop")
            break
        except Exception as e:
            loader_logger.error("Error in uuid: " + uuid + " : " + str(e))
        finally:
            close_logger(logger)  # type: ignore

    #
    # >>> summary <<<
    for i, uuid in enumerate(uuid_List):
        if uuid in uuid_finished:
            msg = str(i) + " uuid: \t" + uuid + "\t finished"
            loader_logger.info(msg)
        else:
            msg = str(i) + " uuid: \t" + uuid + "\t unfinished"
            loader_logger.info(msg)
            #
            try:
                # os.rmdir(uuid_to_wd(uuid))
                shutil.rmtree(uuid_to_wd(uuid))
            except Exception as e:
                loader_logger.error("Error in deleting uuid: " + str(uuid) + str(e))
    # >>> merge data <<<
    if merge_data:
        # create dir named by prefix
        os.mkdir(prefix)
        merge_data_transmission(uuid_List, merge_dst=prefix)

    # >>> end <<<
    loader_logger.info("Work loader end")


def work_para_sweeper(work_template, sweep_range, sweep_var_name):
    works = []
    for sweep_var in sweep_range:
        work = deepcopy(work_template)
        work[sweep_var_name] = sweep_var
        works.append(work)
    return works


if __name__ == "__main__":  # type: ignore
    # print("sleeping")
    # time.sleep(3600 * 5)

    # 639a_bst
    work_grating_639a = {
        "lambda_0": 1.326e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "grating_typ": "grating",
        "start_radius": 12e-6,
        "simulation_typ": 0,
    }
    work_grating_639a_bst = work_grating_639a
    work_grating_639a_bst["grating_typ"] = "grating"
    work_grating_639a_bst["simulation_typ"] = 2
    work_grating_639a_bst["source_angle"] = 14.8
    work_grating_639a_bst["N"] = 30
    work_grating_639a_bst["penalty"] = [[0.02, 10e-9], [0.02, 100e-9]]
    works = [work_grating_639a_bst]
    work_loader(works, "639a_bst")
