from importlib import import_module
from importlib.util import find_spec
from pathlib import Path


FALLBACK_STYLE_NAME = "matplotlib-default"
SCIENCE_STYLE_NAME = "science-ieee"
FALLBACK_RC_PARAMS = {
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "lines.linewidth": 1.8,
    "lines.markersize": 5.0,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "legend.fontsize": 8,
    "savefig.bbox": "tight",
}
PLOT_COLORS = ["black", "0.35", "0.55", "0.7"]


def _load_matplotlib_modules():
    if find_spec("matplotlib") is None:
        raise ImportError(
            "Matplotlib is required for report plotting. Install optional plots extra."
        )

    matplotlib = import_module("matplotlib")
    matplotlib.use("Agg")
    plt = import_module("matplotlib.pyplot")
    return plt


def load_publication_pyplot():
    """Load pyplot with explicit SciencePlots detection and deterministic fallback."""
    plt = _load_matplotlib_modules()
    style_name = FALLBACK_STYLE_NAME

    if find_spec("scienceplots") is not None:
        import_module("scienceplots")
        plt.style.use(["science", "ieee"])
        style_name = SCIENCE_STYLE_NAME
    else:
        plt.style.use("default")
        plt.rcParams.update(FALLBACK_RC_PARAMS)

    plt.rcParams.update({"savefig.bbox": "tight"})
    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=PLOT_COLORS)
    return plt, style_name


def finalize_axes(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, linewidth=0.5, alpha=0.25)


def save_required_figure_outputs(fig, output_dir, stem):
    """Save one figure as mandatory PNG and PDF outputs, then validate both files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    png_path = output_dir / f"{stem}.png"
    pdf_path = output_dir / f"{stem}.pdf"

    fig.tight_layout()
    fig.savefig(png_path, dpi=300)
    fig.savefig(pdf_path)

    if not png_path.exists():
        raise RuntimeError(f"Plot output missing required PNG file: {png_path}")
    if not pdf_path.exists():
        raise RuntimeError(f"Plot output missing required PDF file: {pdf_path}")

    return str(png_path), str(pdf_path)
