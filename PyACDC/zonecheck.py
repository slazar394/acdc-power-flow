"""Check for non-synchronized AC zones.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from pypower.idx_bus import PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, \
    BUS_AREA, VM, VA, BASE_KV, ZONE, VMAX, VMIN, LAM_P, LAM_Q, MU_VMAX, MU_VMIN
from pypower.idx_gen import GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, \
    PMAX, PMIN, MU_PMAX, MU_PMIN, MU_QMAX, MU_QMIN, PC1, PC2, QC1MIN, QC1MAX, \
    QC2MIN, QC2MAX, RAMP_AGC, RAMP_10, RAMP_30, RAMP_Q, APF
from pypower.idx_brch import F_BUS, T_BUS, BR_R, BR_X, BR_B, RATE_A, RATE_B, \
    RATE_C, TAP, SHIFT, BR_STATUS, PF, QF, PT, QT, MU_SF, MU_ST, ANGMIN, \
    ANGMAX, MU_ANGMIN, MU_ANGMAX


def zonecheck(bus, gen, branch, i2eac, output=True):
    """Check for non-synchronized AC zones.

    Check for non-synchronized AC zones. If present, the presence of one
    and only one slack bus is checked, as well as the presence of AC
    connections between the zones, in which case an error message is displayed.

    Args:
        bus: AC bus matrix
        gen: Generator matrix
        branch: AC branch matrix
        i2eac: Internal to external AC indices
        output: Print output flag (default: True)

    Raises:
        ValueError: If zone configuration is invalid
    """
    # Get unique AC zones
    aczones = np.sort(np.unique(bus[:, ZONE]))

    if len(aczones) > 1:
        if output:
            print(f'\nNon-synchronised zones: {len(aczones)} AC zones detected.')

    # Check interzonal connections
    branchzone = np.column_stack([
        bus[branch[:, F_BUS].astype(int) - 1, ZONE],
        bus[branch[:, T_BUS].astype(int) - 1, ZONE]
    ])
    branchconfl = branchzone[:, 0] != branchzone[:, 1]

    if np.sum(branchconfl) != 0:
        brconfl = np.column_stack([
            branch[branchconfl, F_BUS],
            branch[branchconfl, T_BUS]
        ])
        for i in range(brconfl.shape[0]):
            from_bus = int(i2eac[int(brconfl[i, 0]) - 1])
            to_bus = int(i2eac[int(brconfl[i, 1]) - 1])
            print(f'\nRemove branch between buses {from_bus} and {to_bus}.')
        raise ValueError('Connection between different AC zones detected.')

    # Check for one AC slack bus (with a generator) in every zone
    # Addition to original MATPOWER code to avoid that MATPOWER takes a
    # voltage controlling converter (dummy generator) and uses it as an AC
    # slack bus when there is no generator present.
    acslack = np.where(bus[:, BUS_TYPE] == REF)[0]
    acslackz = np.sort(bus[acslack, ZONE])
    acinf = np.where(bus[:, BUS_TYPE] == np.inf)[0]
    acinfz = np.sort(bus[acinf, ZONE])
    nogenslack = np.setdiff1d(acslack + 1, gen[:, GEN_BUS].astype(int)) - 1  # Convert to 0-based

    if len(acslackz) != len(aczones):
        # AC zones without slack bus
        if len(acslackz) < len(aczones):
            zone_noslack = np.setdiff1d(aczones, acslackz)
            zone_noslack_noinf = np.setdiff1d(zone_noslack, acinfz)
            if len(zone_noslack_noinf) > 0:
                for zone in zone_noslack_noinf:
                    print(f'\nNo AC slack bus detected in AC zone {int(zone)}.')
                raise ValueError('Define an AC slack bus for every non-synchronized zone!')

        # Multiple slack buses in AC zone
        elif len(acslackz) > len(aczones):
            acslackzs = np.sort(acslackz)
            multslack = acslackzs[acslackzs == np.roll(acslackzs, 1)]
            if len(multslack) > 0:
                for zone in np.unique(multslack):
                    print(f'\nMultiple AC slack bus detected in AC zone {int(zone)}.')
                raise ValueError('Reduce number of AC slack buses to 1 for every non-synchronized zone!')

    else:  # len(acslackz) == len(aczones)
        # Check for multiple AC slack buses in one zone and inf bus zones
        if len(acinf) > 0:
            acslackzs = np.sort(acslackz)
            multslack = acslackzs[acslackzs == np.roll(acslackzs, 1)]
            if len(multslack) > 1:
                for zone in np.unique(multslack):
                    print(f'\nMultiple AC slack bus detected in AC zone {int(zone)}.')
                raise ValueError('Reduce number of AC slack buses to 1 for every non-synchronized zone!')

    # Check for a generator for every slack bus
    if len(nogenslack) > 0:
        for bus_idx in nogenslack:
            bus_num = int(i2eac[bus_idx])
            print(f'\nAC slack bus without generator at bus {bus_num}.')
        raise ValueError('Add a generator for every AC slack bus!')

    # Check for connections to infinite buses
    fbusinf = np.intersect1d(branch[:, F_BUS].astype(int) - 1, acinf)
    tbusinf = np.intersect1d(branch[:, T_BUS].astype(int) - 1, acinf)
    brchinf = np.concatenate([fbusinf, tbusinf])

    if len(brchinf) > 0:
        for bus_idx in brchinf:
            bus_num = int(i2eac[bus_idx])
            print(f'\nConnection with an infinite bus at bus {bus_num}.')
        raise ValueError('Remove connections to infinite buses!')

    # Check for one infinite bus in every zone (without other buses)
    busi = bus[:, BUS_I].astype(int) - 1  # 0-based bus indices
    acninf = np.setdiff1d(busi, acinf)
    acninfz = np.sort(bus[acninf, ZONE])
    conflinfz = np.intersect1d(acinfz, acninfz)

    if len(conflinfz) > 0:
        for zone in conflinfz:
            print(f'\nInfinite buses and regular buses detected in zone {int(zone)}.')
        raise ValueError('Remove infinite or regular buses!')

    # Check for multiple infinite buses in 1 AC zone
    if len(acinfz) > 0:
        multinf = acinfz[acinfz == np.roll(acinfz, 1)]
        if len(multinf) > 1:
            for zone in np.unique(multinf):
                print(f'\nMultiple infinite buses detected in AC zone {int(zone)}.')
            raise ValueError('Reduce number of infinite buses to 1 for every non-synchronized zone!')


if __name__ == "__main__":
    from Cases.PowerFlowAC.case5_stagg import case5_stagg

    print("Testing zonecheck function:")

    # Load test case
    baseMVA, bus, gen, branch = case5_stagg()

    # Create i2eac mapping (identity for this test)
    i2eac = bus[:, BUS_I].astype(int)

    print("\n=== Test Case 1: Single zone (valid) ===")
    print(f"Zones in system: {np.unique(bus[:, ZONE])}")
    print(f"Number of slack buses: {np.sum(bus[:, BUS_TYPE] == REF)}")

    try:
        zonecheck(bus, gen, branch, i2eac, output=True)
        print("✓ Zone check passed!")
    except ValueError as e:
        print(f"✗ Zone check failed: {e}")

    print("\n=== Test Case 2: Missing slack bus (invalid) ===")
    bus_test = bus.copy()
    # Change slack bus to PV
    slack_idx = np.where(bus_test[:, BUS_TYPE] == REF)[0][0]
    bus_test[slack_idx, BUS_TYPE] = PV

    try:
        zonecheck(bus_test, gen, branch, i2eac, output=True)
        print("✓ Zone check passed!")
    except ValueError as e:
        print(f"✗ Zone check failed (expected): {e}")

    print("\n=== Test Case 3: Multiple zones ===")
    bus_test2 = bus.copy()
    # Create a second zone
    bus_test2[3:, ZONE] = 2
    # Add slack bus for zone 2
    bus_test2[3, BUS_TYPE] = REF
    gen_test2 = gen.copy()
    # Add generator at new slack bus
    new_gen = gen_test2[0].copy()
    new_gen[GEN_BUS] = bus_test2[3, BUS_I]
    gen_test2 = np.vstack([gen_test2, new_gen])

    # Remove any branches between zones
    branch_test2 = branch.copy()
    zone_from = bus_test2[branch_test2[:, F_BUS].astype(int) - 1, ZONE]
    zone_to = bus_test2[branch_test2[:, T_BUS].astype(int) - 1, ZONE]
    same_zone = zone_from == zone_to
    branch_test2 = branch_test2[same_zone]

    try:
        zonecheck(bus_test2, gen_test2, branch_test2, i2eac, output=True)
        print("✓ Zone check passed!")
    except ValueError as e:
        print(f"✗ Zone check failed: {e}")