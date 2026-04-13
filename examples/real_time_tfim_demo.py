import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import real_time_tfim


def main():
    print("=== TFIM Real-Time Evolution Demo ===")
    print("Running deterministic real-time evolution on exact simulator (qml)...")

    result_exact = real_time_tfim(
        n=4,
        J=1.0,
        h=0.5,
        backend="qml",
        dt=0.05,
        steps=20,
    )

    print("\nExact Backend Result:")
    print(f"Final Time: {result_exact['time_history'][-1]:.3f}")
    print(f"Final Energy: {result_exact['energy']:.6f}")

    print("\nRunning deterministic real-time evolution on MPS simulator (mps_starter)...")
    result_mps = real_time_tfim(
        n=4,
        J=1.0,
        h=0.5,
        backend="mps",
        dt=0.05,
        steps=20,
        max_bond_dim=4,
        svd_cutoff=1e-12,
    )

    print("\nMPS Backend Result:")
    print(f"Final Time: {result_mps['time_history'][-1]:.3f}")
    print(f"Final Energy: {result_mps['energy']:.6f}")


if __name__ == "__main__":
    main()
