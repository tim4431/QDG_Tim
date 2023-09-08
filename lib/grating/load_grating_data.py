from typing import List
import numpy as np
import pickle


def load_grating_data(save_folder: str, grating_len: float) -> List:
    import os
    from spins.invdes.problem_graph import optplan
    from spins.invdes.problem_graph import workspace

    # Load the optimization plan.
    with open(os.path.join(save_folder, "optplan.json")) as fp:
        plan = optplan.loads(fp.read())
    dx = plan.transformations[-1].parametrization.simulation_space.mesh.dx

    # Load the data from the latest log file.
    with open(os.path.join(save_folder, "opt_disc.chkpt.pkl"), "rb") as fp:
        log_data = pickle.load(fp)

        coords = (
            log_data["parametrizations"]["parametrization.grating.0"]["vector"] * dx
        )

        if plan.transformations[-1].parametrization.inverted:
            coords = np.insert(coords, 0, 0, axis=0)
            coords = np.insert(coords, len(coords), grating_len, axis=0)
    return list(coords * 1e-3)
