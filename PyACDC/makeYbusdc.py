"""Builds the DC bus admittance matrix and branch admittance matrices.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
from scipy.sparse import csr_matrix
from idx_brchdc import idx_brchdc

import numpy as np


def makeYbusdc(busdc, branchdc):
    """Builds the DC bus admittance matrix and branch admittance matrices.

    Returns the full bus admittance matrix (i.e. for all DC buses) and the
    matrices Yfdc and Ytdc which, when multiplied by the DC voltage vector,
    yield the vector currents injected into each DC line from the "from" and
    "to" buses respectively of each line.

    Args:
        busdc: DC bus matrix
        branchdc: DC branch matrix

    Returns:
        tuple: (Ybusdc, Yfdc, Ytdc)
            Ybusdc: DC bus admittance matrix
            Yfdc: Matrix which when multiplied by DC voltage vector, yields
                  currents from the "from" buses
            Ytdc: Matrix which when multiplied by DC voltage vector, yields
                  currents from the "to" buses

    For each branch, computes the elements of the branch admittance matrix where:
        | If |   | Yff  Yft |   | Vf |
        |    | = |          | * |    |
        | It |   | Ytf  Ytt |   | Vt |
    """
    # Define named indices
    F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()

    # Constants
    n = busdc.shape[0]  # Number of buses
    m = branchdc.shape[0]  # Number of branches

    # For each branch, compute branch admittance
    Ys = 1.0 / branchdc[:, BRDC_R]

    Ytt = Ys
    Yff = Ys
    Yft = -Ys
    Ytf = -Ys

    # Build connection matrices
    # Note: Bus numbers are 1-based, convert to 0-based indices
    f = branchdc[:, F_BUSDC].astype(int) - 1  # List of "from" buses (0-based)
    t = branchdc[:, T_BUSDC].astype(int) - 1  # List of "to" buses (0-based)

    # Connection matrix for line & from buses
    Cf = csr_matrix((np.ones(m), (np.arange(m), f)), shape=(m, n))
    # Connection matrix for line & to buses
    Ct = csr_matrix((np.ones(m), (np.arange(m), t)), shape=(m, n))

    # Build Yfdc and Ytdc such that Yfdc * V is the vector of branch currents
    # injected at each branch's "from" bus, and Ytdc is the same for the "to" bus
    i = np.tile(np.arange(m), 2)  # Double set of row indices

    Yfdc = csr_matrix(
        (np.concatenate([Yff, Yft]), (i, np.concatenate([f, t]))),
        shape=(m, n)
    )

    Ytdc = csr_matrix(
        (np.concatenate([Ytf, Ytt]), (i, np.concatenate([f, t]))),
        shape=(m, n)
    )

    # Build full bus admittance matrix
    Ybusdc = Cf.T @ Yfdc + Ct.T @ Ytdc

    return Ybusdc, Yfdc, Ytdc


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack

    print("Testing makeYbusdc function:")

    # Load test case
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    print(f"\nNumber of DC buses: {busdc.shape[0]}")
    print(f"Number of DC branches: {branchdc.shape[0]}")

    print(f"\nDC branch resistances:")
    for i in range(branchdc.shape[0]):
        from_bus = int(branchdc[i, 0])
        to_bus = int(branchdc[i, 1])
        resistance = branchdc[i, 2]
        print(f"  Branch {i}: {from_bus} -> {to_bus}, R = {resistance:.4f} p.u.")

    # Build admittance matrices
    Ybusdc, Yfdc, Ytdc = makeYbusdc(busdc, branchdc)

    print(f"\n--- Admittance Matrices ---")
    print(f"\nYbusdc shape: {Ybusdc.shape}")
    print(f"Ybusdc (full matrix):")
    print(Ybusdc.toarray())

    print(f"\nYfdc shape: {Yfdc.shape}")
    print(f"Yfdc (branch 'from' bus admittances):")
    print(Yfdc.toarray())

    print(f"\nYtdc shape: {Ytdc.shape}")
    print(f"Ytdc (branch 'to' bus admittances):")
    print(Ytdc.toarray())

    # Verify properties
    print(f"\n--- Verification ---")
    print(f"Ybusdc is symmetric: {np.allclose(Ybusdc.toarray(), Ybusdc.toarray().T)}")
    print(f"Sum of each row in Ybusdc (should be ~0 for passive network):")
    row_sums = np.array(Ybusdc.sum(axis=1)).flatten()
    print(f"  {row_sums}")