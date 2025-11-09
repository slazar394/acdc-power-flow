def idx_busdc():
    """Defines constants for named column indices to DC bus matrix.

    Returns:
        tuple: (BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC)

    Example usage:
        BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()
        Pd = busdc[3, PDC]        # get DC power withdrawal from DC grid at DC bus with index 4
        busdc[:, VDCMIN] = 0.95   # set minimum voltage magnitude to 0.95 at all DC buses

    Column definitions:
     1  BUSDC_I     DC bus number
     2  BUSAC_I     AC bus number (0 indicates no AC bus connection)
     3  GRIDDC      DC grid to which the BUSDC_I is connected
     4  PDC         power withdrawn from the DC grid (MW)
     5  VDC         DC voltage (p.u.)
     6  BASE_KVDC   base DC voltage (kV)
     7  VDCMAX      max DC voltage (p.u.)
     8  VDCMIN      min DC voltage (p.u.)
     9  CDC         DC bus capacitor size (p.u.) (not used in power flow)

    MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
    Converted from MATLAB to Python by Lazar Scekic
    """
    BUSDC_I = 0
    BUSAC_I = 1
    GRIDDC = 2
    PDC = 3
    VDC = 4
    BASE_KVDC = 5
    VDCMAX = 6
    VDCMIN = 7
    CDC = 8

    return BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC


if __name__ == '__main__':
    # Call the function
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()

    # Print the results
    print("DC Bus Column Indices:")
    print(f"BUSDC_I = {BUSDC_I}")
    print(f"BUSAC_I = {BUSAC_I}")
    print(f"GRIDDC = {GRIDDC}")
    print(f"PDC = {PDC}")
    print(f"VDC = {VDC}")
    print(f"BASE_KVDC = {BASE_KVDC}")
    print(f"VDCMAX = {VDCMAX}")
    print(f"VDCMIN = {VDCMIN}")
    print(f"CDC = {CDC}")
