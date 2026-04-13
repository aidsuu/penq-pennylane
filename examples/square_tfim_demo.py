import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import compare_square_tfim_exact_vs_mps
from QML.PenQ import square_tfim_observables


def main():
    print("=== 2D Square TFIM Demo (Mapped-Lattice Workflow) ===")
    print("Mapping: s(x,y) = x + Lx*y (row-major)")

    exact = square_tfim_observables(
        Lx=2,
        Ly=2,
        Jx=1.0,
        Jy=0.8,
        h=0.6,
        backend="qml",
        seed=7,
    )
    mps = square_tfim_observables(
        Lx=3,
        Ly=2,
        Jx=1.0,
        Jy=0.8,
        h=0.6,
        backend="mps",
        max_bond_dim=8,
        svd_cutoff=1e-12,
        seed=7,
    )
    comparison = compare_square_tfim_exact_vs_mps(
        Lx=2,
        Ly=2,
        Jx=1.0,
        Jy=0.8,
        h=0.6,
        max_bond_dim=8,
        svd_cutoff=1e-12,
        seed=7,
    )

    print("\nExact (2x2) observables:")
    print(f"energy={exact['energy']:.8f} energy_per_site={exact['energy_per_site']:.8f}")
    print(
        f"mx={exact['magnetization_x']:.8f} mz={exact['magnetization_z']:.8f} "
        f"zz_h={exact['nn_zz_horizontal']:.8f} zz_v={exact['nn_zz_vertical']:.8f}"
    )

    print("\nMPS mapped approximation (3x2) observables:")
    print(f"energy={mps['energy']:.8f} energy_per_site={mps['energy_per_site']:.8f}")
    print(
        f"mx={mps['magnetization_x']:.8f} mz={mps['magnetization_z']:.8f} "
        f"zz_h={mps['nn_zz_horizontal']:.8f} zz_v={mps['nn_zz_vertical']:.8f}"
    )

    print("\nExact-vs-MPS comparison (2x2):")
    print(
        f"abs_energy_error={comparison['abs_energy_error']:.8e} "
        f"abs_energy_error_per_site={comparison['abs_energy_error_per_site']:.8e} "
        f"abs_mx_error={comparison['abs_magnetization_x_error']:.8e}"
    )


if __name__ == "__main__":
    main()
