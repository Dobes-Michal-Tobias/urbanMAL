import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import pearsonr


def altmann_func(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Altmannova funkce: y = a * x^b * e^(-c*x)."""
    return a * np.power(x, b) * np.exp(-c * x)


def fit_altmann(x: np.ndarray, y: np.ndarray) -> dict:
    """
    Fituje Altmannovu funkci na data metodou nelineárních nejmenších čtverců.

    Vrací slovník s koeficienty a, b, c a jejich standardními chybami.
    """
    p0 = [1.0, -0.3, 0.0]
    popt, pcov = curve_fit(altmann_func, x, y, p0=p0, maxfev=10_000)
    perr = np.sqrt(np.diag(pcov))
    y_pred = altmann_func(x, *popt)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {
        "a": popt[0], "a_se": perr[0],
        "b": popt[1], "b_se": perr[1],
        "c": popt[2], "c_se": perr[2],
        "r2": r2,
        "n": len(x),
    }


def fit_loglog(x: np.ndarray, y: np.ndarray) -> dict:
    """
    Jednoduchý log-log OLS fit: log(y) = log(a) + b*log(x).

    Ignoruje korekční faktor e^(-cx), ale je robustnější pro průzkumnou analýzu.
    """
    log_x = np.log(x)
    log_y = np.log(y)
    b, log_a = np.polyfit(log_x, log_y, 1)
    a = np.exp(log_a)
    r, p = pearsonr(log_x, log_y)
    return {
        "a": a,
        "b": b,
        "r2": r ** 2,
        "pearson_r": r,
        "p_value": p,
        "n": len(x),
    }
