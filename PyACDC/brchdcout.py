"""Split branchdc matrix into operating and non-operating lines.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
from idx_brchdc import idx_brchdc

import numpy as np


def brchdcout(branchdc):
    """Split branchdc matrix into operating and non-operating lines.

    Returns separate branch matrices for lines in operation and those out
    of operation, as well as their indices in the original branch matrix.

    Args:
        branchdc: dc branch matrix

    Returns:
        tuple: (branch_operating, branch_operating_indices, branch_outage, branch_outage_indices)
            branch_operating: dc branch matrix with operating lines
            branch_operating_indices: indices of operating dc lines
            branch_outage: dc branch matrix with non-operating lines
            branch_outage_indices: indices of non-operating dc lines
    """
    # Define named indices
    F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()

    # Branch status validity check
    status_vals = branchdc[:, BRDC_STATUS]
    if np.any((status_vals != 0) & (status_vals != 1)):
        raise ValueError('Branch status flags must be either 0 or 1')

    # Define indices of outage and operating branches
    branch_outage_indices = np.where(branchdc[:, BRDC_STATUS] == 0)[0]
    branch_operating_indices = np.where(branchdc[:, BRDC_STATUS] == 1)[0]

    # Define branch outage and operating matrices
    branch_outage = branchdc[branch_outage_indices, :]
    branch_operating = branchdc[branch_operating_indices, :]

    return branch_operating, branch_operating_indices, branch_outage, branch_outage_indices


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack

    print("Testing brchdcout function:")

    # Load test case
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    print(f"\nOriginal branch matrix shape: {branchdc.shape}")
    print(f"All branches status: {branchdc[:, 8]}")  # BRDC_STATUS is at index 8

    # Simulate an outage on branch 2
    branchdc_test = branchdc.copy()
    branchdc_test[1, 8] = 0  # Set second branch to outage status

    print(f"\nAfter setting branch 2 to outage status: {branchdc_test[:, 8]}")

    # Test brchdcout
    branch_operating, branch_operating_indices, branch_outage, branch_outage_indices = \
        brchdcout(branchdc_test)

    print(f"\nResults:")
    print(f"Number of operating branches: {len(branch_operating_indices)}")
    print(f"Operating branch indices: {branch_operating_indices}")
    print(f"Operating branches shape: {branch_operating.shape}")
    print(f"\nNumber of outage branches: {len(branch_outage_indices)}")
    print(f"Outage branch indices: {branch_outage_indices}")
    print(f"Outage branches shape: {branch_outage.shape}")

    # Show the connections for outage branch
    if len(branch_outage_indices) > 0:
        F_BUSDC, T_BUSDC, _, _, _, _, _, _, _, _, _ = idx_brchdc()
        print(f"\nOutage branch connections:")
        for i, idx in enumerate(branch_outage_indices):
            from_bus = int(branchdc_test[idx, F_BUSDC])
            to_bus = int(branchdc_test[idx, T_BUSDC])
            print(f"  Branch {idx}: from bus {from_bus} to bus {to_bus}")