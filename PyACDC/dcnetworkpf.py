"""Runs the DC network power flow.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from scipy.sparse import csr_matrix, issparse


def dcnetworkpf(Ybusdc, Vdc, Pdc, slack, noslack, droop, PVdroop, Pdcset,
                Vdcset, dVdcset, pol, tol, itmax):
    """Runs the DC network power flow.

    Runs the DC network power flow, possibly including several DC grids.
    Each DC network can have DC slack buses or several converters in DC
    voltage control.

    Args:
        Ybusdc: DC network bus admittance matrix (possibly multiple DC grids)
        Vdc: Vector with voltages at each DC bus
        Pdc: Vector with DC power extractions at each DC bus
        slack: Bus numbers of DC slack buses (1-based)
        noslack: Bus numbers of non-DC slack buses (1-based)
        droop: Bus numbers with distributed voltage control (1-based)
        PVdroop: Voltage droop gain
        Pdcset: Voltage droop power set-point
        Vdcset: Voltage droop voltage set-point
        dVdcset: Voltage droop deadband
        pol: DC grids topology (1=monopolar asymmetric, 2=monopolar symmetric/bipolar)
        tol: Newton's method tolerance
        itmax: Newton's method maximum iterations

    Returns:
        tuple: (Vdc, Pdc)
            Vdc: Updated vector with voltages at each DC bus
            Pdc: Updated vector with DC power extractions at each DC bus
    """
    # Initialization
    nb = len(Vdc)  # Number of DC buses
    Pdc1 = -Pdc.copy()  # Convention on power flow direction

    # Convert bus numbers to 0-based indices
    slack_idx = (slack - 1).astype(int)
    noslack_idx = (noslack - 1).astype(int)
    droop_idx = (droop - 1).astype(int) if len(droop) > 0 else np.array([], dtype=int)

    # Droop power set-points
    if len(droop_idx) > 0:
        Pdc1[droop_idx] = -Pdcset[droop_idx]

    # Convert Ybusdc to CSR format if sparse for efficient operations
    if issparse(Ybusdc):
        Ybusdc = Ybusdc.tocsr()

    # DC network iteration
    it = 0
    converged = False

    # Newton-Raphson iteration
    while not converged and it <= itmax:
        # Update iteration counter
        it += 1

        # Calculate power injections and Jacobian matrix
        Pdccalc = pol * Vdc * (Ybusdc @ Vdc)

        # Build Jacobian: J[i,j] = pol * Ybusdc[i,j] * Vdc[i] * Vdc[j]
        Vdc_outer = np.outer(Vdc, Vdc)
        if issparse(Ybusdc):
            # Sparse matrix - element-wise multiplication
            J = pol * Ybusdc.multiply(Vdc_outer)
            J = J.tocsr()  # Ensure CSR format
        else:
            # Dense matrix
            J = pol * Ybusdc * Vdc_outer

        # Replace diagonal elements: J[i,i] += Pdccalc[i]
        if issparse(J):
            # For sparse matrices
            diag_vals = np.array(J.diagonal()).flatten() + Pdccalc
            J.setdiag(diag_vals)
        else:
            # For dense matrices
            np.fill_diagonal(J, np.diag(J) + Pdccalc)

        # Include droop characteristics
        if len(droop_idx) > 0:
            # Define set-point with deadband
            Vdcsetlh = np.where(
                np.abs(Vdc - Vdcset) <= dVdcset,
                Vdc,
                np.where(
                    (Vdc - Vdcset) > dVdcset,
                    Vdcset + dVdcset,
                    Vdcset - dVdcset
                )
            )

            # Droop addition to power calculation
            Pdccalc[droop_idx] += (1.0 / PVdroop[droop_idx]) * (Vdc[droop_idx] - Vdcsetlh[droop_idx])

            # Update Jacobian diagonal for droop buses
            if issparse(J):
                for i in droop_idx:
                    J[i, i] = J[i, i] + (1.0 / PVdroop[i]) * Vdc[i]
            else:
                for i in droop_idx:
                    J[i, i] += (1.0 / PVdroop[i]) * Vdc[i]

        # DC network solution - reduce Jacobian
        if issparse(J):
            Jr = J[noslack_idx, :][:, noslack_idx]
        else:
            Jr = J[np.ix_(noslack_idx, noslack_idx)]

        dPdcr = Pdc1[noslack_idx] - Pdccalc[noslack_idx]  # Power mismatch vector

        # Solve for voltage corrections
        if issparse(Jr):
            from scipy.sparse.linalg import spsolve
            dVr = spsolve(Jr, dPdcr)
        else:
            dVr = np.linalg.solve(Jr, dPdcr)

        # Update DC voltages
        Vdc[noslack_idx] = Vdc[noslack_idx] * (1.0 + dVr)

        # Convergence check
        if np.max(np.abs(dVr)) < tol:
            converged = True

    # Convergence print
    if not converged:
        print(f'\nDC network power flow did NOT converge after {it} iterations')

    # Output update
    # Recalculate slack bus powers
    if len(slack_idx) > 0:
        Pdc1[slack_idx] = pol * Vdc[slack_idx] * (Ybusdc[slack_idx, :] @ Vdc)
        Pdc[slack_idx] = -Pdc1[slack_idx]

    # Recalculate voltage droop bus powers
    if len(droop_idx) > 0:
        Pdc1[droop_idx] = pol * Vdc[droop_idx] * (Ybusdc[droop_idx, :] @ Vdc)
        Pdc[droop_idx] = -Pdc1[droop_idx]

    return Vdc, Pdc


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack

    print("Testing dcnetworkpf function:")

    # Load test case
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    # Build admittance matrix
    from makeYbusdc import makeYbusdc
    Ybusdc, Yfdc, Ytdc = makeYbusdc(busdc, branchdc)

    # Setup power flow parameters
    nb = busdc.shape[0]
    Vdc = np.ones(nb)  # Initial voltages (p.u.)
    Pdc = np.array([0.0, 0.0, 0.0])  # Initial power extractions

    # Define bus types (1-based bus numbers)
    slack = np.array([2])  # Bus 2 is slack
    noslack = np.array([1, 3])  # Buses 1 and 3 are not slack
    droop = np.array([])  # No droop control in this case

    # Droop parameters (empty for this case)
    PVdroop = np.zeros(nb)
    Pdcset = np.zeros(nb)
    Vdcset = np.ones(nb)
    dVdcset = np.zeros(nb)

    # Power flow settings
    tol = 1e-8
    itmax = 10

    print(f"\nInitial conditions:")
    print(f"  Number of buses: {nb}")
    print(f"  Slack bus: {slack}")
    print(f"  Non-slack buses: {noslack}")
    print(f"  Initial Vdc: {Vdc}")
    print(f"  Initial Pdc: {Pdc}")
    print(f"  Pole configuration: {pol}")

    # Run DC power flow
    Vdc_result, Pdc_result = dcnetworkpf(
        Ybusdc, Vdc.copy(), Pdc.copy(), slack, noslack, droop,
        PVdroop, Pdcset, Vdcset, dVdcset, pol, tol, itmax
    )

    print(f"\n--- Power Flow Results ---")
    print(f"Final Vdc: {Vdc_result}")
    print(f"Final Pdc: {Pdc_result}")

    print("\n✓ DC network power flow completed successfully!")