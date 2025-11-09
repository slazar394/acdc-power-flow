def idx_brchdc():
    """Defines constants for named column indices to dc branch matrix.

    Returns:
        tuple: (F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B,
                RATEDC_C, BRDC_STATUS, PFDC, PTDC)

    Example usage:
        F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()
        Ploss = branchdc[:, PFDC] + branchdc[:, PTDC]  # compute real power loss vector

    Column definitions:
     1  F_BUSDC     f, from bus number
     2  T_BUSDC     t, to bus number
     3  BRDC_R      r, resistance (p.u.)
     4  BRDC_L      l, inductance (p.u./s) (not used in power flow)
     5  BRDC_C      c, total line charging capacity (p.u.*s) (not used in power flow)
     6  RATEDC_A    rateA, MVA rating A (long term rating)
     7  RATEDC_B    rateB, MVA rating B (short term rating)
     8  RATEDC_C    rateC, MVA rating C (emergency rating)
     9  BRDC_STATUS initial branch status, 1 - in service, 0 - out of service
    10  PFDC        real power injected at "from" bus end (MW)
    11  PTDC        real power injected at "to" bus end (MW)

    MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
    Converted from MATLAB to Python by Lazar Scekic
    """
    F_BUSDC = 0
    T_BUSDC = 1
    BRDC_R = 2
    BRDC_L = 3
    BRDC_C = 4
    RATEDC_A = 5
    RATEDC_B = 6
    RATEDC_C = 7
    BRDC_STATUS = 8
    PFDC = 9
    PTDC = 10

    return F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC


if __name__ == "__main__":
    # Call the function
    F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()

    # Print the results
    print("DC Branch Column Indices:")
    print(f"F_BUSDC = {F_BUSDC}")
    print(f"T_BUSDC = {T_BUSDC}")
    print(f"BRDC_R = {BRDC_R}")
    print(f"BRDC_L = {BRDC_L}")
    print(f"BRDC_C = {BRDC_C}")
    print(f"RATEDC_A = {RATEDC_A}")
    print(f"RATEDC_B = {RATEDC_B}")
    print(f"RATEDC_C = {RATEDC_C}")
    print(f"BRDC_STATUS = {BRDC_STATUS}")
    print(f"PFDC = {PFDC}")
    print(f"PTDC = {PTDC}")