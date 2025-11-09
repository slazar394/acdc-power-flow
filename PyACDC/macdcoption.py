"""Used to retrieve a MatACDC options vector.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np

# Option indices (0-based)
TOLACDC = 0  # tolerance ac/dc power flow
ITMAXACDC = 1  # maximum iterations ac/dc power flow
TOLDC = 2  # tolerance dc power flow (Newton's method)
ITMAXDC = 3  # maximum iterations dc power flow (Newton's method)
TOLSLACKDROOP = 4  # tolerance dc slack bus iteration
ITMAXSLACKDROOP = 5  # maximum iterations dc slack bus iteration
TOLSLACKDROOPINT = 6  # tolerance internal slack bus iteration (Newton's method)
ITMAXSLACKDROOPINT = 7  # maximum iterations internal slack bus iteration (Newton's method)
MULTSLACK = 8  # multiple dc slack buses per dc grid
LIMAC = 9  # enforce ac converter limits
LIMDC = 10  # enforce dc converter limits (not implemented)
TOLLIM = 11  # maximum difference between subsequent violations
OUTPUT = 12  # print output
CONVPLOTOPT = 13  # plot converter limit violations


def macdcoption():
    """Returns default MatACDC options vector.

    Returns:
        np.ndarray: Options vector with default values

    Option descriptions:
        idx - NAME                  default   description [options]
        ---   ----------------      -------   ---------------------------------
         0  - TOLACDC               1e-8      tolerance ac/dc power flow
         1  - ITMAXACDC             10        maximum iterations ac/dc power flow
         2  - TOLDC                 1e-8      tolerance dc power flow (Newton's method)
         3  - ITMAXDC               10        maximum iterations dc power flow (Newton's method)
         4  - TOLSLACKDROOP         1e-8      tolerance dc slack bus iteration
         5  - ITMAXSLACKDROOP       10        maximum iterations dc slack bus iteration
         6  - TOLSLACKDROOPINT      1e-8      tolerance internal slack bus iteration (Newton's method)
         7  - ITMAXSLACKDROOPINT    10        maximum iterations internal slack bus iteration (Newton's method)
         8  - MULTSLACK             0         multiple dc slack buses per dc grid
             [0 - only 1 dc voltage controlling per dc grid allowed]
             [1 - more than 1 dc voltage controlling per dc grid allowed]
         9  - LIMAC                 0         enforce ac converter limits
             [0 - do NOT enforce limits]
             [1 - enforce converter current and voltage limits]
        10  - LIMDC                 0         enforce dc converter limits (not implemented)
        11  - TOLLIM                1e-2      maximum difference between subsequent violations
        12  - OUTPUT                1         print output
        13  - CONVPLOTOPT           0         plot converter limit violations
             [0 - do not plot converter limit violations]
             [1 - plot only converter limit violations]
             [2 - plot converter limit violations and end situation]

    Example:
        from macdcoption import macdcoption, TOLACDC, ITMAXACDC
        options = macdcoption()
        options[TOLACDC] = 1e-6        # Change tolerance
        options[ITMAXACDC] = 20        # Change max iterations
    """
    options = np.array([
        1e-8,  # tolerance ac/dc power flow
        10,  # maximum iterations ac/dc power flow
        1e-8,  # tolerance dc power flow (Newton's method)
        10,  # maximum iterations dc power flow (Newton's method)
        1e-8,  # tolerance slack/droop bus iteration
        10,  # maximum iterations slack/droop bus iteration
        1e-8,  # tolerance internal slack/droop bus iteration (Newton's method)
        10,  # maximum iterations internal slack/droop bus iteration (Newton's method)
        0,  # multiple dc slack buses per dc grid allowed
        0,  # ac limits converters enabled
        0,  # dc limits converters enabled (not implemented)
        1e-2,  # maximum error between subsequent limit violations
        1,  # print output
        0,  # plot converter station limit violations
    ])

    return options


if __name__ == "__main__":
    options = macdcoption()

    print("MatACDC Default Options:")
    print(f"TOLACDC (idx {TOLACDC}): {options[TOLACDC]}")
    print(f"ITMAXACDC (idx {ITMAXACDC}): {options[ITMAXACDC]}")
    print(f"TOLDC (idx {TOLDC}): {options[TOLDC]}")
    print(f"ITMAXDC (idx {ITMAXDC}): {options[ITMAXDC]}")
    print(f"TOLSLACKDROOP (idx {TOLSLACKDROOP}): {options[TOLSLACKDROOP]}")
    print(f"ITMAXSLACKDROOP (idx {ITMAXSLACKDROOP}): {options[ITMAXSLACKDROOP]}")
    print(f"TOLSLACKDROOPINT (idx {TOLSLACKDROOPINT}): {options[TOLSLACKDROOPINT]}")
    print(f"ITMAXSLACKDROOPINT (idx {ITMAXSLACKDROOPINT}): {options[ITMAXSLACKDROOPINT]}")
    print(f"MULTSLACK (idx {MULTSLACK}): {options[MULTSLACK]}")
    print(f"LIMAC (idx {LIMAC}): {options[LIMAC]}")
    print(f"LIMDC (idx {LIMDC}): {options[LIMDC]}")
    print(f"TOLLIM (idx {TOLLIM}): {options[TOLLIM]}")
    print(f"OUTPUT (idx {OUTPUT}): {options[OUTPUT]}")
    print(f"CONVPLOTOPT (idx {CONVPLOTOPT}): {options[CONVPLOTOPT]}")

    print("\nModifying options:")
    options[TOLACDC] = 1e-6
    options[ITMAXACDC] = 20
    print(f"New TOLACDC: {options[TOLACDC]}")
    print(f"New ITMAXACDC: {options[ITMAXACDC]}")