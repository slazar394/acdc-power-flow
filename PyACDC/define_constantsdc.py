"""Defines constants for named column indices to DC system data matrices.

This module defines the names for all column indices used in the busdc,
convdc and branchdc matrices. These indices also refer to columns that
are added as a result of the AC/DC power flow. The constants also
include compare values.

busdc:
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX,
    VDCMIN, CDC

convdc:
    DCDROOP, DCSLACK, DCNOSLACK, PVC, PQC, CONV_BUS, CONVTYPE_DC,
    CONVTYPE_AC, PCONV, QCONV, VCONV, RTF, XTF, BF, RCONV, XCONV,
    BASEKVC, VCMAX, VCMIN, ICMAX, CONVSTATUS, LOSSA, LOSSB, LOSSCR,
    LOSSCI, DROOP, PDCSET, VDCSET, DVDCSET, VMC, VAC, PCCONV, QCCONV,
    PCLOSS, VMF, VAF, PFIL, QCONVF, QCCONVF

branchdc:
    F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B,
    RATEDC_C, BRDC_STATUS, PFDC, PTDC

See also idx_busdc, idx_convdc and idx_brchdc.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""

from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc

# Define named indices into busdc, convdc, branchdc matrices
BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()

DCDROOP, DCSLACK, DCNOSLACK, PVC, PQC, CONV_BUS, CONVTYPE_DC, \
    CONVTYPE_AC, PCONV, QCONV, VCONV, RTF, XTF, BF, RCONV, XCONV, \
    BASEKVC, VCMAX, VCMIN, ICMAX, CONVSTATUS, LOSSA, LOSSB, LOSSCR, \
    LOSSCI, DROOP, PDCSET, VDCSET, DVDCSET, VMC, VAC, PCCONV, QCCONV, \
    PCLOSS, VMF, VAF, PFIL, QCONVF, QCCONVF = idx_convdc()

F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
    RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()

# Export all constants
__all__ = [
    # busdc indices
    'BUSDC_I', 'BUSAC_I', 'GRIDDC', 'PDC', 'VDC', 'BASE_KVDC', 'VDCMAX',
    'VDCMIN', 'CDC',

    # convdc indices
    'DCDROOP', 'DCSLACK', 'DCNOSLACK', 'PVC', 'PQC', 'CONV_BUS', 'CONVTYPE_DC',
    'CONVTYPE_AC', 'PCONV', 'QCONV', 'VCONV', 'RTF', 'XTF', 'BF', 'RCONV', 'XCONV',
    'BASEKVC', 'VCMAX', 'VCMIN', 'ICMAX', 'CONVSTATUS', 'LOSSA', 'LOSSB', 'LOSSCR',
    'LOSSCI', 'DROOP', 'PDCSET', 'VDCSET', 'DVDCSET', 'VMC', 'VAC', 'PCCONV', 'QCCONV',
    'PCLOSS', 'VMF', 'VAF', 'PFIL', 'QCONVF', 'QCCONVF',

    # branchdc indices
    'F_BUSDC', 'T_BUSDC', 'BRDC_R', 'BRDC_L', 'BRDC_C', 'RATEDC_A', 'RATEDC_B',
    'RATEDC_C', 'BRDC_STATUS', 'PFDC', 'PTDC'
]

if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack

    print("DC System Constants:")
    print("\n=== BUSDC Indices ===")
    print(f"BUSDC_I: {BUSDC_I}, BUSAC_I: {BUSAC_I}, GRIDDC: {GRIDDC}")
    print(f"PDC: {PDC}, VDC: {VDC}, BASE_KVDC: {BASE_KVDC}")
    print(f"VDCMAX: {VDCMAX}, VDCMIN: {VDCMIN}, CDC: {CDC}")

    print("\n=== CONVDC Indices (first 10) ===")
    print(f"DCDROOP: {DCDROOP}, DCSLACK: {DCSLACK}, DCNOSLACK: {DCNOSLACK}")
    print(f"PVC: {PVC}, PQC: {PQC}, CONV_BUS: {CONV_BUS}")
    print(f"CONVTYPE_DC: {CONVTYPE_DC}, CONVTYPE_AC: {CONVTYPE_AC}")
    print(f"PCONV: {PCONV}, QCONV: {QCONV}")

    print("\n=== BRANCHDC Indices ===")
    print(f"F_BUSDC: {F_BUSDC}, T_BUSDC: {T_BUSDC}")
    print(f"BRDC_R: {BRDC_R}, BRDC_L: {BRDC_L}, BRDC_C: {BRDC_C}")
    print(f"RATEDC_A: {RATEDC_A}, RATEDC_B: {RATEDC_B}, RATEDC_C: {RATEDC_C}")
    print(f"BRDC_STATUS: {BRDC_STATUS}, PFDC: {PFDC}, PTDC: {PTDC}")

    print("\n✓ All DC constants defined successfully!")

    # Example usage
    print("\n=== Example Usage ===")

    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    print(f"\nAccessing data using constants:")
    print(f"DC Bus 1 voltage: {busdc[0, VDC]:.3f} p.u.")
    print(f"DC Bus 1 power: {busdc[0, PDC]:.3f} MW")
    print(f"Converter 1 DC bus: {int(convdc[0, CONV_BUS])}")
    print(f"Branch 1 resistance: {branchdc[0, BRDC_R]:.4f} p.u.")