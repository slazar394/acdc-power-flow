"""Converts external per unit inputs to internal values.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc


import numpy as np


def ext2intpu(baseMVA, baseMVAac, baseMVAdc, busdc, convdc, branchdc):
    """Converts external per unit quantities to internal per unit quantities.

    Converts external per unit quantities of the DC bus, converter and branch
    matrix into internal per unit quantities using the AC power network base.

    Only p.u. impedances and currents are changed. Voltages (p.u.) and powers
    (real values) are left unaltered.

    Args:
        baseMVA: Base power of AC power flow data
        baseMVAac: Base power of AC data of the converters
        baseMVAdc: Base power of DC data of the DC system
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

    # Per unit conversion
    # Only p.u. impedances and currents are changed. Voltages (p.u.) and
    # powers (real values) are left unaltered.

    # Converter AC side conversion
    convdc[:, RTF] = convdc[:, RTF] * baseMVA / baseMVAac  # (p.u.)
    convdc[:, XTF] = convdc[:, XTF] * baseMVA / baseMVAac  # (p.u.)
    convdc[:, BF] = convdc[:, BF] * baseMVA / baseMVAac  # (p.u.)
    convdc[:, RCONV] = convdc[:, RCONV] * baseMVA / baseMVAac  # (p.u.)
    convdc[:, XCONV] = convdc[:, XCONV] * baseMVA / baseMVAac  # (p.u.)
    convdc[:, ICMAX] = convdc[:, ICMAX] * baseMVAac / baseMVA

    # DC side per unit convention
    # basekAdc = baseMVAdc/basekVdc
    # baseRdc  = basekVdc^2/baseMVAdc

    # Converter DC side conversion
    baseR_busdc = busdc[:, BASE_KVDC] ** 2 / baseMVAdc  # (Ohm)
    baseR_busdc2ac = busdc[:, BASE_KVDC] ** 2 / baseMVA  # (Ohm)
    busdc[:, CDC] = busdc[:, CDC] / baseR_busdc * baseR_busdc2ac  # (p.u.*s)

    # DC network branch conversion
    # Check for equal base voltages at two sides of a DC branch
    V_from = busdc[branchdc[:, F_BUSDC].astype(int) - 1, BASE_KVDC]  # Voltage at 'from' bus
    V_to = busdc[branchdc[:, T_BUSDC].astype(int) - 1, BASE_KVDC]  # Voltage at 'to' bus

    if np.sum(V_from != V_to) > 0:
        raise ValueError('The DC voltages at both sides of a DC branch do not match.')

    baseKVDC_brch = busdc[branchdc[:, F_BUSDC].astype(int) - 1, BASE_KVDC]
    baseR_brchdc = baseKVDC_brch ** 2 / baseMVAdc
    baseR_brchdc2ac = baseKVDC_brch ** 2 / baseMVA

    branchdc[:, BRDC_R] = branchdc[:, BRDC_R] * baseR_brchdc / baseR_brchdc2ac  # (p.u.)
    branchdc[:, BRDC_L] = branchdc[:, BRDC_L] * baseR_brchdc / baseR_brchdc2ac  # (p.u./s)
    branchdc[:, BRDC_C] = branchdc[:, BRDC_C] / baseR_brchdc * baseR_brchdc2ac  # (p.u.*s)

    return busdc, convdc, branchdc


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack

    print("Testing ext2intpu function:")

    # Load test case
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    # Use different base MVA for AC system
    baseMVA = 100

    print(f"\nBase MVA values:")
    print(f"  baseMVA (AC system): {baseMVA}")
    print(f"  baseMVAac (converter AC): {baseMVAac}")
    print(f"  baseMVAdc (DC system): {baseMVAdc}")

    print(f"\nOriginal converter impedances (first converter):")
    print(f"  RTF: {convdc[0, 6]}")
    print(f"  XTF: {convdc[0, 7]}")
    print(f"  BF: {convdc[0, 8]}")
    print(f"  RCONV: {convdc[0, 9]}")
    print(f"  XCONV: {convdc[0, 10]}")
    print(f"  ICMAX: {convdc[0, 14]}")

    print(f"\nOriginal DC branch resistance (first branch):")
    print(f"  BRDC_R: {branchdc[0, 2]}")

    print(f"\nOriginal DC bus capacitance (first bus):")
    print(f"  CDC: {busdc[0, 8]}")

    # Convert to internal per unit
    busdc_int, convdc_int, branchdc_int = ext2intpu(
        baseMVA, baseMVAac, baseMVAdc,
        busdc.copy(), convdc.copy(), branchdc.copy()
    )

    print(f"\n--- After per unit conversion ---")
    print(f"\nNew converter impedances (first converter):")
    print(f"  RTF: {convdc_int[0, 6]}")
    print(f"  XTF: {convdc_int[0, 7]}")
    print(f"  BF: {convdc_int[0, 8]}")
    print(f"  RCONV: {convdc_int[0, 9]}")
    print(f"  XCONV: {convdc_int[0, 10]}")
    print(f"  ICMAX: {convdc_int[0, 14]}")

    print(f"\nNew DC branch resistance (first branch):")
    print(f"  BRDC_R: {branchdc_int[0, 2]}")

    print(f"\nNew DC bus capacitance (first bus):")
    print(f"  CDC: {busdc_int[0, 8]}")

    # Verify conversion ratios
    print(f"\n--- Conversion ratios ---")
    print(f"Converter impedance ratio (baseMVA/baseMVAac): {baseMVA / baseMVAac}")
    print(f"Converter current ratio (baseMVAac/baseMVA): {baseMVAac / baseMVA}")