"""Converts dc external to internal bus numbering.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc


def ext2intdc(busdc, convdc, branchdc):
    """Converts external dc bus numbers to consecutive internal bus numbers.

    Converts external dc bus numbers (possibly non-consecutive) to consecutive
    internal bus numbers, starting at 1.

    Args:
        busdc: dc bus matrix
        convdc: dc converter matrix
        branchdc: dc branch matrix

    Returns:
        tuple: (internal_to_external_pmt, internal_to_external, busdc, convdc, branchdc)
            internal_to_external_pmt: Internal to external dc bus permutation.
                All dc buses with an ac grid connection are grouped, followed by
                the dc buses without a converter or with a converter outage.
                Buses are grouped per dc grid.
            internal_to_external: Internal to external dc bus number mapping
            busdc: Updated dc bus matrix with internal numbering
            convdc: Updated converter matrix with internal numbering
            branchdc: Updated dc branch matrix with internal numbering
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

    # Check grid numbering
    griddc = np.sort(np.unique(busdc[:, GRIDDC]))
    expected = np.arange(1, len(griddc) + 1)
    if not np.all(griddc == expected):
        raise ValueError('Non-successive dc grid numbering detected')

    # Part 1: Group all dc buses without ac grid connection
    # Buses with AC connection come first, then buses without AC connection
    no_ac_bus_indices = np.where(busdc[:, BUSAC_I] == 0)[0]
    ac_bus_indices = np.where(busdc[:, BUSAC_I] != 0)[0]
    internal_to_external_pmt = np.concatenate([ac_bus_indices, no_ac_bus_indices])
    busdc = busdc[internal_to_external_pmt, :]

    # Part 2: Sort dc buses based on dc grid number
    # Add permutation indices as last column temporarily
    busdc_ext = np.column_stack([busdc, internal_to_external_pmt])
    # Sort by GRIDDC column
    sort_indices = np.argsort(busdc_ext[:, GRIDDC])
    busdc_ext = busdc_ext[sort_indices, :]
    # Extract sorted data
    busdc = busdc_ext[:, :busdc.shape[1]]
    internal_to_external_pmt = busdc_ext[:, -1].astype(int)

    # Rename dc nodes
    # internal_to_external: maps internal bus number to external bus number
    internal_to_external = busdc[:, BUSDC_I].astype(int)

    # external_to_internal: maps external bus number to internal bus number
    max_bus_num = int(np.max(internal_to_external))
    external_to_internal = np.zeros(max_bus_num + 1, dtype=int)
    external_to_internal[internal_to_external] = np.arange(1, busdc.shape[0] + 1)

    # Update bus numbers to internal numbering (1-based for compatibility with MATLAB)
    busdc[:, BUSDC_I] = np.arange(1, busdc.shape[0] + 1)

    # Update converter and branch matrices
    convdc[:, CONV_BUS] = external_to_internal[convdc[:, CONV_BUS].astype(int)]
    branchdc[:, F_BUSDC] = external_to_internal[branchdc[:, F_BUSDC].astype(int)]
    branchdc[:, T_BUSDC] = external_to_internal[branchdc[:, T_BUSDC].astype(int)]

    return internal_to_external_pmt, internal_to_external, busdc, convdc, branchdc


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack

    print("Testing ext2intdc function:")

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
    internal_to_external_pmt, internal_to_external, busdc_int, convdc_int, branchdc_int = \
        ext2intdc(busdc.copy(), convdc.copy(), branchdc.copy())

    print(f"\n--- After conversion to internal numbering ---")
    print(f"\nInternal to external permutation: {internal_to_external_pmt}")
    print(f"Internal to external bus mapping: {internal_to_external}")
    print(f"\nNew DC bus numbers: {busdc_int[:, 0]}")
    print(f"AC bus connections: {busdc_int[:, 1]}")
    print(f"DC grid numbers: {busdc_int[:, 2]}")
    print(f"\nNew converter DC bus connections: {convdc_int[:, 0]}")
    print(f"New branch from-to buses:")
    for i in range(branchdc_int.shape[0]):
        print(f"  Branch {i}: {int(branchdc_int[i, 0])} -> {int(branchdc_int[i, 1])}")