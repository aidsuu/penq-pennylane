from QML.PenQ.penq_algorithms import adaptive_tfim_vqe
from QML.PenQ.penq_algorithms import compare_tfim_vqe_exact_vs_mps


def demo_rows():
    """Run small deterministic adaptive TFIM VQE demo on exact and MPS backends."""
    exact_result = adaptive_tfim_vqe(n=6, J=1.0, h=0.5, backend="qml", max_layers=4, steps=2)
    mps_result = adaptive_tfim_vqe(
        n=6,
        J=1.0,
        h=0.5,
        backend="mps",
        max_layers=4,
        max_bond_dim=4,
        svd_cutoff=1e-12,
        steps=2,
    )
    comparison = compare_tfim_vqe_exact_vs_mps(
        n=6,
        J=1.0,
        h=0.5,
        max_layers=4,
        max_bond_dim=4,
        svd_cutoff=1e-12,
        steps=2,
    )
    return {
        "exact": exact_result,
        "mps": mps_result,
        "comparison": comparison,
    }


def main():
    rows = demo_rows()
    print("workflow=Adaptive TFIM VQE demo")
    print("hamiltonian=H=-J sum_i Z_i Z_{i+1} - h sum_i X_i")
    print("objective=E(theta)=<psi(theta)|H|psi(theta)>")
    print("ansatz=U_l(gamma_l,beta_l)=U_X(beta_l)U_ZZ(gamma_l), |psi_L>=prod_l U_l |+>^n")
    print("identity=CNOT-RZ(2 gamma)-CNOT=exp(-i gamma Z⊗Z)")
    for label in ("exact", "mps"):
        result = rows[label]
        print(
            f"backend={result['backend']} n={result['n']} J={result['J']:.2f} h={result['h']:.2f} "
            f"layers={result['layers_used']} energy={result['energy']:.8f} "
            f"energy_per_site={result['energy_per_site']:.8f} "
            f"x0={result['expval_x0']:.8f} z0z1={result['expval_z0z1']:.8f} "
            f"converged={result['converged']} delta={result['final_delta_energy']:.8f}"
        )
    print(
        f"exact_vs_mps_abs_error={rows['comparison']['abs_energy_error']:.8f} "
        f"abs_error_per_site={rows['comparison']['abs_energy_error_per_site']:.8f}"
    )


if __name__ == "__main__":
    main()
