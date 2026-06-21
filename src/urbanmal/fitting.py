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


def _linear_func(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a + b * x


def _exp_func(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * np.exp(-b * x)


def _power_func(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * np.power(x, b)


def _aic_bic(y: np.ndarray, y_pred: np.ndarray, n_params: int) -> dict:
    n = len(y)
    rss = np.sum((y - y_pred) ** 2)
    rss = max(rss, 1e-12)
    log_lik = -n / 2 * (np.log(2 * np.pi) + np.log(rss / n) + 1)
    aic = 2 * n_params - 2 * log_lik
    bic = n_params * np.log(n) - 2 * log_lik
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - rss / ss_tot if ss_tot > 0 else float("nan")
    return {"aic": aic, "bic": bic, "r2": r2, "n_params": n_params}


def compare_functional_forms(x: np.ndarray, y: np.ndarray) -> pd.DataFrame:
    """
    Porovná čtyři funkční formy vztahu konstrukt~konstituent přes AIC/BIC:
    lineární, exponenciální pokles, mocninná funkce, plná Altmannova funkce.

    Nižší AIC/BIC = lepší fit (s penalizací za počet parametrů). Toto je
    nezbytný krok pro robustní potvrzení MA zákona -- samotný hezký fit
    mocninné funkce nestačí, je třeba ukázat, že fituje lépe než alternativy
    (analogie k požadavkům na testování power-law distribucí, viz Clauset et al. 2009).
    """
    rows = []

    try:
        popt, _ = curve_fit(_linear_func, x, y, maxfev=10_000)
        stats = _aic_bic(y, _linear_func(x, *popt), n_params=2)
        rows.append({"model": "linear", **stats})
    except Exception:
        rows.append({"model": "linear", "aic": None, "bic": None, "r2": None, "n_params": 2})

    try:
        popt, _ = curve_fit(_exp_func, x, y, p0=[1.0, 0.001], maxfev=10_000)
        stats = _aic_bic(y, _exp_func(x, *popt), n_params=2)
        rows.append({"model": "exponential", **stats})
    except Exception:
        rows.append({"model": "exponential", "aic": None, "bic": None, "r2": None, "n_params": 2})

    try:
        popt, _ = curve_fit(_power_func, x, y, p0=[1.0, -0.3], maxfev=10_000)
        stats = _aic_bic(y, _power_func(x, *popt), n_params=2)
        rows.append({"model": "power", **stats})
    except Exception:
        rows.append({"model": "power", "aic": None, "bic": None, "r2": None, "n_params": 2})

    try:
        popt, _ = curve_fit(altmann_func, x, y, p0=[1.0, -0.3, 0.0], maxfev=10_000)
        stats = _aic_bic(y, altmann_func(x, *popt), n_params=3)
        rows.append({"model": "altmann", **stats})
    except Exception:
        rows.append({"model": "altmann", "aic": None, "bic": None, "r2": None, "n_params": 3})

    df = pd.DataFrame(rows)
    df["delta_aic"] = df["aic"] - df["aic"].min()
    return df.sort_values("aic").reset_index(drop=True)
