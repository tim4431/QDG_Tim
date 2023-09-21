import sys, os
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
import shutil
from matplotlib.gridspec import GridSpec

sys.path.append("..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d
from lib.lumerical.util import add_lumerical_path
from lib.gaussian.FOM_analysis import FOM_analysis
from json_uuid import load_json, uuid_to_wd, load_paras, getdataName
from typing import Union, List, Tuple, Dict, Any, Optional, Callable, Iterable

analysis = FOM_analysis()


add_lumerical_path()

from const_var import DEFAULT_PARA


def process_data(fdtd, SOURCE_typ) -> tuple:
    if "gaussian" in SOURCE_typ:
        res = fdtd.getresult("output", "T")
        mod_overlap = fdtd.getresult("output_TE", "expansion for output_TE")
    elif SOURCE_typ == "fiber":
        res = fdtd.getresult("FDTD::ports::port 2", "T")
    #
    l = np.squeeze(res["lambda"])  # type: ignore
    # T = np.squeeze(np.abs(res["T"]))  # type: ignore
    T = np.squeeze((-1.0) * mod_overlap["T_net"])  # type: ignore
    # sort T using increasing l
    idx = np.argsort(l)
    l = l[idx]
    T = T[idx]
    #
    return l, T


def calculate_FOM(l, T, **kwargs):
    # >>> load paras <<< #
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    # alpha = kwargs.get("alpha", DEFAULT_PARA["alpha"])
    FOM_typ = kwargs.get("FOM_typ", DEFAULT_PARA["FOM_typ"])

    # >>> analysis <<< #
    _crop_range = 3 * FWHM
    l_c, T_c = analysis.data_crop(l, T, lambda_0, _crop_range)
    T_des = analysis.gaussian_curve(l_c, lambda_0, FWHM)
    cross_correlation = analysis.cross_correlation(T_c, T_des)
    norm_cross_correlation = analysis.norm_cross_correlation(T_c, T_des)
    maxT, lambda_maxT, FWHM_fit, CE = arb_fit_1d(False, l, T, "")  # type: ignore
    norm_T = analysis.mean_alpha(T_c, 2)
    #

    # >>> FOM <<< #
    if FOM_typ == "square":
        # print("square")
        print(norm_T, norm_cross_correlation)
        # FOM = float((norm_T + alpha) * norm_cross_correlation)
        FOM = float(norm_T * norm_cross_correlation)
    elif FOM_typ == "linear":
        # print("linear")
        # T_c1 = _data_crop(l, T, lambda_0, FWHM)
        # mean_CE = _mean_CE(T_c1)
        # print(mean_CE)
        FOM = float(norm_T * (FWHM / FWHM_fit))
        # FWHM_range = 30e-9
        # FOM = float(maxT * FWHM_range / (FWHM_range + np.abs(FWHM_fit - FWHM)))
        # FOM = float(((T_div + alpha) ** 0.2) * norm_cross_correlation)
    elif FOM_typ == "single":
        # print("single")
        T_0 = analysis.T_0(l, lambda_0, T)
        FOM = float(norm_cross_correlation * T_0)
    else:
        raise ValueError("Invalid FOM_typ: {:s}".format(FOM_typ))
    #
    return maxT, lambda_maxT, FWHM_fit, FOM


def set_params(fdtd, paras, **kwargs):
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    N = kwargs.get("N", DEFAULT_PARA["N"])
    #
    if grating_typ == "subw_grating":
        #
        Lambda = paras[0]
        fdtd.setnamed(grating_typ, "Lambda", Lambda)
        ffL = paras[1]
        fdtd.setnamed(grating_typ, "ffL", ffL)
        ffH = paras[2]
        fdtd.setnamed(grating_typ, "ffH", ffH)
        ff = paras[3]
        fdtd.setnamed(grating_typ, "ff", ff)
        fiberx = paras[4]
        #
    elif grating_typ == "subw_grating_sourcefixed":
        #
        Lambda = paras[0]
        fdtd.setnamed(grating_typ, "Lambda", Lambda)
        ffL = paras[1]
        fdtd.setnamed(grating_typ, "ffL", ffL)
        ffH = paras[2]
        fdtd.setnamed(grating_typ, "ffH", ffH)
        ff = paras[3]
        fdtd.setnamed(grating_typ, "ff", ff)
        fiberx = kwargs.get("source_x", DEFAULT_PARA["source_x"])
        #
    elif grating_typ == "apodized_subw_grating":
        # i for initial, f for final
        Lambda_i = paras[0]
        fdtd.setnamed(grating_typ, "Lambda_i", Lambda_i)
        Lambda_f = paras[1]
        fdtd.setnamed(grating_typ, "Lambda_f", Lambda_f)
        ffL_i = paras[2]
        fdtd.setnamed(grating_typ, "ffL_i", ffL_i)
        ffL_f = paras[3]
        fdtd.setnamed(grating_typ, "ffL_f", ffL_f)
        ffH_i = paras[4]
        fdtd.setnamed(grating_typ, "ffH_i", ffH_i)
        ffH_f = paras[5]
        fdtd.setnamed(grating_typ, "ffH_f", ffH_f)
        ff_i = paras[6]
        fdtd.setnamed(grating_typ, "ff_i", ff_i)
        ff_f = paras[7]
        fdtd.setnamed(grating_typ, "ff_f", ff_f)
        fiberx = paras[8]
        #
    elif grating_typ == "inverse_grating":
        pitch_list = paras[1 : 1 + N]
        fdtd.setnamed(grating_typ, "pitch_list", pitch_list)
        ff_list = paras[1 + N : 1 + 2 * N]
        fdtd.setnamed(grating_typ, "ff_list", ff_list)
        fiberx = paras[0]
        #
    elif grating_typ == "grating":
        Lambda = paras[0]
        fdtd.setnamed(grating_typ, "Lambda", Lambda)
        ff = paras[1]
        fdtd.setnamed(grating_typ, "ff", ff)
        fiberx = paras[2]
        #
    elif grating_typ == "apodized_grating":
        Lambda_i = paras[0]
        fdtd.setnamed(grating_typ, "Lambda_i", Lambda_i)
        Lambda_f = paras[1]
        fdtd.setnamed(grating_typ, "Lambda_f", Lambda_f)
        ff_i = paras[2]
        fdtd.setnamed(grating_typ, "ff_i", ff_i)
        ff_f = paras[3]
        fdtd.setnamed(grating_typ, "ff_f", ff_f)
        fiberx = paras[4]
        #
    else:
        raise ValueError("set_params: Invalid grating_typ: {:s}".format(grating_typ))
    # >>> set source x <<< #
    if "gaussian" in SOURCE_typ:
        fdtd.setnamed("source", "x", fiberx)  # type: ignore
    elif SOURCE_typ == "fiber":
        fdtd.setnamed("fiber", "x", fiberx)  # type: ignore


def _linear_apodize_func(N, x_i, x_f):
    return lambda i: x_i + (x_f - x_i) * (i / (N - 1))


def calc_min_feature(paras, **kwargs) -> float:
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    N = kwargs.get("N", DEFAULT_PARA["N"])
    #
    if grating_typ in ["subw_grating", "subw_grating_sourcefixed"]:
        NL = kwargs.get("NL", DEFAULT_PARA["NL"])
        NH = kwargs.get("NH", DEFAULT_PARA["NH"])
        #
        Lambda = paras[0]
        ffL = paras[1]
        ffH = paras[2]
        ff = paras[3]
        #
        l_H = Lambda * ff
        l_L = Lambda * (1 - ff)
        #
        min_L = (l_L / NL) * (ffL)
        min_H = (l_H / NH) * (1 - ffH)
        #
        return float(min(min_L, min_H))  # type: ignore
    elif grating_typ == "apodized_subw_grating":
        NL = kwargs.get("NL", DEFAULT_PARA["NL"])
        NH = kwargs.get("NH", DEFAULT_PARA["NH"])
        #
        Lambda_i = paras[0]
        Lambda_f = paras[1]
        ffL_i = paras[2]
        ffL_f = paras[3]
        ffH_i = paras[4]
        ffH_f = paras[5]
        ff_i = paras[6]
        ff_f = paras[7]
        #
        Lambda_func = _linear_apodize_func(N, Lambda_i, Lambda_f)
        ffL_func = _linear_apodize_func(N, ffL_i, ffL_f)
        ffH_func = _linear_apodize_func(N, ffH_i, ffH_f)
        ff_func = _linear_apodize_func(N, ff_i, ff_f)
        #
        _min_feature_size = 1
        for i in range(N):
            Lambda = Lambda_func(i)
            ff = ff_func(i)
            l_H = Lambda * ff
            l_L = Lambda * (1 - ff)
            #
            ffL = ffL_func(i)
            ffH = ffH_func(i)
            min_L = (l_L / NL) * min(ffL, (1 - ffL))
            min_H = (l_H / NH) * min(ffH, (1 - ffH))
            #
            _min_feature_size = min(_min_feature_size, min(min_L, min_H))
        return float(_min_feature_size)  # type: ignore
    elif grating_typ == "inverse_grating":
        pitch_list = paras[1 : 1 + N]
        ff_list = paras[1 + N : 1 + 2 * N]
        _min_feature = 1
        for i in range(1, N):  # the first unit does not count
            feature_i = pitch_list[i] * min((1 - ff_list[i]), ff_list[i])
            _min_feature = min(_min_feature, feature_i)
        return float(_min_feature)
    elif grating_typ == "grating":
        Lambda = paras[0]
        ff = paras[1]
        return float(min(Lambda * ff, Lambda * (1 - ff)))  # type: ignore
    elif grating_typ == "apodized_grating":
        Lambda_i = paras[0]
        Lambda_f = paras[1]
        ff_i = paras[2]
        ff_f = paras[3]
        #
        Lambda_func = _linear_apodize_func(N, Lambda_i, Lambda_f)
        ff_func = _linear_apodize_func(N, ff_i, ff_f)
        #
        _min_feature_size = 1
        for i in range(N):
            Lambda = Lambda_func(i)
            ff = ff_func(i)
            feature_i = Lambda * min((1 - ff), ff)
            _min_feature_size = min(_min_feature_size, feature_i)
        return float(_min_feature_size)
    else:
        raise ValueError(
            "calc_min_feature: Invalid grating_typ: {:s}".format(grating_typ)
        )


def fdtd_iter(
    fdtd, paras, simulation_typ: int, reload_gds=False, **kwargs
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, float, float, float]:
    """
    - l, T, R, maxT, lambda_maxT, FWHM_fit, FOM = fdtd_iter(fdtd, paras, simulation_typ, reload_gds, **kwargs)
    - simulation_typ (int): 0 - forward only, 1 - back reflection only, 2 - both
    """
    #
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    #
    # >>> run simulation, forward, 1 <<< #
    if simulation_typ in [0, 2]:
        setup_source(fdtd, dimension="2D", simulation_typ=0, **kwargs)
        fdtd.switchtolayout()
        if not reload_gds:
            set_params(fdtd, paras, **kwargs)
        fdtd.run()
        lT, T = process_data(fdtd, SOURCE_typ)
        maxT, lambda_maxT, FWHM_fit_T, FOMT = calculate_FOM(lT, T, **kwargs)  # type: ignore
    # >>> run simulation, backward, 2 <<< #
    if simulation_typ in [1, 2]:
        setup_source(fdtd, dimension="2D", simulation_typ=1, **kwargs)
        fdtd.switchtolayout()
        if not reload_gds:
            set_params(fdtd, paras, **kwargs)
        fdtd.run()
        lR, R = process_data(fdtd, SOURCE_typ)
        maxR, lambda_maxR, FWHM_fit_R, FOMR = calculate_FOM(lR, R, **kwargs)  # type: ignore
    # >>> Return result
    if simulation_typ == 0:
        return lT, T, np.zeros_like(lT), maxT, lambda_maxT, FWHM_fit_T, FOMT  # type: ignore
    elif simulation_typ == 1:
        return lR, np.zeros_like(lR), R, maxR, lambda_maxR, FWHM_fit_R, FOMR  # type: ignore
    elif simulation_typ == 2:
        return lT, T, R, maxT, lambda_maxT, FWHM_fit_T, FOMT - FOMR  # type: ignore
    else:
        raise ValueError("Invalid simulation_typ")


def optimize_wrapper(fdtd, paras, plot=False, **kwargs):
    # >>> Plot <<< #
    fig = kwargs.get("fig", None)
    axs = kwargs.get("axs", None)
    fig_transmission = kwargs.get("fig_transmission", None)
    fig_reflection = kwargs.get("fig_reflection", None)
    fig_FOM_his = kwargs.get("fig_FOM_his", None)
    fig_feature_his = kwargs.get("fig_feature_his", None)
    fig_lambda0_his = kwargs.get("fig_lambda0_his", None)
    fig_FWHM_his = kwargs.get("fig_FWHM_his", None)
    #
    # >>> History <<< #
    transmissionHist = kwargs.get("transmissionHist", [])
    reflectionHist = kwargs.get("reflectionHist", [])
    parasHist = kwargs.get("parasHist", [])
    FOMHist = kwargs.get("FOMHist", [])
    featureHist = kwargs.get("featureHist", [])
    lambda0Hist = kwargs.get("lambda0Hist", [])
    FWHMHist = kwargs.get("FWHMHist", [])
    #
    # >>> Analyse <<< #
    simulation_typ = kwargs.get("simulation_typ", DEFAULT_PARA["simulation_typ"])
    l, T, R, maxT, lambda_maxT, FWHM_fit, FOM = fdtd_iter(
        fdtd, paras, simulation_typ=simulation_typ, reload=False, **kwargs
    )
    #
    # >>> Figure of merit <<< #
    # Feature size penalty
    feature_size = calc_min_feature(paras, **kwargs)
    MIN_FEATURE_SIZE = kwargs.get("MIN_FEATURE_SIZE", DEFAULT_PARA["MIN_FEATURE_SIZE"])
    feature_size_penalty = analysis.feature_size_penalty(feature_size, MIN_FEATURE_SIZE)
    # Center wavelength penalty
    penalty = kwargs.get("penalty", DEFAULT_PARA["penalty"])
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    cw_penalty = analysis.center_wavelength_penalty(penalty, lambda_0, lambda_maxT)
    #
    # >>> Logging <<< #
    logger = kwargs.get("logger", DEFAULT_PARA["logger"])
    if logger is not None:
        logger.info("Iter: {:d}".format(len(FOMHist)))
        logger.info(paras)
        logger.info("maxT = {:.5f}".format(maxT))
        logger.info("lambda_maxT = {:.1f}".format(lambda_maxT * 1e9))
        logger.info("FWHM_fit = {:.1f}".format(FWHM_fit * 1e9))
        logger.info("FOM = {:.5f}".format(FOM))
        logger.info("feature_size = {:.1f}".format(feature_size * 1e9))
    #
    transmissionHist.append((l, T))
    reflectionHist.append((l, R))
    parasHist.append(paras)
    FOMHist.append(FOM)
    featureHist.append(feature_size)
    lambda0Hist.append(lambda_maxT)
    FWHMHist.append(FWHM_fit)
    #
    if plot:
        fig_transmission.set_data(l, T)
        axs[0, 0].relim()
        axs[0, 0].autoscale_view()
        #
        fig_reflection.set_data(l, R)
        axs[0, 1].relim()
        axs[0, 1].autoscale_view()
        #
        fig_FOM_his.set_data(np.arange(len(FOMHist)), FOMHist)
        axs[0, 2].relim()
        axs[0, 2].autoscale_view()
        # twin axis to plot feature size
        fig_feature_his.set_data(
            np.arange(len(featureHist)), np.asarray(featureHist) * 1e9
        )
        axs[1, 0].relim()
        axs[1, 0].autoscale_view()
        #
        fig_lambda0_his.set_data(
            np.arange(len(lambda0Hist)), np.asarray(lambda0Hist) * 1e9
        )
        axs[1, 1].relim()
        axs[1, 1].autoscale_view()
        # twin axis to plot FWHM
        fig_FWHM_his.set_data(np.arange(len(FWHMHist)), np.asarray(FWHMHist) * 1e9)
        axs[1, 2].relim()
        axs[1, 2].autosc0ale_view()
        #
        fig.canvas.flush_events()
    #
    #
    return (
        -FOM + feature_size_penalty - cw_penalty
    )  # take care of the minus and plus sign!


def setup_source(fdtd, dimension="2D", simulation_typ: int = 0, **kwargs):
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    source_angle = kwargs.get("source_angle", DEFAULT_PARA["source_angle"])
    #
    # >>> set source span and wavelength <<< #
    if "gaussian" in SOURCE_typ:
        fdtd.setnamed("source", "center wavelength", lambda_0)
        fdtd.setnamed("source", "wavelength span", max(400e-9, FWHM * 3))
        fdtd.setnamed("source_wg", "center wavelength", lambda_0)
        fdtd.setnamed("source_wg", "wavelength span", max(400e-9, FWHM * 3))
        fdtd.setnamed("output_TE", "wavelength center", lambda_0)
        fdtd.setnamed("output_TE", "wavelength span", max(400e-9, FWHM * 3))
    else:
        raise ValueError("setup_source: Invalid SOURCE_typ: {:s}".format(SOURCE_typ))
    # >>> set gaussian source angle <<< #
    if dimension == "2D":
        fdtd.setnamed("FDTD", "dimension", dimension)
        fdtd.setnamed("source", "angle theta", -source_angle)
        fdtd.setnamed("source", "polarization angle", 90)  # TE mode
    elif dimension == "3D":
        fdtd.setnamed("FDTD", "dimension", dimension)
        fdtd.setnamed("FDTD", "z min bc", "Anti-Symmetric")
        fdtd.setnamed("source", "angle theta", -source_angle)
        fdtd.setnamed("source", "angle phi", -90)
        fdtd.setnamed("source", "polarization angle", 90)  # TE mode
        # because the definition of 2D source is different from 3D ver.
    # >>> set source type <<< #
    if simulation_typ == 0:  # forward
        fdtd.setnamed("source", "enabled", 1)
        fdtd.setnamed("source_wg", "enabled", 0)
    elif simulation_typ == 1:  # backward
        fdtd.setnamed("source", "enabled", 0)
        fdtd.setnamed("source_wg", "enabled", 1)
    else:
        raise ValueError(
            "setup_source: Invalid simulation_typ: {:d}".format(simulation_typ)
        )
    # >>> set monitor <<< #
    fdtd.setglobalmonitor(
        "frequency points", 300
    )  # setting the global frequency resolution


def setup_monitor(fdtd, monitor=False, movie=False, advanced_monitor=False):
    if monitor:
        fdtd.setnamed("index_monitor", "enabled", 1)
        fdtd.setnamed("field_monitor", "enabled", 1)
    else:
        fdtd.setnamed("index_monitor", "enabled", 0)
        fdtd.setnamed("field_monitor", "enabled", 0)
    #
    if movie:
        fdtd.setnamed("movie_monitor", "enabled", 1)
    else:
        fdtd.setnamed("movie_monitor", "enabled", 0)
    #
    if advanced_monitor:
        fdtd.setnamed("advanced_field_monitor", "enabled", 1)
    else:
        fdtd.setnamed("advanced_field_monitor", "enabled", 0)


def load_script(script_name):
    cwd = os.getcwd()
    with open(os.path.join(cwd, "script", script_name), "r") as f:
        script = f.read()
        return script


def setup_grating_structuregroup(fdtd, **kwargs):
    # adduserprop("property name", type, value);
    # type 0 - number, type 2 - Length, type 6 - matrix
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    start_radius = kwargs.get("start_radius", DEFAULT_PARA["start_radius"])
    taper_angle = kwargs.get("taper_angle", DEFAULT_PARA["taper_angle"])
    N = kwargs.get("N", DEFAULT_PARA["N"])
    #
    fdtd.addstructuregroup(name=grating_typ)
    fdtd.adduserprop("start_radius", 2, start_radius)
    fdtd.adduserprop("taper_angle", 0, taper_angle)
    fdtd.adduserprop("wg_h", 2, 220e-9)
    #
    if grating_typ in ["subw_grating", "subw_grating_sourcefixed"]:
        NL = kwargs.get("NL", DEFAULT_PARA["NL"])
        NH = kwargs.get("NH", DEFAULT_PARA["NH"])
        #
        fdtd.adduserprop("Lambda", 2, 1.1e-6)
        fdtd.adduserprop("ff", 0, 0.5)
        fdtd.adduserprop("ffL", 0, 0.2)
        fdtd.adduserprop("ffH", 0, 0.8)
        fdtd.adduserprop("NL", 0, NL)
        fdtd.adduserprop("NH", 0, NH)
        fdtd.adduserprop("N", 0, N)
        #
        fdtd.setnamed(
            grating_typ,
            "script",
            load_script("subw_grating_concentric.lsf"),
        )
    elif grating_typ == "apodized_subw_grating":
        NL = kwargs.get("NL", DEFAULT_PARA["NL"])
        NH = kwargs.get("NH", DEFAULT_PARA["NH"])
        #
        fdtd.adduserprop("Lambda_i", 2, 1.1e-6)
        fdtd.adduserprop("Lambda_f", 2, 1.1e-6)
        fdtd.adduserprop("ff_i", 0, 0.5)
        fdtd.adduserprop("ff_f", 0, 0.5)
        fdtd.adduserprop("ffL_i", 0, 0.2)
        fdtd.adduserprop("ffL_f", 0, 0.2)
        fdtd.adduserprop("ffH_i", 0, 0.8)
        fdtd.adduserprop("ffH_f", 0, 0.8)
        fdtd.adduserprop("NL", 0, NL)
        fdtd.adduserprop("NH", 0, NH)
        fdtd.adduserprop("N", 0, N)
        #
        fdtd.setnamed(
            grating_typ,
            "script",
            load_script("apodized_subw_grating_concentric.lsf"),
        )
    elif grating_typ == "inverse_grating":
        #
        fdtd.adduserprop("N", 0, N)
        fdtd.adduserprop("pitch_list", 6, np.array([0.5e-6] * N))
        fdtd.adduserprop("ff_list", 6, np.array([0.2] * N))
        #
        fdtd.setnamed(
            grating_typ, "script", load_script("inverse_grating_concentric.lsf")
        )
    elif grating_typ == "grating":
        #
        fdtd.adduserprop("N", 0, N)
        fdtd.adduserprop("Lambda", 2, 1.1e-6)
        fdtd.adduserprop("ff", 0, 0.5)
        #
        fdtd.setnamed(grating_typ, "script", load_script("grating_concentric.lsf"))
    elif grating_typ == "apodized_grating":
        #
        fdtd.adduserprop("N", 0, N)
        fdtd.adduserprop("Lambda_i", 2, 1.1e-6)
        fdtd.adduserprop("Lambda_f", 2, 1.1e-6)
        fdtd.adduserprop("ff_i", 0, 0.5)
        fdtd.adduserprop("ff_f", 0, 0.5)
        #
        fdtd.setnamed(
            grating_typ, "script", load_script("apodized_grating_concentric.lsf")
        )
    else:
        raise ValueError(
            "setup_grating_structuregroup: Invalid grating_typ: {:s}".format(
                grating_typ
            )
        )


def load_template(dataName, SOURCE_typ, purpose=""):
    import lumapi  # type: ignore

    # make a copy of the template file
    dest_fileName = "{:s}_{:s}_subw_{:s}.fsp".format(dataName, purpose, SOURCE_typ)
    shutil.copy("./subw_{:s}_template.fsp".format(SOURCE_typ), dest_fileName)
    return lumapi.FDTD(dest_fileName)


def convert_paras_init(para, kwargs, kwargs_init):
    from lib.grating.subwavelength import subw_grating, grating_to_pitch_ff

    #
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    grating_typ_init = kwargs_init.get("grating_typ", DEFAULT_PARA["grating_typ"])
    if grating_typ == "subw_grating":  # should only be converted from subw_grating
        if grating_typ_init == "subw_grating":
            return para
        else:
            raise ValueError(
                "convert_paras_init: Invalid grating_typ_init: {:s}".format(
                    grating_typ_init
                )
            )
    elif (
        grating_typ == "apodized_subw_grating"
    ):  # can be converted from subw_grating or apodized subw grating
        if grating_typ_init == "apodized_subw_grating":
            return para
        elif grating_typ_init == "subw_grating":
            Lambda_i = para[0]
            Lambda_f = para[0]
            ffL_i = para[1]
            ffL_f = para[1]
            ffH_i = para[2]
            ffH_f = para[2]
            ff_i = para[3]
            ff_f = para[3]
            fiberx = para[4]
            paras = np.array(
                [Lambda_i, Lambda_f, ffL_i, ffL_f, ffH_i, ffH_f, ff_i, ff_f, fiberx]
            )
            return paras
    elif (
        grating_typ == "inverse_grating"
    ):  # can be converted from subw_grating or inverse_grating
        if grating_typ_init == "subw_grating":
            fiberx = para[4]
            N = kwargs_init.get("N", DEFAULT_PARA["N"])
            NL = kwargs_init.get("NL", DEFAULT_PARA["NL"])
            NH = kwargs_init.get("NH", DEFAULT_PARA["NH"])
            grating = subw_grating(
                N=N,
                Lambda=para[0],
                ff=para[3],
                ffL=para[1],
                ffH=para[2],
                NL=NL,
                NH=NH,
            )
            pitch_list, ff_list = grating_to_pitch_ff(grating)
            paras = np.hstack((fiberx, pitch_list, ff_list))
            return paras
        elif grating_typ_init == "inverse_grating":
            return para
    elif grating_typ == "grating":  # can only be converted from grating
        if grating_typ_init == "grating":
            return para
        else:
            raise ValueError(
                "convert_paras_init: Invalid grating_typ_init: {:s}".format(
                    grating_typ_init
                )
            )
    elif (
        grating_typ == "apodized_grating"
    ):  # can be converted from grating or apodized_grating
        if grating_typ_init == "apodized_grating":
            return para
        elif grating_typ_init == "grating":
            Lambda_i = para[0]
            Lambda_f = para[0]
            ff_i = para[1]
            ff_f = para[1]
            fiberx = para[2]
            paras = np.array([Lambda_i, Lambda_f, ff_i, ff_f, fiberx])
            return paras
    else:
        raise ValueError(
            "convert_paras_init: Invalid grating_typ: {:s}".format(grating_typ)
        )


def get_paras_bound(**kwargs):
    grating_typ = kwargs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    N = kwargs.get("N", DEFAULT_PARA["N"])
    #
    if grating_typ == "subw_grating":  # [Lambda, ffL, ffH, ff, fiberx]
        NL = kwargs.get("NL", DEFAULT_PARA["NL"])
        if SOURCE_typ in ["gaussian_airclad"]:
            paras_min = np.array([0.7e-6, 0.05, 0.4, 0.3, 10e-6], dtype=np.float_)
            paras_max = np.array([1.1e-6, 0.4, 0.95, 0.7, 18e-6], dtype=np.float_)
        elif SOURCE_typ in [
            "gaussian_released",
            "gaussian_packaged",
            "gaussian_airclad",
        ]:
            if NL == 2:
                paras_min = np.array([1.1e-6, 0.00, 0.5, 0.3, 12e-6], dtype=np.float_)
                paras_max = np.array([1.7e-6, 0.32, 0.95, 0.7, 20e-6], dtype=np.float_)
            else:
                paras_min = np.array([0.4e-6, 0.00, 0.3, 0.2, 10e-6], dtype=np.float_)
                paras_max = np.array([1.3e-6, 0.5, 0.95, 0.8, 22e-6], dtype=np.float_)
        else:
            raise ValueError(
                "get_paras_bound: Invalid SOURCE_typ: {:s}".format(SOURCE_typ)
            )
    elif grating_typ == "subw_grating_sourcefixed":  # [Lambda, ffL, ffH, ff]
        paras_min = np.array([1.1e-6, 0.00, 0.5, 0.3], dtype=np.float_)
        paras_max = np.array([1.7e-6, 0.32, 0.95, 0.7], dtype=np.float_)
    elif (
        grating_typ == "apodized_subw_grating"
    ):  # [Lambda_i, Lambda_f, ffL_i, ffL_f, ffH_i, ffH_f, ff_i, ff_f, fiberx]
        paras_min = np.array(
            [1.1e-6, 1.1e-6, 0.00, 0.00, 0.5, 0.5, 0.3, 0.3, 12e-6], dtype=np.float_
        )
        paras_max = np.array(
            [1.7e-6, 1.7e-6, 0.32, 0.32, 0.95, 0.95, 0.7, 0.7, 20e-6], dtype=np.float_
        )
    elif grating_typ == "inverse_grating":  # [fiberx, pitch_list, ff_list]
        paras_min = np.array([10e-6] + [200e-9] * N + [0.05] * N, dtype=np.float_)
        paras_max = np.array([25e-6] + [1.1e-6] * N + [0.95] * N, dtype=np.float_)
    elif grating_typ == "grating":  # [Lambda, ff, fiberx]
        lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
        dLambda = 0.55e-6 * (lambda_0 - 1326e-9) / (1326e-9)
        paras_min = np.array([0.2e-6 + dLambda, 0.6, 13e-6], dtype=np.float_)
        paras_max = np.array([0.9e-6 + dLambda, 1.0, 20e-6], dtype=np.float_)
    elif grating_typ == "apodized_grating":  # [Lambda_i, Lambda_f, ff_i, ff_f, fiberx]
        paras_min = np.array([0.8e-6, 0.8e-6, 0.0, 0.0, 12e-6], dtype=np.float_)
        paras_max = np.array([1.6e-6, 1.6e-6, 0.5, 0.5, 20e-6], dtype=np.float_)
    else:
        raise ValueError(
            "get_paras_bound: Invalid grating_typ: {:s}".format(grating_typ)
        )
    #
    return paras_min, paras_max


def run_optimize(dataName, **kwargs):
    transmissionHist = []
    reflectionHist = []
    parasHist = []
    FOMHist = []
    featureHist = []
    lambda0Hist = []
    FWHMHist = []
    #
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    maxiter = kwargs.get("maxiter", DEFAULT_PARA["maxiter"])
    # >>> parameter bounds <<< #
    paras_min, paras_max = get_paras_bound(**kwargs)
    # >>> paras_init <<< #
    paras_init = kwargs.get("paras_init", DEFAULT_PARA["paras_init"])
    if paras_init is not None:  # initialize the paras
        if isinstance(paras_init, str):  # uuid
            para = load_paras(paras_init)
            kwargs_init = load_json(paras_init)
            paras = convert_paras_init(para, kwargs, kwargs_init)
        elif isinstance(paras_init, list) or isinstance(paras_init, np.ndarray):
            paras = np.asarray(paras_init)
        else:
            raise ValueError(
                "run_optimize: Invalid paras_init: {:s}".format(paras_init)
            )
    else:  # no initialization
        # paras = np.random.uniform(paras_min, paras_max)
        paras = (paras_min + paras_max) / 2
        # add random noise
        # paras = paras * np.random.uniform(0.8, 1.2, len(paras))
    #
    paras_bounds = opt.Bounds(paras_min, paras_max)  # type: ignore
    # plot setup
    plt.ion()
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))
    fig.subplots_adjust(wspace=0.3, hspace=0.3)
    (fig_transmission,) = axs[0, 0].plot([], [])
    axs[0, 0].set_title("Transmission")
    (fig_reflection,) = axs[0, 1].plot([], [])
    axs[0, 1].set_title("Reflection")
    (fig_FOM_his,) = axs[0, 2].plot([], [])
    axs[0, 2].set_title("FOM")
    (fig_feature_his,) = axs[1, 0].plot([], [])
    axs[1, 0].set_title("Feature size")
    (fig_lambda0_his,) = axs[1, 1].plot([], [])
    axs[1, 1].set_title("lambda0")
    (fig_FWHM_his,) = axs[1, 2].plot([], [])
    axs[1, 2].set_title("FWHM")
    #
    with load_template(dataName, SOURCE_typ, purpose="scan") as fdtd:
        kwargs1 = {
            **kwargs,
            #
            "transmissionHist": transmissionHist,
            "reflectionHist": reflectionHist,
            "parasHist": parasHist,
            "FOMHist": FOMHist,
            "featureHist": featureHist,
            "lambda0Hist": lambda0Hist,
            "FWHMHist": FWHMHist,
            #
            "fig": fig,
            "axs": axs,
            "fig_transmission": fig_transmission,
            "fig_reflection": fig_reflection,
            "fig_FOM_his": fig_FOM_his,
            "fig_feature_his": fig_feature_his,
            "fig_lambda0_his": fig_lambda0_his,
            "fig_FWHM_his": fig_FWHM_his,
            #
        }
        # >>> setting up simulation <<< #
        setup_monitor(fdtd, monitor=False, movie=False)
        setup_grating_structuregroup(fdtd, **kwargs)
        #
        paras = opt.minimize(
            lambda para: optimize_wrapper(fdtd, para, plot=True, **kwargs1),
            paras,
            method="Nelder-Mead",
            bounds=paras_bounds,
            options={"disp": True, "maxiter": maxiter, "adaptive": True},
        )
    #
    logger = kwargs.get("logger", DEFAULT_PARA["logger"])
    logger.info("Final Parameter: ")
    logger.info(paras.x)
    # >>> savedata, using try-catch to avoid error <<< #
    try:
        l, T = transmissionHist[-1]
        a = np.transpose(np.vstack((l * 1e6, T)))  # wavelength in um
        np.savetxt(
            "{:s}_transmission.txt".format(dataName), a
        )  # using lambda,T on each row to save the transmission data
    except Exception as e:
        logger.error(e)
    try:
        l, R = reflectionHist[-1]
        a = np.transpose(np.vstack((l * 1e6, R)))  # wavelength in um
        np.savetxt(
            "{:s}_reflection.txt".format(dataName), a
        )  # using lambda,R on each row to save the transmission data
    except Exception as e:
        logger.error(e)
    try:
        np.savetxt("{:s}_paras.txt".format(dataName), paras.x)
    except Exception as e:
        logger.error(e)
    try:
        np.savetxt("{:s}_parasHist.txt".format(dataName), parasHist)
    except Exception as e:
        logger.error(e)
    try:
        np.savetxt("{:s}_FOMHist.txt".format(dataName), FOMHist)
    except Exception as e:
        logger.error(e)
    try:
        np.savetxt("{:s}_featureHist.txt".format(dataName), featureHist)
    except Exception as e:
        logger.error(e)
    plt.ioff()
    return transmissionHist, parasHist, FOMHist, featureHist, lambda0Hist, FWHMHist


def plot_result(transmission, FOMHist, featureHist, lambda0Hist, FWHMHist, dataName):
    fig = plt.figure(figsize=(14, 6))
    grid = GridSpec(1, 3, width_ratios=[2, 1, 1])
    ax0 = plt.subplot(grid[0])
    ax1 = plt.subplot(grid[1])
    ax2 = plt.subplot(grid[2])
    #
    fig.subplots_adjust(wspace=0.35)
    # plot the final transmission
    l, T = transmission
    arb_fit_1d(ax0, l * 1e9, T, "2D")
    # ax0.plot(l * 1e9, T)
    # ax0.scatter(l * 1e9, T, marker="+", alpha=0.4)
    # ax0.set_xlabel(r"$\lambda$(nm)")
    # ax0.set_ylabel(r"T($\lambda$)")
    # ax0.set_title("Transmission_lambda")
    #
    # plot the FOM history
    ax1.plot(np.asarray(FOMHist), color="blue", alpha=0.5, label="FOM")
    ax1.set_xlabel("Iteration num")
    ax1.set_ylabel("Figure of merit(FOM)")
    ax1.set_title("FOM_feature_iter")
    ax1.legend(loc="upper right")
    # add double y axis to record feature size
    ax1_2 = ax1.twinx()
    ax1_2.plot(
        np.asarray(featureHist) * 1e9, color="orange", alpha=0.5, label="feature size"
    )
    ax1_2.set_ylabel("Feature size(nm)")
    ax1_2.legend(loc="lower right")
    #
    # plot lambda0 history
    ax2.plot(np.asarray(lambda0Hist) * 1e9, color="blue", alpha=0.5, label="lambda0")
    ax2.set_xlabel("Iteration num")
    ax2.set_ylabel("lambda0(nm)")
    ax2.set_title("lambda0_FWHM_iter")
    ax2.legend(loc="upper right")
    # add double y axis to record FWHM
    ax2_2 = ax2.twinx()
    ax2_2.plot(np.asarray(FWHMHist) * 1e9, color="orange", alpha=0.5, label="FWHM")
    ax2_2.set_ylabel("FWHM(nm)")
    ax2_2.legend(loc="lower right")
    #
    plt.savefig("{:s}_result.png".format(dataName), dpi=200, bbox_inches="tight")
    #


def load_work(uuid, logger):
    # get uuid for remaining params based on MD5
    kwargs = load_json(uuid)
    kwargs["logger"] = logger
    dataName = getdataName(uuid)

    # >>> start working <<<
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    logger.info("Start loading work: {:s}".format(dataName))
    logger.info("lambda_0 = {:.1f} nm".format(lambda_0 * 1e9))
    logger.info("FWHM = {:.1f} nm".format(FWHM * 1e9))

    # log kwargs
    for key, value in kwargs.items():
        if key in DEFAULT_PARA.keys():
            if key not in ["lambda_0", "FWHM"]:
                logger.info("{:s} = {:s}".format(key, str(value)))
        else:
            logger.warning("Unknown key: {:s}".format(key))
    #
    (
        transmissionHist,
        parasHist,
        FOMHist,
        featureHist,
        lambda0Hist,
        FWHMHist,
    ) = run_optimize(dataName, **kwargs)
    plot_result(
        transmissionHist[-1], FOMHist, featureHist, lambda0Hist, FWHMHist, dataName
    )
    #
    logger.info("Work done: {:s}".format(dataName))
