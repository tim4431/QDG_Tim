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
    # print("sleeping")
    # time.sleep(3600 * 5)
    from works.w_subw_4e25 import work_4e25
    from works.w_grating_639a import work_grating_639a

    # 4e25_minback
    work_4e25_minback = work_4e25
    work_4e25_minback["simulation_typ"] = 2
    work_4e25_minback["grating_typ"] = "inverse_grating"
    work_4e25_minback["N"] = 36
    work_4e25_minback["paras_init"] = "4e25"
    # 639a_minback
    work_grating_639a_minback = work_grating_639a
    work_grating_639a_minback["simulation_typ"] = 2
    work_grating_639a_minback["grating_typ"] = "inverse_grating"
    work_grating_639a_minback["paras_init"] = "639a"
    # e86d_minback
    work_grating_e86d_minback = load_json("e86d")
    work_grating_e86d_minback["simulation_typ"] = 2
    work_grating_e86d_minback["grating_typ"] = "inverse_grating"
    work_grating_e86d_minback["paras_init"] = "e86d"
    #
    works = [work_4e25_minback, work_grating_639a_minback, work_grating_e86d_minback]
    #
    work_loader(works, "min_back,4e25,639a,e86d_test3")
