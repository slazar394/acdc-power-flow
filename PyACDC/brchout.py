"""Split branch matrix into operating and non-operating lines.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
from pypower.idx_brch import F_BUS, T_BUS, BR_STATUS

import numpy as np


def brchout(branch):
    """Split branch matrix into operating and non-operating lines.

    Returns separate branch matrices for lines in operation and those out
    of operation, as well as their indices in the original branch matrix.

    Args:
        branch: ac branch matrix

    Returns:
        tuple: (branch_operating, branch_operating_indices, branch_outage, branch_outage_indices)
            branch_operating: branch matrix with operating lines
            branch_operating_indices: indices of operating lines
            branch_outage: branch matrix with non-operating lines
            branch_outage_indices: indices of non-operating lines
    """
    # Branch status validity check
    status_vals = branch[:, BR_STATUS]
    if np.any((status_vals != 0) & (status_vals != 1)):
        raise ValueError('Branch status flags must be either 0 or 1')

    # Define indices of outage and operating branches
    branch_outage_indices = np.where(branch[:, BR_STATUS] == 0)[0]
    branch_operating_indices = np.where(branch[:, BR_STATUS] == 1)[0]

    # Define branch outage and operating matrices
    branch_outage = branch[branch_outage_indices, :]
    branch_operating = branch[branch_operating_indices, :]

    return branch_operating, branch_operating_indices, branch_outage, branch_outage_indices


if __name__ == "__main__":
    from Cases.PowerFlowAC.case5_stagg import case5_stagg

    print("Testing brchout function:")

    # Load test case
    baseMVA, bus, gen, branch = case5_stagg()

    print(f"\nOriginal branch matrix shape: {branch.shape}")
    print(f"All branches status: {branch[:, BR_STATUS]}")

    # Simulate an outage on branch 2
    branch_test = branch.copy()
    branch_test[1, BR_STATUS] = 0  # Set second branch to outage status

    print(f"\nAfter setting branch 2 to outage status: {branch_test[:, BR_STATUS]}")

    # Test brchout
    branch_operating, branch_operating_indices, branch_outage, branch_outage_indices = \
        brchout(branch_test)

    print(f"\nResults:")
    print(f"Number of operating branches: {len(branch_operating_indices)}")
    print(f"Operating branch indices: {branch_operating_indices}")
    print(f"Operating branches shape: {branch_operating.shape}")
    print(f"\nNumber of outage branches: {len(branch_outage_indices)}")
    print(f"Outage branch indices: {branch_outage_indices}")
    print(f"Outage branches shape: {branch_outage.shape}")

    # Show the connections for outage branch
    if len(branch_outage_indices) > 0:
        print(f"\nOutage branch connections:")
        for i, idx in enumerate(branch_outage_indices):
            from_bus = int(branch_test[idx, F_BUS])
            to_bus = int(branch_test[idx, T_BUS])
            print(f"  Branch {idx}: from bus {from_bus} to bus {to_bus}")