"""case 3 nodes - data for system with 3 zones consisting of 3 infinite buses.

Can be used together with dc case files "case5_stagg_....py"

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""

def case3_inf():
    """Returns power flow data for 3 infinite bus system.
    
    Returns:
        tuple: (baseMVA, bus, gen, branch)
    """
    import numpy as np

    baseMVA = 100
    
    # bus data
    # bus_i  type  Pd  Qd  Gs  Bs  area  Vm    Va  baseKV  zone  Vmax  Vmin
    bus = np.array([
        [2,  np.inf,  0,  0,  0,  0,  1,  1.06,  0,  345,  1,  1.1,  0.9],
        [3,  np.inf,  0,  0,  0,  0,  1,  1,     0,  345,  2,  1.1,  0.9],
        [5,  np.inf,  0,  0,  0,  0,  1,  1,     0,  345,  3,  1.1,  0.9],
    ])
    
    gen = np.zeros((0, 10))
    branch = np.zeros((0, 11))
    
    return baseMVA, bus, gen, branch
