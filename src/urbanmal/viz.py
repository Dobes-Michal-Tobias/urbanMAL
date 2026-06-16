import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Callable

# -- Palety ------------------------------------------------------------------

palette_seq = sns.color_palette("flare", as_cmap=False)    # sekvenční: metriky na spojité škále
palette_cat = sns.color_palette("Set2")                     # kategorická: typy sídel, fáze analýzy

SETTLEMENT_COLORS = {
    "obec": palette_cat[0],
    "mestys": palette_cat[1],
    "mesto": palette_cat[2],
    "statutarni_mesto": palette_cat[3],
}

# -- Globální styl -----------------------------------------------------------

def set_style() -> None:
    """Nastaví jednotný styl pro všechny grafy projektu."""
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.1)
    plt.rcParams.update({
        "figure.dpi": 120,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

# -- Distribuční grafy -------------------------------------------------------

def plot_segment_distribution(lengths, city_name: str, ax=None):
    """Histogram délek uličních segmentů pro jedno město."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(lengths, bins=50, color=palette_seq[3], ax=ax)
    ax.axvline(lengths.mean(), color="crimson", linestyle="--", label=f"průměr {lengths.mean():.0f} m")
    ax.axvline(lengths.median(), color="steelblue", linestyle=":", label=f"medián {lengths.median():.0f} m")
    ax.set_xlabel("Délka segmentu (m)")
    ax.set_ylabel("Počet segmentů")
    ax.set_title(f"Distribuce délek segmentů – {city_name}")
    ax.legend()
    return ax

# -- MA zákon: scatter + fit -------------------------------------------------

def plot_ma_fit(
    x, y,
    fit_func: Callable | None = None,
    fit_params: dict | None = None,
    x_label: str = "Velikost konstruktu",
    y_label: str = "Průměrná velikost konstituentu",
    title: str = "Menzerath-Altmannův zákon",
    hue=None,
    hue_label: str = "typ_sidla",
    ax=None,
):
    """
    Scatter plot závislosti konstituent ~ konstrukt s volitelnou fit křivkou.

    fit_func: funkce f(x, *params) — typicky altmann_func nebo mocninná funkce
    fit_params: slovník {'a': ..., 'b': ..., 'c': ...} z fitting.py
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 5))

    scatter_kw = dict(alpha=0.7, edgecolors="white", linewidths=0.4, s=60)

    if hue is not None:
        for label, color in SETTLEMENT_COLORS.items():
            mask = hue == label
            if mask.any():
                ax.scatter(x[mask], y[mask], color=color, label=label, **scatter_kw)
        ax.legend(title=hue_label, frameon=False)
    else:
        ax.scatter(x, y, color=palette_seq[3], **scatter_kw)

    if fit_func is not None and fit_params is not None:
        x_line = np.linspace(x.min(), x.max(), 500)
        a, b, c = fit_params.get("a"), fit_params.get("b"), fit_params.get("c", 0.0)
        y_line = fit_func(x_line, a, b, c)
        r2 = fit_params.get("r2", float("nan"))
        ax.plot(x_line, y_line, color="crimson", linewidth=2, label=f"fit  R²={r2:.3f}")
        ax.legend(frameon=False)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    return ax


def plot_ma_fit_loglog(x, y, fit_params: dict | None = None, title: str = "MA zákon (log–log)", ax=None):
    """Jako plot_ma_fit, ale obě osy jsou logaritmické."""
    ax = plot_ma_fit(x, y, title=title, ax=ax)
    ax.set_xscale("log")
    ax.set_yscale("log")
    if fit_params:
        a, b = fit_params.get("a"), fit_params.get("b")
        x_line = np.geomspace(x.min(), x.max(), 500)
        y_line = a * x_line ** b
        r2 = fit_params.get("r2", float("nan"))
        ax.plot(x_line, y_line, color="crimson", linewidth=2, label=f"log-log fit  R²={r2:.3f}")
        ax.legend(frameon=False)
    return ax
