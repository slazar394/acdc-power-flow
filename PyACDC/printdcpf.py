"""Prints power flow results related to DC network and converters.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc


def printdcpf(busdc, convdc, branchdc):
    """Prints power flow results related to DC network and converters.

    Prints all AC/DC power flow results related to DC grid and converters.

    Args:
        busdc: DC bus matrix
        convdc: DC converter matrix
        branchdc: DC branch matrix
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

    # Define other numbers and indices
    nconv = convdc.shape[0]
    nbusdc = busdc.shape[0]

    # DC bus data
    print('\n' + '=' * 80)
    print('|     DC bus data                                                              |')
    print('=' * 80)
    print(' Bus   Bus   Voltage    Power')
    print(' DC #  AC #  Mag(pu)    P (MW)')
    print('-----  ----  ---------  --------')

    for i in range(nbusdc):
        if busdc[i, BUSAC_I] == 0:
            print(f'{int(busdc[i, BUSDC_I]):4d}     -  {busdc[i, VDC]:9.3f}  '
                  f'{busdc[i, PDC]:9.3f}')
        else:
            print(f'{int(busdc[i, BUSDC_I]):4d}  {int(busdc[i, BUSAC_I]):4d}  '
                  f'{busdc[i, VDC]:9.3f}  {busdc[i, PDC]:9.3f}')
    print()

    # Transformer losses
    Plosstf = np.abs(convdc[:, PFIL] - convdc[:, PCONV])
    Qlosstf = np.abs(convdc[:, QCONVF] - convdc[:, QCONV])

    # Reactor losses
    Plossc = np.abs(convdc[:, PCCONV] - convdc[:, PFIL])
    Qlossc = np.abs(convdc[:, QCCONV] - convdc[:, QCCONVF])

    # Converter data - total losses
    Plosstot = Plosstf + Plossc + convdc[:, PCLOSS]

    # Filter reactive power
    Qfilt = convdc[:, QCCONVF] - convdc[:, QCONVF]

    print('\n' + '=' * 80)
    print('|     VSC Converter Data                                                       |')
    print('=' * 80)
    print(' Bus     Bus injection           Converter Voltage                 Total loss')
    print(' DC#   P (MW)   Q (MVAr)         Mag(pu) Ang(deg)                    P (MW)')
    print('-----  -------  --------         ------- --------                  -----------')

    for i in range(nconv):
        print(f'{int(convdc[i, CONV_BUS]):4d}  {convdc[i, PCONV]:7.2f}  '
              f'{convdc[i, QCONV]:8.2f}         {convdc[i, VMC]:7.3f}  '
              f'{convdc[i, VAC]:8.3f}                  {Plosstot[i]:9.2f}')

    print('                                                                      ------')
    print(f'                                                           Total: {np.sum(Plosstot):9.2f}')
    print()

    print(' Bus  Converter power   Filter   Transfo loss     Reactor loss    Converter loss')
    print(' DC#  P (MW) Q (MVAr)  Q (MVAr)  P (MW) Q (MVAr)  P (MW) Q (MVAr)    P (MW)')
    print('----- ------- -------  --------  ------ --------  ------ -------- --------------')

    for i in range(nconv):
        print(f'{int(convdc[i, CONV_BUS]):4d}  {convdc[i, PCCONV]:7.2f}  '
              f'{convdc[i, QCCONV]:7.2f}  {Qfilt[i]:7.2f}  {Plosstf[i]:7.2f}  '
              f'{Qlosstf[i]:7.2f}  {Plossc[i]:7.2f}  {Qlossc[i]:7.2f}      '
              f'{convdc[i, PCLOSS]:7.2f}')

    print('                                 ------ --------  ------ -------- --------------')
    print(f'                      Total: {np.sum(Plosstf):9.2f}  '
          f'{np.sum(Qlosstf):7.2f}  {np.sum(Plossc):7.2f}  '
          f'{np.sum(Qlossc):7.2f}      {np.sum(convdc[:, PCLOSS]):7.2f}')
    print()

    print(' Bus  Grid power       Traf Filt.Power  Filter    Conv Filt. Pwr   Converter Power')
    print(' DC#  P (MW) Q (MVAr)  P (MW) Q (MVAr)  Q (MVAr)  Q (MVAr)         P (MW) Q (MVAr)')
    print('----- ------ --------  ------ --------  --------  --------------   ------ --------')

    for i in range(nconv):
        print(f'{int(convdc[i, CONV_BUS]):4d}  {convdc[i, PCONV]:7.2f}  '
              f'{convdc[i, QCONV]:7.2f}  {convdc[i, PFIL]:7.2f}  '
              f'{convdc[i, QCONVF]:8.2f}  {convdc[i, QCCONVF] - convdc[i, QCONVF]:7.2f}  '
              f'{convdc[i, QCCONVF]:10.2f}        {convdc[i, PCCONV]:7.2f}  '
              f'{convdc[i, QCCONV]:7.2f}')

    # DC branch data
    nbranch = branchdc.shape[0]

    P_max = np.maximum(np.abs(branchdc[:, PFDC]), np.abs(branchdc[:, PTDC]))
    P_min = np.minimum(np.abs(branchdc[:, PFDC]), np.abs(branchdc[:, PTDC]))
    Plossline = P_max - P_min

    print('\n' + '=' * 80)
    print('|     DC branch data                                                           |')
    print('=' * 80)
    print('Brnch   From   To     From Bus    To Bus      Loss')
    print('  #     Bus    Bus    P (MW)      P (MW)      P (MW)')
    print('-----  -----  -----  --------    --------    --------')

    for i in range(nbranch):
        print(f'{i + 1:4d}  {int(branchdc[i, F_BUSDC]):5d}  '
              f'{int(branchdc[i, T_BUSDC]):5d}  {branchdc[i, PFDC]:8.2f}    '
              f'{branchdc[i, PTDC]:8.2f}    {Plossline[i]:8.2f}')

    print('                                             --------')
    print(f'                                 Total: {np.sum(Plossline):12.2f}')
    print()
    print()
