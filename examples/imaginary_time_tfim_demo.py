import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from QML.PenQ import imaginary_time_tfim

def main():
    print("=== TFIM Variational Imaginary-Time Evolution (VITE) Demo ===")
    print("Running deterministic VITE on exact simulator (qml)...")
    
    result_exact = imaginary_time_tfim(
        n=4, 
        J=1.0, 
        h=0.5, 
        backend="qml",
        delta_tau=0.05,
        steps=20,
        max_layers=4,
        seed=42,
    )
    
    print("\nExact Backend Result:")
    print(f"Final Energy: {result_exact['energy']:.6f}")
    print("Energy History:")
    for step, energy in enumerate(result_exact['energy_history']):
        print(f"  Step {step:2d} | Energy: {energy:.6f}")
        
    print("\nRunning deterministic VITE on MPS simulator (mps_starter)...")
    result_mps = imaginary_time_tfim(
        n=4, 
        J=1.0, 
        h=0.5, 
        backend="mps",
        delta_tau=0.05,
        steps=20,
        max_layers=4,
        max_bond_dim=4,
        svd_cutoff=1e-12,
        seed=42,
    )
    
    print("\nMPS Backend Result:")
    print(f"Final Energy: {result_mps['energy']:.6f}")
    print("Energy History:")
    for step, energy in enumerate(result_mps['energy_history']):
        print(f"  Step {step:2d} | Energy: {energy:.6f}")

if __name__ == "__main__":
    main()
