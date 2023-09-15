from lumapi_optimize import load_work
import matplotlib.pyplot as plt
from json_uuid import load_json, save_json, uuid_to_logname, uuid_to_wd
import os
import logging
from datetime import datetime
from setup_logger import create_logger, close_logger
import shutil


def work_loader(workList, prefix):
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
            msg = str(i) + " uuid: " + uuid + " finished"
            loader_logger.info(msg)
        else:
            msg = str(i) + " uuid: " + uuid + " unfinished"
            loader_logger.info(msg)
            #
            try:
                # os.rmdir(uuid_to_wd(uuid))
                shutil.rmtree(uuid_to_wd(uuid))
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
    work_4e25 = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_crop_1 = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 102,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }

    work_inverse_1 = {
        "lambda_0": 1.326e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.03, 100e-9]],
        "N": 6,
        "NL": 2,
        "NH": 2,
        "maxiter": 1000,
        # "paras_init": "4e25",
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "grating_typ": "inverse_grating",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_inverse_2 = {
        "lambda_0": 1.326e-6,
        "FWHM": 100e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.03, 100e-9]],
        "N": 6,
        "NL": 2,
        "NH": 2,
        "maxiter": 1000,
        # "paras_init": "4e25",
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "grating_typ": "inverse_grating",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_inverse_3 = {
        "lambda_0": 1.326e-6,
        "FWHM": 100e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.03, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 1000,
        "paras_init": "4e25",
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "grating_typ": "inverse_grating",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_23 = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 3,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_23_bw20 = {
        "lambda_0": 1.326e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 3,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_23_bw70 = {
        "lambda_0": 1.326e-6,
        "FWHM": 70e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 3,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    #
    work_grating_1 = {
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
    }
    work_grating_1_1120 = {
        "lambda_0": 1.12e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1160 = {
        "lambda_0": 1.16e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1200 = {
        "lambda_0": 1.2e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1240 = {
        "lambda_0": 1.24e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1280 = {
        "lambda_0": 1.28e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1315 = {
        "lambda_0": 1.315e-6,
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
    }
    work_grating_1_1320 = {
        "lambda_0": 1.32e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1330 = {
        "lambda_0": 1.33e-6,
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
    }
    work_grating_1_1335 = {
        "lambda_0": 1.335e-6,
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
    }
    work_grating_1_1360 = {
        "lambda_0": 1.36e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1400 = {
        "lambda_0": 1.40e-6,
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
    }
    work_grating_1_1440 = {
        "lambda_0": 1.44e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1480 = {
        "lambda_0": 1.48e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_1520 = {
        "lambda_0": 1.52e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    work_grating_1_apodized = {
        "lambda_0": 1.326e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 25,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "grating_typ": "apodized_grating",
        "start_radius": 12e-6,
    }
    #
    work_grating_1_single = {
        "lambda_0": 1.326e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 18,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "single",
        "SOURCE_typ": "gaussian_released",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }
    #
    work_4e25_maxT = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "single",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_1550 = {
        "lambda_0": 1.550e-6,
        "FWHM": 60e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_1330 = {
        "lambda_0": 1.330e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.03, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_min60 = {
        "lambda_0": 1.3260e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.02, 10e-9], [0.03, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 60e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_min60_N7 = {
        "lambda_0": 1.3260e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 7,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 60e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_1336 = {
        "lambda_0": 1.336e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_1280 = {
        "lambda_0": 1.28e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_1370 = {
        "lambda_0": 1.37e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_apodized = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "paras_init": "4e25",
        "FOM_typ": "square",
        "grating_typ": "apodized_subw_grating",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_1336_apodized = {
        "lambda_0": 1.336e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.03, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "paras_init": "4e25",
        "FOM_typ": "square",
        "grating_typ": "apodized_subw_grating",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_ade1_apodized = {
        "lambda_0": 1.326e-6,
        "FWHM": 60e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 10,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "paras_init": "ade1",
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "grating_typ": "apodized_grating",
        "start_radius": 12e-6,
    }
    work_4e25_21 = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_21_apodized = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 1,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "grating_typ": "apodized_subw_grating",
        "SOURCE_typ": "gaussian_released",
        "start_radius": 12e-6,
    }
    work_4e25_packaged = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 2,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "start_radius": 12e-6,
    }
    work_4e25_packaged_23 = {
        "lambda_0": 1.326e-6,
        "FWHM": 40e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 9,
        "NL": 2,
        "NH": 3,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 20e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "start_radius": 12e-6,
    }
    work_grating_1_packaged = {
        "lambda_0": 1.326e-6,
        "FWHM": 20e-9,
        "alpha": 0.00,
        "penalty": [[0.01, 10e-9], [0.02, 100e-9]],
        "N": 18,
        "maxiter": 100,
        "MIN_FEATURE_SIZE": 40e-9,
        "FOM_typ": "square",
        "SOURCE_typ": "gaussian_packaged",
        "grating_typ": "grating",
        "start_radius": 12e-6,
    }

if __name__ == "__main__":  # type: ignore
    works_test = [work0]  # type: ignore
    # works = [work1, work2, work3]
    # works = [work9, work10, work11, work11_5, work12, work13, work14, work15, work16]
    # works = [work9,work10,work11,work12,work13,work14]
    # works = [work_inverse_1, work_inverse_2, work_inverse_3]
    # works = [work_4e25_1330, work_4e25_min60]
    # works = [work_4e25_apodized, work_4e25_1336_apodized]
    # works = [
    #     work_grating_1_1200,
    #     work_grating_1_1240,
    #     work_grating_1_1280,
    #     work_grating_1_1320,
    #     work_grating_1_1360,
    #     work_grating_1_1400,
    #     work_grating_1_1440,
    # ]
    works = [
        work_grating_1_1120,
        work_grating_1_1160,
        work_grating_1_1200,
        work_grating_1_1240,
        work_grating_1_1280,
        work_grating_1_1320,
        work_grating_1_1360,
        work_grating_1_1400,
        work_grating_1_1440,
        work_grating_1_1480,
        work_grating_1_1520,
    ]
    # works = [work_4e25_1280, work_4e25_1370]
    # works = [work_4e25_inverse]
    # works = [work_4e25_packaged, work_4e25_packaged_23, work_grating_1_packaged]
    work_loader(works, prefix="grating_1120-1520_list_packaged")
    # work_loader(works, prefix="4e25_square_bw100_inverse")
    # work_loader(works_test)
