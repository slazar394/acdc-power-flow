"""Converts internal per unit values to original values.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc


def int2extpu(baseMVA, baseMVAac, baseMVAdc, busdc, convdc, branchdc):
    """Converts internal per unit values to original values.

    Converts internal per unit values of the DC matrices (busdc, convdc
    and branchdc) to the original bases provided in the input files.

    Only p.u. impedances and currents are changed. Voltages (p.u.) and
    powers (real values) are left unaltered.

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

    F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()

    DCDROOP, DCSLACK, DCNOSLACK, PVC, PQC, CONV_BUS, CONVTYPE_DC, \
        CONVTYPE_AC, PCONV, QCONV, VCONV, RTF, XTF, BF, RCONV, XCONV, \
        BASEKVC, VCMAX, VCMIN, ICMAX, CONVSTATUS, LOSSA, LOSSB, LOSSCR, \
        LOSSCI, DROOP, PDCSET, VDCSET, DVDCSET, VMC, VAC, PCCONV, QCCONV, \
        PCLOSS, VMF, VAF, PFIL, QCONVF, QCCONVF = idx_convdc()

    # Per unit conversion
    # Only p.u. impedances and currents are changed. Voltages (p.u.) and
    # powers (real values) are left unaltered.

    # Converter AC side conversion
    convdc[:, RTF] = convdc[:, RTF] * baseMVAac / baseMVA  # (p.u.)
    convdc[:, XTF] = convdc[:, XTF] * baseMVAac / baseMVA  # (p.u.)
    convdc[:, BF] = convdc[:, BF] * baseMVAac / baseMVA  # (p.u.)
    convdc[:, RCONV] = convdc[:, RCONV] * baseMVAac / baseMVA  # (p.u.)
    convdc[:, XCONV] = convdc[:, XCONV] * baseMVAac / baseMVA  # (p.u.)
    convdc[:, ICMAX] = convdc[:, ICMAX] * baseMVA / baseMVAac

    # DC side per unit convention
    # basekAdc = baseMVAdc/basekVdc
    # baseRdc  = basekVdc^2/baseMVAdc

    # Converter DC side conversion
    baseR_busdc = busdc[:, BASE_KVDC] ** 2 / baseMVAdc  # (Ohm)
    baseR_busdc2ac = busdc[:, BASE_KVDC] ** 2 / baseMVA  # (Ohm)
    busdc[:, CDC] = busdc[:, CDC] / baseR_busdc2ac * baseR_busdc  # (p.u.*s)

    # DC network branch conversion
    baseKVDC_brch = busdc[branchdc[:, F_BUSDC].astype(int) - 1, BASE_KVDC]
    baseR_brchdc = baseKVDC_brch ** 2 / baseMVAdc
    baseR_brchdc2ac = baseKVDC_brch ** 2 / baseMVA

    branchdc[:, BRDC_R] = branchdc[:, BRDC_R] * baseR_brchdc2ac / baseR_brchdc  # (p.u.)
    branchdc[:, BRDC_L] = branchdc[:, BRDC_L] * baseR_brchdc2ac / baseR_brchdc  # (p.u./s)
    branchdc[:, BRDC_C] = branchdc[:, BRDC_C] / baseR_brchdc2ac * baseR_brchdc  # (p.u.*s)

    return busdc, convdc, branchdc


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack
    from ext2intpu import ext2intpu

    print("Testing int2extpu function:")

    # Load test case
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    # Use different base MVA for AC system
    baseMVA = 100

    print(f"\nBase MVA values:")
    print(f"  baseMVA (AC system): {baseMVA}")
    print(f"  baseMVAac (converter AC): {baseMVAac}")
    print(f"  baseMVAdc (DC system): {baseMVAdc}")

    print(f"\nOriginal values (before any conversion):")
    print(f"  RTF (first converter): {convdc[0, 6]:.6f}")
    print(f"  ICMAX (first converter): {convdc[0, 14]:.6f}")
    print(f"  BRDC_R (first branch): {branchdc[0, 2]:.6f}")

    # Convert to internal per unit
    busdc_int, convdc_int, branchdc_int = ext2intpu(
        baseMVA, baseMVAac, baseMVAdc,
        busdc.copy(), convdc.copy(), branchdc.copy()
    )

    print(f"\nAfter ext2intpu (internal per unit):")
    print(f"  RTF (first converter): {convdc_int[0, 6]:.6f}")
    print(f"  ICMAX (first converter): {convdc_int[0, 14]:.6f}")
    print(f"  BRDC_R (first branch): {branchdc_int[0, 2]:.6f}")

    # Convert back to original per unit
    busdc_back, convdc_back, branchdc_back = int2extpu(
        baseMVA, baseMVAac, baseMVAdc,
        busdc_int.copy(), convdc_int.copy(), branchdc_int.copy()
    )

    print(f"\nAfter int2extpu (back to original):")
    print(f"  RTF (first converter): {convdc_back[0, 6]:.6f}")
    print(f"  ICMAX (first converter): {convdc_back[0, 14]:.6f}")
    print(f"  BRDC_R (first branch): {branchdc_back[0, 2]:.6f}")

    # Verify round-trip conversion
    print(f"\n--- Verification ---")
    print(f"RTF matches original: {np.isclose(convdc[0, 6], convdc_back[0, 6])}")
    print(f"ICMAX matches original: {np.isclose(convdc[0, 14], convdc_back[0, 14])}")
    print(f"BRDC_R matches original: {np.isclose(branchdc[0, 2], branchdc_back[0, 2])}")

    print("\n✓ Round-trip conversion successful!")