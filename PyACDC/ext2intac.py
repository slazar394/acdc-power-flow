"""Converts external to internal bus numbering.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from idx_busdc import idx_busdc
from pypower.idx_bus import PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, \
    BUS_AREA, VM, VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN
from pypower.idx_gen import GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, \
    PMAX, PMIN, MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN, PC1, PC2, QC1MIN, QC1MAX, \
    QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF
from pypower.idx_brch import F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, \
    RATE_C, TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST, ANGMIN, \
    ANGMAX, MU_ANGMIN, MU_ANGMAX


def ext2intac(busdc, bus, gen, branch):
    """Converts external AC bus numbers to consecutive internal bus numbers.

    Converts external AC bus numbers (possibly non-consecutive) to consecutive
    internal bus numbers. The AC grid is sorted based on converter-connected buses
    and DC buses, per DC grid. Dummy AC buses are assigned to DC buses without a
    connection to the AC grid. All other AC buses are grouped at the end.

    Example sorting result for 2 DC grids with outages in grid 1:
        DC grid 1:
            1-4: AC buses connected to DC buses 1-4 (DC grid 1)
            5: Dummy AC bus for DC bus 5 (converter outage in DC grid 1)
        DC grid 2:
            7-9: AC buses connected to DC buses 7-9 (DC grid 2)
        Rest of AC system:
            10+: AC buses without connection to DC grid

    Args:
        busdc: DC bus matrix
        bus: AC bus matrix
        gen: Generator matrix
        branch: AC branch matrix

    Returns:
        tuple: (internal_to_external_ac, dummy_ac_indices, busdc, bus, gen, branch)
            internal_to_external_ac: Internal to external AC bus number mapping
            dummy_ac_indices: Bus numbers assigned to AC buses which have the same
                number as a DC bus but no physical connection (converter outages
                or DC buses without AC grid connection)
            busdc: Updated DC bus matrix with internal AC bus numbering
            bus: Updated AC bus matrix with internal bus numbering
            gen: Updated generator matrix with internal bus numbering
            branch: Updated AC branch matrix with internal bus numbering
    """
    # Define named indices
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()

    # Find AC buses with converter connections
    ac_converter_indices = np.where(busdc[:, BUSAC_I] != 0)[0]
    ac_converter_buses = busdc[ac_converter_indices, BUSAC_I].astype(int)

    # Find DC buses without AC converter connections (dummy buses needed)
    dummy_ac_indices = np.where(busdc[:, BUSAC_I] == 0)[0]

    # Find AC buses without converter connections
    all_ac_buses = bus[:, BUS_I].astype(int)
    ac_no_converter = np.setdiff1d(all_ac_buses, ac_converter_buses)

    # Assign dummy AC buses (take first N buses from ac_no_converter)
    num_dummy = len(dummy_ac_indices)
    dummy_ac_buses = ac_no_converter[:num_dummy]
    ac_no_dummy = ac_no_converter[num_dummy:]

    # Check for multiple converters on same AC bus
    if len(ac_converter_buses) != len(np.unique(ac_converter_buses)):
        raise ValueError('More than one converter per AC node detected!')

    # Define internal to external mapping
    internal_to_external_ac = np.zeros(len(bus), dtype=int)
    internal_to_external_ac[ac_converter_indices] = ac_converter_buses
    internal_to_external_ac[dummy_ac_indices] = dummy_ac_buses
    internal_to_external_ac[busdc.shape[0]:] = ac_no_dummy

    # Create external to internal mapping
    max_bus_num = int(np.max(internal_to_external_ac))
    external_to_internal_ac = np.zeros(max_bus_num + 1, dtype=int)
    external_to_internal_ac[internal_to_external_ac] = np.arange(1, len(bus) + 1)

    # Add dummy AC buses to busdc matrix
    busdc[dummy_ac_indices, BUSAC_I] = dummy_ac_buses

    # Rename AC buses to internal numbering
    busdc[:, BUSAC_I] = external_to_internal_ac[busdc[:, BUSAC_I].astype(int)]
    bus[:, BUS_I] = external_to_internal_ac[bus[:, BUS_I].astype(int)]
    gen[:, GEN_BUS] = external_to_internal_ac[gen[:, GEN_BUS].astype(int)]
    branch[:, F_BUS] = external_to_internal_ac[branch[:, F_BUS].astype(int)]
    branch[:, T_BUS] = external_to_internal_ac[branch[:, T_BUS].astype(int)]

    return internal_to_external_ac, dummy_ac_indices, busdc, bus, gen, branch


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack
    from Cases.PowerFlowAC.case5_stagg import case5_stagg

    print("Testing ext2intac function:")

    # Load test cases
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()
    baseMVA, bus, gen, branch = case5_stagg()

    print(f"\nOriginal AC bus numbers: {bus[:, BUS_I]}")
    print(f"Original DC bus AC connections: {busdc[:, 1]}")
    print(f"\nOriginal generator buses: {gen[:, GEN_BUS]}")
    print(f"Original branch connections:")
    for i in range(min(5, branch.shape[0])):
        print(f"  Branch {i}: {int(branch[i, F_BUS])} -> {int(branch[i, T_BUS])}")

    # Simulate a converter outage
    busdc_test = busdc.copy()
    busdc_test[1, 1] = 0  # Remove AC connection from DC bus 2
    print(f"\nAfter removing AC connection from DC bus 2:")
    print(f"DC bus AC connections: {busdc_test[:, 1]}")

    # Convert to internal numbering
    internal_to_external_ac, dummy_ac_indices, busdc_int, bus_int, gen_int, branch_int = \
        ext2intac(busdc_test.copy(), bus.copy(), gen.copy(), branch.copy())

    print(f"\n--- After conversion to internal numbering ---")
    print(f"\nInternal to external AC mapping: {internal_to_external_ac}")
    print(f"Dummy AC bus indices (in DC bus matrix): {dummy_ac_indices}")
    print(f"\nNew AC bus numbers: {bus_int[:, BUS_I]}")
    print(f"New DC bus AC connections: {busdc_int[:, 1]}")
    print(f"\nNew generator buses: {gen_int[:, GEN_BUS]}")
    print(f"New branch connections:")
    for i in range(min(5, branch_int.shape[0])):
        print(f"  Branch {i}: {int(branch_int[i, F_BUS])} -> {int(branch_int[i, T_BUS])}")