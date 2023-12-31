DEFAULT_PARA = {
    "plot": False,
    "lambda_0": 1.326e-6,
    "FWHM": 0.0833e-6,
    "alpha": 0.00,
    "penalty": [[0.01, 10e-9]],
    "SOURCE_typ": "gaussian_released",
    "NL": 2,
    "NH": 3,
    "N": 14,
    "MIN_FEATURE_SIZE": 50.0,
    "FOM_typ": "square",
    "grating_typ": "subw_grating",  # ["grating","subw_grating","apodized_grating","apodized_subw_grating","inverse_taper_grating","inverse_grating"]
    "paras_init": None,
    "maxiter": 90,
    "logger": None,
    "start_radius": 10e-6,
    "taper_angle": 24,
    "source_angle": 10,
    "source_x": 17e-6,
    "simulation_typ": 0,  # 0: forward, 1: backward, 2: forward and backward
    "BOX": "Air",  # ["Air", "SiO2"]
    "TOX": "Air",  # ["Air", "SiO2"]
    "etch_typ": "full",  # ["full", "partial"]
}
