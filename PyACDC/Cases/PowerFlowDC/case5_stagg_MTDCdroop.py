"""dc case 3 nodes - dc power flow data for 3 node system

3 node system (voltage droop controlled) can be used together with 
ac case files 'case5_stagg.py' and 'case3_inf.py'

Network data based on:
J. Beerten, D. Van Hertem, R. Belmans, "VSC MTDC systems with a 
distributed DC voltage control – a power flow approach", in IEEE 
Powertech2011, Trondheim, Norway, Jun 2011.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""


def case5_stagg_MTDCdroop():
    """Returns dc power flow data for 3 node MTDC system with droop control.
    
    Returns:
        tuple: (baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc)
    """
    import numpy as np

    baseMVAac = 100
    baseMVAdc = 100
    pol = 2  # numbers of poles (1=monopolar grid, 2=bipolar grid)
    
    # bus data
    # busdc_i  busac_i  grid  Pdc  Vdc  basekVdc  Vdcmax  Vdcmin  Cdc
    busdc = np.array([
        [1,  2,  1,  0,  1,  345,  1.1,  0.9,  0],
        [2,  3,  1,  0,  1,  345,  1.1,  0.9,  0],
        [3,  5,  1,  0,  1,  345,  1.1,  0.9,  0],
    ])
    
    # converters
    # busdc_i  type_dc  type_ac  P_g  Q_g  Vtar  rtf     xtf     bf      rc      xc       basekVac  Vmmax  Vmmin  Imax  status  LossA  LossB  LossCrec  LossCinv  droop   Pdcset     Vdcset  dVdcset
    convdc = np.array([
        [1,  3,  1,  -60,  -40,  1,  0.0015,  0.1121,  0.0887,  0.0001,  0.16428,  345,  1.1,  0.9,  1.1,  1,  1.103,  0.887,  2.885,  4.371,  0.0050,  -58.6274,  1.0079,  0],
        [2,  3,  2,    0,    0,  1,  0.0015,  0.1121,  0.0887,  0.0001,  0.16428,  345,  1.1,  0.9,  1.1,  1,  1.103,  0.887,  2.885,  4.371,  0.0070,   21.9013,  1.0000,  0],
        [3,  3,  1,   35,    5,  1,  0.0015,  0.1121,  0.0887,  0.0001,  0.16428,  345,  1.1,  0.9,  1.1,  1,  1.103,  0.887,  2.885,  4.371,  0.0050,   36.1856,  0.9978,  0],
    ])
    
    # branches
    # fbusdc  tbusdc  r      l  c  rateA  rateB  rateC  status
    branchdc = np.array([
        [1,  2,  0.052,  0,  0,  100,  100,  100,  1],
        [2,  3,  0.052,  0,  0,  100,  100,  100,  1],
        [1,  3,  0.073,  0,  0,  100,  100,  100,  1],
    ])
    
    return baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc
