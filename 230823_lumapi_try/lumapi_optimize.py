import sys, os
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
import shutil
from matplotlib.gridspec import GridSpec

sys.path.append("..")
from lib.gaussian.gaussian_fit_1d import arb_fit_1d
from json_uuid import load_json, uuid_to_wd, load_paras, getdataName


def add_lumerical_path():
    # add lumerical api path
    pathList = [
        "C:\\Program Files\\Lumerical\\v221\\api\\python\\",
        "C:\\Program Files\\Lumerical\\FDTD\\api\\python\\",
        "D:\\software\\Lumerical\\Lumerical\\v221\\api\\python",
    ]
    for pathName in pathList:
        if os.path.exists(pathName):
            sys.path.append(pathName)
            break
    sys.path.append(os.path.dirname(__file__))  # Current directory


add_lumerical_path()

from const_var import DEFAULT_PARA


def process_data(fdtd, SOURCE_typ):
    if SOURCE_typ in ["gaussian_released", "gaussian_packaged"]:
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


def analysis_FOM(l, T, **kwargs):
    # >>> useful functions <<< #
    def _find(l, val):
        # return the index of most close value in l
        # uni-directional, l must be sorted
        idx = np.abs(np.asarray(l) - val).argmin()
        return idx

    def _gaussian_curve(l, lambda_0, FWHM):
        sigma = FWHM / 1.6651092223153954
        return np.exp(-((l - lambda_0) ** 2) / (sigma**2))

    def _T_0(l, lambda_0, T):
        index_center = _find(l, lambda_0)
        T_0 = T[index_center]
        return T_0

    def _T_max(l, T):
        return np.max(T), l[np.argmax(T)]

    def _data_crop(l, T, lambda_0, width):
        """get data from lambda_0-width/2 to lambda_0+width/2"""
        assert width > 0, "width must be positive"
        index_leftmost = _find(l, lambda_0 - width / 2)
        index_rightmost = _find(l, lambda_0 + width / 2)
        l_crop = l[index_leftmost : index_rightmost + 1]
        T_crop = T[index_leftmost : index_rightmost + 1]
        return l_crop, T_crop

    def _cross_correlation(f, g):
        assert len(f) == len(g), "f and g must have the same length"
        return np.sum(np.asarray(f) * np.asarray(g))

    def _sum_alpha(f, alpha=1):
        return np.sum(np.power(f, alpha))

    def _mean_alpha(f, alpha=1):
        return np.power(np.mean(np.power(f, alpha)), 1 / alpha)

    def _norm_cross_correlation(f, g):
        cc = _cross_correlation(f, g)
        norm_f = np.sqrt(_sum_alpha(f, 2))
        norm_g = np.sqrt(_sum_alpha(g, 2))
        return cc / (norm_f * norm_g)

    def _mean_CE(f):
        return np.mean(10 * np.log10(np.asarray(f)))

    # >>> load paras <<< #
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwargs.get("FWHM", DEFAULT_PARA["FWHM"])
    alpha = kwargs.get("alpha", DEFAULT_PARA["alpha"])
    FOM_typ = kwargs.get("FOM_typ", DEFAULT_PARA["FOM_typ"])

    # >>> analysis <<< #
    l_c, T_c = _data_crop(l, T, lambda_0, FWHM * 3)
    T_des = _gaussian_curve(l_c, lambda_0, FWHM)
    cross_correlation = _cross_correlation(T_c, T_des)
    norm_cross_correlation = _norm_cross_correlation(T_c, T_des)
    # maxT, lambda_maxT = _T_max(l, T)
    maxT, lambda_maxT, FWHM_fit, CE = arb_fit_1d(False, l, T, "")  # type: ignore
    norm_T = _mean_alpha(T_c, 2)

    # >>> FOM <<< #
    if FOM_typ == "square":
        # print("square")
        print(norm_T, norm_cross_correlation)
        FOM = float((norm_T + alpha) * norm_cross_correlation)
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
        T_0 = _T_0(l, lambda_0, T)
        FOM = T_0
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
    elif grating_typ == "inverse_grating":
        fiberx = paras[0]
        pitch_list = paras[1 : 1 + N]
        fdtd.setnamed(grating_typ, "pitch_list", pitch_list)
        ff_list = paras[1 + N : 1 + 2 * N]
        fdtd.setnamed(grating_typ, "ff_list", ff_list)
    #

    if SOURCE_typ in ["gaussian_released", "gaussian_packaged"]:
        fdtd.setnamed("source", "x", fiberx)  # type: ignore
    elif SOURCE_typ == "fiber":
        fdtd.setnamed("fiber", "x", fiberx)  # type: ignore


def calc_min_feature(paras, NL, NH) -> float:
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
    return min(min_L, min_H)


def fdtd_iter(fdtd, paras, **kwargs):
    """l, T, maxT, FOM=fdtd_iter(fdtd, paras, **kwargs)"""
    #
    SOURCE_typ = kwargs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    #
    fdtd.switchtolayout()
    set_params(fdtd, paras, **kwargs)
    fdtd.run()
    l, T = process_data(fdtd, SOURCE_typ)
    #
    maxT, lambda_maxT, FWHM_fit, FOM = analysis_FOM(l, T, **kwargs)
    #
    return l, T, maxT, lambda_maxT, FWHM_fit, FOM


def optimize_wrapper(fdtd, paras, **kwargs):
    fig = kwargs.get("fig", None)
    axs = kwargs.get("axs", None)
    fig_transmission = kwargs.get("fig_transmission", None)
    fig_FOM_his = kwargs.get("fig_FOM_his", None)
    fig_feature_his = kwargs.get("fig_feature_his", None)
    fig_lambda0_his = kwargs.get("fig_lambda0_his", None)
    fig_FWHM_his = kwargs.get("fig_FWHM_his", None)
    plot = kwargs.get("plot", False)
    # >>> History <<< #
    transmissionHist = kwargs.get("transmissionHist", [])
    parasHist = kwargs.get("parasHist", [])
    FOMHist = kwargs.get("FOMHist", [])
    featureHist = kwargs.get("featureHist", [])
    lambda0Hist = kwargs.get("lambda0Hist", [])
    FWHMHist = kwargs.get("FWHMHist", [])
    # >>> Analyse <<< #
    l, T, maxT, lambda_maxT, FWHM_fit, FOM = fdtd_iter(fdtd, paras, **kwargs)
    #
    # >>> Figure of merit <<< #
    # Feature size penalty
    NL = kwargs.get("NL", DEFAULT_PARA["NL"])
    NH = kwargs.get("NH", DEFAULT_PARA["NH"])
    feature_size = calc_min_feature(paras, NL, NH)
    MIN_FEATURE_SIZE = kwargs.get("MIN_FEATURE_SIZE", DEFAULT_PARA["MIN_FEATURE_SIZE"])
    feature_size_penalty = (
        0.3
        * int(feature_size < MIN_FEATURE_SIZE)
        * (MIN_FEATURE_SIZE - feature_size)
        / MIN_FEATURE_SIZE
    )
    # Center wavelength penalty
    penalty = kwargs.get("penalty", DEFAULT_PARA["penalty"])
    lambda_0 = kwargs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    cw_penalty = 0
    for p_coeff, lambda_range in penalty:
        cw_penalty += (
            p_coeff * lambda_range / (lambda_range + np.abs(lambda_0 - lambda_maxT))
        )
    print("penalty: ", cw_penalty)
    #
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
        fig_FOM_his.set_data(np.arange(len(FOMHist)), FOMHist)
        axs[0, 1].relim()
        axs[0, 1].autoscale_view()
        # twin axis to plot feature size
        fig_feature_his.set_data(
            np.arange(len(featureHist)), np.asarray(featureHist) * 1e9
        )
        axs[0, 2].relim()
        axs[0, 2].autoscale_view()
        #
        fig_lambda0_his.set_data(
            np.arange(len(lambda0Hist)), np.asarray(lambda0Hist) * 1e9
        )
        axs[1, 0].relim()
        axs[1, 0].autoscale_view()
        # twin axis to plot FWHM
        fig_FWHM_his.set_data(np.arange(len(FWHMHist)), np.asarray(FWHMHist) * 1e9)
        axs[1, 1].relim()
        axs[1, 1].autoscale_view()
        #
        fig.canvas.flush_events()
    #
    #
    return (
        -FOM + feature_size_penalty - cw_penalty
    )  # take care of the minus and plus sign!


def setup_source(fdtd, lambda_0, FWHM, SOURCE_typ, dimension="2D"):
    # set source
    if SOURCE_typ in ["gaussian_released", "gaussian_packaged"]:
        fdtd.setnamed("source", "center wavelength", lambda_0)
        fdtd.setnamed("source", "wavelength span", max(400e-9, FWHM * 3))
        fdtd.setnamed("output_TE", "wavelength center", lambda_0)
        fdtd.setnamed("output_TE", "wavelength span", max(400e-9, FWHM * 3))
    elif SOURCE_typ == "fiber":
        fdtd.setglobalsource("center wavelength", lambda_0)
        fdtd.setglobalsource("wavelength span", max(400e-9, FWHM * 3))
    # set monitor
    fdtd.setglobalmonitor(
        "frequency points", 300
    )  # setting the global frequency resolution
    # set dimension of fdtd
    if dimension == "2D":
        fdtd.setnamed("FDTD", "dimension", dimension)
        fdtd.setnamed("source", "angle theta", -10)
        fdtd.setnamed("source", "polarization angle", 90)  # TE mode
    elif dimension == "3D":
        fdtd.setnamed("FDTD", "dimension", dimension)
        fdtd.setnamed("FDTD", "z min bc", "Anti-Symmetric")
        fdtd.setnamed("source", "angle theta", -10)
        fdtd.setnamed("source", "angle phi", -90)
        fdtd.setnamed("source", "polarization angle", 90)  # TE mode
        # because the definition of 2D source is different from 3D ver.


def setup_monitor(fdtd, monitor=False, movie=False):
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


def load_script(script_name):
    cwd = os.getcwd()
    with open(os.path.join(cwd, "script", script_name), "r") as f:
        script = f.read()
        return script


def setup_grating_structuregroup(fdtd, grating_typ, **kwargs):
    # adduserprop("property name", type, value);
    # type 0 - number, type 2 - Length, type 6 - matrix
    start_radius = kwargs.get("start_radius", DEFAULT_PARA["start_radius"])
    taper_angle = kwargs.get("taper_angle", DEFAULT_PARA["taper_angle"])
    N = kwargs.get("N", DEFAULT_PARA["N"])
    #
    fdtd.addstructuregroup(name=grating_typ)
    fdtd.adduserprop("start_radius", 2, start_radius)
    fdtd.adduserprop("taper_angle", 0, taper_angle)
    fdtd.adduserprop("wg_h", 2, 220e-9)
    #
    if grating_typ == "subw_grating":
        #
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
            "subw_grating", "script", load_script("subw_grating_concentric.lsf")
        )
    elif grating_typ == "inverse_grating":
        #
        fdtd.adduserprop("N", 0, N)
        fdtd.adduserprop("pitch_list", 6, np.array([0.5e-6] * N))
        fdtd.adduserprop("ff_list", 6, np.array([0.2] * 6))
        #
        fdtd.setnamed(
            "inverse_grating", "script", load_script("inverse_grating_concentric.lsf")
        )


def load_template(dataName, SOURCE_typ, purpose=""):
    import lumapi  # type: ignore

    # make a copy of the template file
    dest_fileName = "{:s}_{:s}_subw_{:s}.fsp".format(dataName, purpose, SOURCE_typ)
    shutil.copy("./subw_{:s}_template.fsp".format(SOURCE_typ), dest_fileName)
    return lumapi.FDTD(dest_fileName)


def run_optimize(dataName, **kwagrs):
    transmissionHist = []
    parasHist = []
    FOMHist = []
    featureHist = []
    lambda0Hist = []
    FWHMHist = []
    #
    SOURCE_typ = kwagrs.get("SOURCE_typ", DEFAULT_PARA["SOURCE_typ"])
    lambda_0 = kwagrs.get("lambda_0", DEFAULT_PARA["lambda_0"])
    FWHM = kwagrs.get("FWHM", DEFAULT_PARA["FWHM"])
    maxiter = kwagrs.get("maxiter", DEFAULT_PARA["maxiter"])
    grating_typ = kwagrs.get("grating_typ", DEFAULT_PARA["grating_typ"])
    N = kwagrs.get("N", DEFAULT_PARA["N"])
    NL = kwagrs.get("NL", DEFAULT_PARA["NL"])
    NH = kwagrs.get("NH", DEFAULT_PARA["NH"])
    # >>> parameter bounds <<< #
    if grating_typ == "subw_grating":
        if SOURCE_typ == "gaussian_packaged":
            paras_min = np.array([0.7e-6, 0.05, 0.4, 0.3, 10e-6], dtype=np.float_)
            paras_max = np.array([1.1e-6, 0.4, 0.95, 0.7, 18e-6], dtype=np.float_)
        elif SOURCE_typ == "gaussian_released":
            if NL == 2 and NH == 2:
                paras_min = np.array([1.1e-6, 0.00, 0.5, 0.3, 12e-6], dtype=np.float_)
                paras_max = np.array([1.7e-6, 0.32, 0.95, 0.7, 20e-6], dtype=np.float_)
            else:
                paras_min = np.array([0.6e-6, 0.00, 0.3, 0.2, 10e-6], dtype=np.float_)
                paras_max = np.array([1.5e-6, 0.5, 0.95, 0.8, 22e-6], dtype=np.float_)
        elif SOURCE_typ == "fiber":
            paras_min = np.array([0.7e-6, 0.1, 0.3, 0.3, 12e-6], dtype=np.float_)
            paras_max = np.array([1.0e-6, 0.4, 0.8, 0.6, 18e-6], dtype=np.float_)
        else:
            raise ValueError("Invalid SOURCE_typ: {:s}".format(SOURCE_typ))
    elif grating_typ == "inverse_grating":
        paras_min = np.array([10e-6] + [100e-9] * N + [0.1] * N, dtype=np.float_)
        paras_max = np.array([20e-6] + [1.5e-6] * N + [0.9] * N, dtype=np.float_)
    else:
        raise ValueError("Invalid grating_typ: {:s}".format(grating_typ))
    # >>> paras_init <<< #
    paras_init = kwagrs.get("paras_init", DEFAULT_PARA["paras_init"])
    if paras_init is not None:
        if isinstance(paras_init, str):  # uuid
            if grating_typ == "subw_grating":
                paras = load_paras(paras_init)
            else:
                para = load_paras(paras_init)
                fiberx = para[4]
                from lib.grating.subwavelength import subw_grating, grating_to_pitch_ff

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
                print(paras.shape)
        else:  # np.ndarray
            paras = paras_init
    else:
        # paras = np.random.uniform(paras_min, paras_max)
        paras = (paras_min + paras_max) / 2
    #
    paras_bounds = opt.Bounds(paras_min, paras_max)  # type: ignore
    # plot setup
    plt.ion()
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))
    fig.subplots_adjust(wspace=0.3, hspace=0.3)
    (fig_transmission,) = axs[0, 0].plot([], [])
    axs[0, 0].set_title("Transmission")
    (fig_FOM_his,) = axs[0, 1].plot([], [])
    axs[0, 1].set_title("FOM")
    (fig_feature_his,) = axs[0, 2].plot([], [])
    axs[0, 2].set_title("Feature size")
    (fig_lambda0_his,) = axs[1, 0].plot([], [])
    axs[1, 0].set_title("lambda0")
    (fig_FWHM_his,) = axs[1, 1].plot([], [])
    axs[1, 1].set_title("FWHM")
    #
    with load_template(dataName, SOURCE_typ, purpose="scan") as fdtd:
        kwargs1 = {
            "plot": True,
            #
            "transmissionHist": transmissionHist,
            "parasHist": parasHist,
            "FOMHist": FOMHist,
            "featureHist": featureHist,
            "lambda0Hist": lambda0Hist,
            "FWHMHist": FWHMHist,
            #
            "fig": fig,
            "axs": axs,
            "fig_transmission": fig_transmission,
            "fig_FOM_his": fig_FOM_his,
            "fig_feature_his": fig_feature_his,
            "fig_lambda0_his": fig_lambda0_his,
            "fig_FWHM_his": fig_FWHM_his,
            #
            **kwagrs,
        }
        # >>> setting up simulation <<< #
        grating_typ = kwagrs.get("grating_typ", DEFAULT_PARA["grating_typ"])
        setup_source(fdtd, lambda_0, FWHM, SOURCE_typ, dimension="2D")
        setup_monitor(fdtd, monitor=False, movie=False)
        setup_grating_structuregroup(fdtd, grating_typ)
        #
        paras = opt.minimize(
            lambda para: optimize_wrapper(fdtd, para, **kwargs1),
            paras,
            method="Nelder-Mead",
            bounds=paras_bounds,
            options={"disp": True, "maxiter": maxiter, "adaptive": True},
        )

    #
    logger = kwagrs.get("logger", DEFAULT_PARA["logger"])
    logger.info("Final Parameter: ")
    logger.info(paras.x)
    # savedata
    try:
        l, T = transmissionHist[-1]
        a = np.transpose(np.vstack((l * 1e6, T)))  # wavelength in um
        np.savetxt(
            "{:s}_transmission.txt".format(dataName), a
        )  # using lambda,T on each row to save the transmission data
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


# def getdataName_DEPRECATED(uid, lambda_0, FWHM, alpha, penalty, SOURCE_typ, setup=True):
#     #
#     dataName = "{:03d}_{:.1f}_bw={:.1f}_alpha={:.3f}_penalty=({:.3f},{:d})_{:s}".format(
#         uid,
#         lambda_0 * 1e9,
#         FWHM * 1e9,
#         alpha,
#         penalty[0],
#         round(penalty[1] * 1e9),
#         SOURCE_typ,
#     )
#     # make dir named uid at current cwd
#     try:
#         cwd = os.getcwd()
#         if (not os.path.exists(os.path.join(cwd, "{:03d}".format(uid)))) and setup:
#             os.mkdir(os.path.join(cwd, "{:03d}".format(uid)))
#         print("Current working directory: {:s}".format(cwd))
#         path_dataName = os.path.join(cwd, "{:03d}".format(uid), dataName)
#         return path_dataName
#     except Exception as e:
#         print(e)
#         return dataName
#     #


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


if __name__ == "__main__":
    lambda_0 = 1.326e-6
    FWHM = 0.3e-6
    alpha = 0.02
    penalty = (0.03, 40e-9)
    SOURCE_typ = "gaussian_released"
    #
