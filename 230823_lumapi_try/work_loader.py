from lumapi_optimize import load_work
import matplotlib.pyplot as plt
from json_uuid import load_json, save_json, uuid_to_logname, uuid_to_wd
import os
import logging
from datetime import datetime
from setup_logger import create_logger, close_logger


def work_loader(workList, prefix):
    cwd = os.getcwd()
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d_%H%M%S")
    loader_dataName = os.path.join(cwd, dt_string + "_" + prefix)
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
    with open(loader_dataName + "_uuid_list.txt", "w") as uuid_file:
        for i, uuid in enumerate(uuid_List):
            if uuid in uuid_finished:
                msg = str(i) + " uuid: " + uuid + " finished"
                loader_logger.info(msg)
                uuid_file.write(msg + "\n")
            else:
                msg = str(i) + " uuid: " + uuid + " unfinished"
                loader_logger.info(msg)
                uuid_file.write(msg + "\n")
                #
                try:
                    os.rmdir(uuid_to_wd(uuid))
                except Exception as e:
                    loader_logger.error("Error in deleting uuid: " + str(uuid) + str(e))

    # >>> end <<<
    loader_logger.info("Work loader end")


if __name__ == "__main__":
    work0 = {
        "lambda_0": 1.326e-6,
        "FWHM": 0.0833e-6,
        "alpha": 0.02,
        "penalty": [[0.02, 10e-9]],
        "maxiter": 5,
        "SOURCE_typ": "gaussian_released",
    }  # for test use
    work1 = {
        "uid": 1,
        "lambda_0": 1.326e-6,
        "FWHM": 0.0833e-6,
        "alpha": 0.02,
        "penalty": (0.05, 50e-9),
        "maxiter": 90,
        "SOURCE_typ": "gaussian_released",
    }  # done
    work2 = {
        "uid": 2,
        "lambda_0": 1.326e-6,
        "FWHM": 0.15e-6,
        "alpha": 0.04,
        "penalty": (0.05, 50e-9),
        "maxiter": 90,
        "SOURCE_typ": "gaussian_released",
    }  # done
    work3 = {
        "uid": 3,
        "lambda_0": 1.340e-6,
        "FWHM": 0.15e-6,
        "alpha": 0.02,
        "penalty": (0.05, 50e-9),
        "maxiter": 90,
        "SOURCE_typ": "gaussian_released",
    }  # done

    para_done = (
        [
            8.812476273029164531e-07,
            2.200684041028692917e-01,
            8.208995755163028818e-01,
            5.731574927604761172e-01,
            1.500027252161092499e-05,
        ],
    )
    # >>> single, sweep N
    work4 = {
        "lambda_0": 1.326e-6,
        "FWHM": 0.1e-6,
        "alpha": 0.02,
        "penalty": [[0.04, 10e-9]],
        "N": 8,
        "NL": 2,
        "NH": 2,
        "maxiter": 90,
        "FOM_typ": "single",
        "SOURCE_typ": "gaussian_released",
    }
    work5 = {
        "lambda_0": 1.326e-6,
        "FWHM": 0.1e-6,
        "alpha": 0.02,
        "penalty": [[0.04, 10e-9]],
        "N": 11,
        "NL": 2,
        "NH": 2,
        "maxiter": 90,
        "FOM_typ": "single",
        "SOURCE_typ": "gaussian_released",
    }
    work6 = {
        "lambda_0": 1.326e-6,
        "FWHM": 0.1e-6,
        "alpha": 0.02,
        "penalty": [[0.04, 10e-9]],
        "N": 14,
        "NL": 2,
        "NH": 2,
        "maxiter": 90,
        "FOM_typ": "single",
        "SOURCE_typ": "gaussian_released",
    }
    # >>> single, sweep lambda
    work7 = {
        "lambda_0": 1.34e-6,
        "FWHM": 0.1e-6,
        "alpha": 0.02,
        "penalty": [[0.04, 10e-9]],
        "N": 14,
        "NL": 2,
        "NH": 2,
        "maxiter": 90,
        "FOM_typ": "single",
        "SOURCE_typ": "gaussian_released",
    }
    work8 = {
        "lambda_0": 1.55e-6,
        "FWHM": 0.1e-6,
        "alpha": 0.02,
        "penalty": [[0.04, 10e-9]],
        "N": 14,
        "NL": 2,
        "NH": 2,
        "maxiter": 90,
        "FOM_typ": "single",
        "SOURCE_typ": "gaussian_released",
    }
    # >>> square, sweep FWHM
    work9 = {
        "lambda_0": 1.326e-6,
        "FWHM": 100e-9,
        "alpha": 0.00,
        "penalty": [[0.002, 10e-9], [0.002, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work10 = {
        "lambda_0": 1.326e-6,
        "FWHM": 200e-9,
        "alpha": 0.00,
        "penalty": [[0.002, 10e-9], [0.002, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work11 = {
        "lambda_0": 1.326e-6,
        "FWHM": 100e-9,
        "alpha": 0.00,
        "penalty": [[0.002, 10e-9], [0.002, 100e-9]],
        "N": 9,
        "NL": 1,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work12 = {
        "lambda_0": 1.326e-6,
        "FWHM": 200e-9,
        "alpha": 0.00,
        "penalty": [[0.002, 10e-9], [0.002, 100e-9]],
        "N": 9,
        "NL": 1,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work13 = {
        "lambda_0": 1.326e-6,
        "FWHM": 150e-9,
        "alpha": 0.00,
       "penalty": [[0.002, 10e-9], [0.002, 100e-9]],
        "N": 12,
        "NL": 1,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work14 = {
        "lambda_0": 1.326e-6,
        "FWHM": 150e-9,
        "alpha": 0.00,
        "penalty": [[0.002, 10e-9], [0.002, 100e-9]],
        "N": 15,
        "NL": 1,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }

if __name__ == "__main__":  # type: ignore
    works_test = [work0]  # type: ignore
    # works = [work1, work2, work3]
    # works = [work9, work10, work11, work11_5, work12, work13, work14, work15, work16]
    works = [work9,work10,work11,work12,work13,work14]
    work_loader(works, prefix="NL_NH_sweep_broad")
    # work_loader(works_test)
