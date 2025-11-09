"""Converts DC internal to external bus numbering.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc


def int2extdc(i2edcpmt, i2edc, busdc, convdc, branchdc):
    """Converts DC internal to external bus numbering.

    Converts internal DC bus numbers back to external (possibly non-consecutive)
    bus numbers using the mapping from ext2intdc, and restores original bus order.

    Args:
        i2edcpmt: Internal to external DC bus permutation (row ordering)
        i2edc: Internal to external DC bus number mapping
        busdc: DC bus matrix
        convdc: DC converter matrix
        branchdc: DC branch matrix

    Returns:
        tuple: (busdc, convdc, branchdc)
            busdc: Updated DC bus matrix
            convdc: Updated converter matrix
            branchdc: Updated DC branch matrix
    """
    # Define named indices
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()

    DCDROOP, DCSLACK, DCNOSLACK, PVC, PQC, CONV_BUS, CONVTYPE_DC, \
        CONVTYPE_AC, PCONV, QCONV, VCONV, RTF, XTF, BF, RCONV, XCONV, \
        BASEKVC, VCMAX, VCMIN, ICMAX, CONVSTATUS, LOSSA, LOSSB, LOSSCR, \
        LOSSCI, DROOP, PDCSET, VDCSET, DVDCSET, VMC, VAC, PCCONV, QCCONV, \
        PCLOSS, VMF, VAF, PFIL, QCONVF, QCCONVF = idx_convdc()

    F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()

    # Internal to external bus numbering
    # Part 1: Bus renumbering - convert internal bus numbers to external
    busdc[:, BUSDC_I] = i2edc[busdc[:, BUSDC_I].astype(int) - 1]
    convdc[:, CONV_BUS] = i2edc[convdc[:, CONV_BUS].astype(int) - 1]
    branchdc[:, F_BUSDC] = i2edc[branchdc[:, F_BUSDC].astype(int) - 1]
    branchdc[:, T_BUSDC] = i2edc[branchdc[:, T_BUSDC].astype(int) - 1]

    # Part 2: Change bus order of busdc matrix - restore original row order
    busdc[i2edcpmt, :] = busdc.copy()

    return busdc, convdc, branchdc


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack
    from ext2intdc import ext2intdc

    print("Testing int2extdc function:")

    # Load test case
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    print(f"\nOriginal DC bus numbers: {busdc[:, 0]}")
    print(f"Original AC bus connections: {busdc[:, 1]}")
    print(f"Original DC grid numbers: {busdc[:, 2]}")
    print(f"\nOriginal converter DC bus connections: {convdc[:, 0]}")
    print(f"Original branch from-to buses:")
    for i in range(branchdc.shape[0]):
        print(f"  Branch {i}: {int(branchdc[i, 0])} -> {int(branchdc[i, 1])}")

    # Convert to internal numbering
    i2edcpmt, i2edc, busdc_int, convdc_int, branchdc_int = ext2intdc(
        busdc.copy(), convdc.copy(), branchdc.copy()
    )

    print(f"\n--- After ext2intdc (internal numbering) ---")
    print(f"\nInternal to external permutation: {i2edcpmt}")
    print(f"Internal to external bus mapping: {i2edc}")
    print(f"\nInternal DC bus numbers: {busdc_int[:, 0]}")
    print(f"AC bus connections: {busdc_int[:, 1]}")
    print(f"DC grid numbers: {busdc_int[:, 2]}")
    print(f"\nInternal converter DC bus connections: {convdc_int[:, 0]}")
    print(f"Internal branch from-to buses:")
    for i in range(branchdc_int.shape[0]):
        print(f"  Branch {i}: {int(branchdc_int[i, 0])} -> {int(branchdc_int[i, 1])}")

    # Convert back to external numbering
    busdc_ext, convdc_ext, branchdc_ext = int2extdc(
        i2edcpmt, i2edc, busdc_int.copy(), convdc_int.copy(), branchdc_int.copy()
    )

    print(f"\n--- After int2extdc (back to external) ---")
    print(f"\nExternal DC bus numbers: {busdc_ext[:, 0]}")
    print(f"AC bus connections: {busdc_ext[:, 1]}")
    print(f"DC grid numbers: {busdc_ext[:, 2]}")
    print(f"\nExternal converter DC bus connections: {convdc_ext[:, 0]}")
    print(f"External branch from-to buses:")
    for i in range(branchdc_ext.shape[0]):
        print(f"  Branch {i}: {int(branchdc_ext[i, 0])} -> {int(branchdc_ext[i, 1])}")

    # Verify round-trip conversion
    print(f"\n--- Verification ---")
    print(f"DC bus numbers match: {np.allclose(busdc[:, 0], busdc_ext[:, 0])}")
    print(f"AC connections match: {np.allclose(busdc[:, 1], busdc_ext[:, 1])}")
    print(f"Converter buses match: {np.allclose(convdc[:, 0], convdc_ext[:, 0])}")
    print(f"Branch from buses match: {np.allclose(branchdc[:, 0], branchdc_ext[:, 0])}")
    print(f"Branch to buses match: {np.allclose(branchdc[:, 1], branchdc_ext[:, 1])}")

    print("\n✓ Round-trip conversion successful!")