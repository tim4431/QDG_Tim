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
            loader_logger.error("Error in uuid: " + uuid + str(e))
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
    from works.w_230918_4e25 import work_4e25

    # sweep lambda from 1296 to 1356, spacing 10
    work_4e25_sweep_lambda = work_para_sweeper(
        work_4e25, np.arange(1296, 1366, 10) * 1e-9, "lambda_0"
    )
    # sweep source_angle from 10 to 30, spacing 5
    work_4e25_sweep_source_angle = work_para_sweeper(
        work_4e25, range(10, 35, 5), "source_angle"
    )
    # sourcefixed at 17
    work_4e25_sourcefixed = deepcopy(work_4e25)
    work_4e25_sourcefixed["grating_typ"] = "subw_grating_sourcefixed"
    work_4e25_sourcefixed["source_x"] = 17e-6
    # sweep lambda from 1296 to 1356, spacing 10
    work_4e25_sweep_lambda_sourcefixed = work_para_sweeper(
        work_4e25_sourcefixed, np.arange(1296, 1366, 10) * 1e-9, "lambda_0"
    )
    # merge works
    # works = work_4e25_sweep_lambda + work_4e25_sweep_source_angle
    works = work_4e25_sweep_lambda + work_4e25_sweep_source_angle+work_4e25_sweep_lambda_sourcefixed
    print(len(works))
    #
    work_loader(works, "4e25_sweep_lambda_source_angle")
