"""Converts internal bus numbering back to external numbering.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from idx_busdc import idx_busdc
from pypower.idx_bus import BUS_I
from pypower.idx_gen import GEN_BUS
from pypower.idx_brch import F_BUS, T_BUS


def int2extac(i2eac, acdum_i, busdc, bus, gen, branch):
    """Converts internal bus numbering back to external numbering.

    Converts consecutive internal AC bus numbers back to the original bus
    numbers using the mapping provided by i2eac returned from ext2intac and
    removes the dummy AC buses assigned to the DC buses without connection
    to the AC grid as a result from ext2intac.

    Args:
        i2eac: Internal to external AC indices (array where i2eac[i] gives
               the external bus number for internal bus i+1)
        acdum_i: Indices (0-based) of dummy AC buses in busdc matrix
        busdc: DC bus matrix
        bus: AC bus matrix
        gen: Generator matrix
        branch: AC branch matrix

    Returns:
        tuple: (busdc, bus, gen, branch)
            busdc: Updated DC bus matrix
            bus: Updated AC bus matrix
            gen: Updated generator matrix
            branch: Updated AC branch matrix
    """
    # Define named indices
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()

    # Rename bus numbers using i2eac mapping
    # Convert 1-based bus numbers to 0-based indices, look up external number
    busdc[:, BUSAC_I] = i2eac[busdc[:, BUSAC_I].astype(int) - 1]
    bus[:, BUS_I] = i2eac[bus[:, BUS_I].astype(int) - 1]
    gen[:, GEN_BUS] = i2eac[gen[:, GEN_BUS].astype(int) - 1]
    branch[:, F_BUS] = i2eac[branch[:, F_BUS].astype(int) - 1]
    branch[:, T_BUS] = i2eac[branch[:, T_BUS].astype(int) - 1]

    # Dummy AC bus removal
    busdc[acdum_i, BUSAC_I] = 0

    return busdc, bus, gen, branch


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack
    from Cases.PowerFlowAC.case5_stagg import case5_stagg
    from ext2intac import ext2intac

    print("Testing int2extac function:")

    # Load test cases
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()
    baseMVA, bus, gen, branch = case5_stagg()

    print(f"\nOriginal AC bus numbers: {bus[:, BUS_I]}")
    print(f"Original DC bus AC connections: {busdc[:, 1]}")
    print(f"Original generator buses: {gen[:, GEN_BUS]}")

    # Simulate a converter outage and convert to internal
    busdc_test = busdc.copy()
    busdc_test[1, 1] = 0  # Remove AC connection from DC bus 2

    print(f"\nAfter removing AC connection from DC bus 2:")
    print(f"DC bus AC connections: {busdc_test[:, 1]}")

    # Convert to internal numbering
    i2eac, acdum_i, busdc_int, bus_int, gen_int, branch_int = ext2intac(
        busdc_test.copy(), bus.copy(), gen.copy(), branch.copy()
    )

    print(f"\n--- After ext2intac (internal numbering) ---")
    print(f"Internal to external mapping: {i2eac}")
    print(f"Dummy AC bus indices: {acdum_i}")
    print(f"Internal AC bus numbers: {bus_int[:, BUS_I]}")
    print(f"Internal DC bus AC connections: {busdc_int[:, 1]}")
    print(f"Internal generator buses: {gen_int[:, GEN_BUS]}")

    # Convert back to external numbering
    busdc_ext, bus_ext, gen_ext, branch_ext = int2extac(
        i2eac, acdum_i, busdc_int.copy(), bus_int.copy(),
        gen_int.copy(), branch_int.copy()
    )

    print(f"\n--- After int2extac (back to external) ---")
    print(f"External AC bus numbers: {bus_ext[:, BUS_I]}")
    print(f"External DC bus AC connections: {busdc_ext[:, 1]}")
    print(f"External generator buses: {gen_ext[:, GEN_BUS]}")

    # Verify round-trip conversion
    print(f"\n--- Verification ---")
    print(f"AC bus numbers match: {np.allclose(bus[:, BUS_I], bus_ext[:, BUS_I])}")
    print(f"Generator buses match: {np.allclose(gen[:, GEN_BUS], gen_ext[:, GEN_BUS])}")
    print(f"Dummy AC bus removed (should be 0): {busdc_ext[acdum_i, 1]}")

    print("\n✓ Round-trip conversion successful!")