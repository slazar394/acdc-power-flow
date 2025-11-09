"""Check for converter operation within AC voltage and current limits.

MatACDC - Copyright (C) 2011 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np


def convlim(Ss, Vs, Vc, Ztf, Bf, Zc, Icmax, Vcmax, Vcmin, convi, epslim, printopt):
    """Check converter operation within AC voltage and current limits.

    Converter operation checked with the converter's PQ capability diagram
    that are calculated based on the converter limits and grid operation state.

    Args:
        Ss: Grid side complex power
        Vs: Grid side complex voltage
        Vc: Converter side complex voltage
        Ztf: Complex transformer impedance
        Bf: Filter susceptance
        Zc: Complex phase reactor
        Icmax: Maximum converter current
        Vcmax: Maximum converter voltage
        Vcmin: Minimum converter voltage
        convi: Converter number
        epslim: Limit value for allowed differences when a converter limit is exceeded
        printopt: Print option (0=no print, 1=print results)

    Returns:
        tuple: (convlimviol, Ss, plotarg)
            convlimviol: Converter violation flag
                0 = no violation
                1 = converter reactive power violation
                2 = converter active power violation
            Ss: Updated converter grid injection (within limits)
            plotarg: Arguments for converter limit plot
    """
    fd = 1  # File descriptor (stdout)

    # Voltage limits order check
    if Vcmax < Vcmin:
        raise ValueError(f'Vcmin is larger than Vcmax for converter {convi}.')
    elif Vcmax == Vcmin:
        raise ValueError(f'Vcmin is equal to Vcmax for converter {convi}.')

    Ssold = Ss

    # Define voltage magnitudes, angles, powers
    Vsm = np.abs(Vs)
    Vsa = np.angle(Vs)
    Vcm = np.abs(Vc)
    Vca = np.angle(Vc)
    Ps = np.real(Ss)
    Qs = np.imag(Ss)

    # Initialization - load existing parameters
    Zf = 1.0 / (1j * Bf)
    Ytf = 1.0 / (Ztf + np.finfo(float).eps)  # Avoid division by zero
    Yf = 1j * Bf
    Yc = 1.0 / Zc

    # Pi-equivalent parameters of the converter station (voltage limits)
    # Implementation based on:
    # J. Beerten, S. Cole and R. Belmans: "Generalized Steady-State VSC MTDC
    # Model for Sequential AC/DC Power Flow Algorithms", IEEE Trans. Pow.
    # Syst., vol. 27, no. 2, 2012, pp. 821 - 829.

    if Ztf != 0 and Bf != 0:
        Z1 = (Ztf * Zc + Zc * Zf + Zf * Ztf) / Zc
        Z2 = (Ztf * Zc + Zc * Zf + Zf * Ztf) / Zf
    elif Ztf == 0 and Bf != 0:
        Z1 = Zf
        Z2 = Zc
    elif Ztf != 0 and Bf == 0:
        Z1 = np.inf
        Z2 = Ztf + Zc
    else:  # Ztf == 0 and Bf == 0
        Z1 = np.inf
        Z2 = Zc

    Y1 = 1.0 / Z1
    Y2 = 1.0 / Z2
    G2 = np.real(Y2)
    B2 = np.imag(Y2)
    Y12 = Y1 + Y2
    G12 = np.real(Y12)
    B12 = np.imag(Y12)

    # Voltage and current limit parameters
    # Maximum current limit circle parameters
    if Bf != 0:
        MPL1 = -Vsm ** 2 * (1.0 / (np.conj(Zf) + np.conj(Ztf)))
    else:
        MPL1 = 0.0 + 0.0j

    if Ztf != 0:
        rL1 = Vsm * Icmax * np.abs(np.conj(Ytf) / (np.conj(Yf) + np.conj(Ytf)))
    else:
        rL1 = Vsm * Icmax

    # Maximum and minimal active power on current limit
    PmaxL1 = np.real(MPL1) + rL1
    PminL1 = np.real(MPL1) - rL1
    QPmaxL1 = np.imag(MPL1)
    QPminL1 = np.imag(MPL1)

    # Minimum and maximum voltage limit circle parameters
    MPL2 = -Vsm ** 2 * np.conj(Y1 + Y2)
    rL2 = Vsm * np.array([Vcmin, Vcmax]) * np.abs(Y2)

    # Voltage limit compliance of min/max active power point
    # Find intersection points of Vcmin/Vcmax and current limit circles
    dL12 = np.sqrt((np.real(MPL2) - np.real(MPL1)) ** 2 + (np.imag(MPL2) - np.imag(MPL1)) ** 2)
    alpha = np.arctan2((np.imag(MPL2) - np.imag(MPL1)), (np.real(MPL2) - np.real(MPL1)))
    beta = np.arccos(((dL12 ** 2 + rL1 ** 2) * np.ones(2) - rL2 ** 2) / (2 * dL12 * rL1))
    delta = np.arccos(((dL12 ** 2 - rL1 ** 2) * np.ones(2) + rL2 ** 2) / (2 * dL12 * rL2))
    gamma = np.array([alpha - beta[0], np.pi - alpha - beta[1]])
    eta = np.array([alpha + delta[0], alpha - delta[1]])

    # Possible intersection points (current limit)
    x1 = np.zeros((2, 2))
    y1 = np.zeros((2, 2))
    x1[0, :] = np.real(MPL1) + rL1 * np.cos(gamma)
    x1[1, :] = np.real(MPL1) - rL1 * np.cos(gamma)
    y1[0, :] = np.imag(MPL1) + rL1 * np.sin(gamma)
    y1[1, :] = np.imag(MPL1) - rL1 * np.sin(gamma)

    # Possible intersection points (voltage limits)
    x2 = np.zeros((2, 2))
    y2 = np.zeros((2, 2))
    x2[0, :] = np.real(MPL2) + rL2 * np.cos(eta)
    x2[1, :] = np.real(MPL2) - rL2 * np.cos(eta)
    y2[0, :] = np.imag(MPL2) + rL2 * np.sin(eta)
    y2[1, :] = np.imag(MPL2) - rL2 * np.sin(eta)

    # Vectorize intersection point matrices
    x1v = x1.flatten('F')  # Fortran-style (column-major) flattening
    x2v = x2.flatten('F')
    y1v = y1.flatten('F')
    y2v = y2.flatten('F')

    # Decrease accuracy to detect the intersection points
    eps2 = 1e-8
    x1r = np.round(x1v / eps2) * eps2
    x2r = np.round(x2v / eps2) * eps2
    y1r = np.round(y1v / eps2) * eps2
    y2r = np.round(y2v / eps2) * eps2

    # Corresponding elements in intersection vectors
    x1i = np.where(np.isin(x1r, x2r))[0]
    x2i = np.where(np.isin(x2r, x1r))[0]
    y1i = np.where(np.isin(y1r, y2r))[0]
    y2i = np.where(np.isin(y2r, y1r))[0]

    # Sort by indices
    x12r1 = np.column_stack([x1i, x1r[x1i]])
    x12r1 = x12r1[x12r1[:, 0].argsort()]
    x12r2 = np.column_stack([x2i, x2r[x2i]])
    x12r2 = x12r2[x12r2[:, 0].argsort()]
    y12r1 = np.column_stack([y1i, y1r[y1i]])
    y12r1 = y12r1[y12r1[:, 0].argsort()]
    y12r2 = np.column_stack([y2i, y2r[y2i]])
    y12r2 = y12r2[y12r2[:, 0].argsort()]

    # Define intersection points (full accuracy)
    VcminPQ1 = x1v[int(x12r1[0, 0])] + 1j * y1v[int(y12r1[0, 0])]
    VcminPQ2 = x1v[int(x12r1[2, 0])] + 1j * y1v[int(y12r1[2, 0])]
    VcmaxPQ1 = x1v[int(x12r1[1, 0])] + 1j * y1v[int(y12r1[1, 0])]
    VcmaxPQ2 = x1v[int(x12r1[3, 0])] + 1j * y1v[int(y12r1[3, 0])]

    # Remove imaginary intersection points (no intersections, due to low/high voltage limits)
    if not np.isreal(x12r2[0, 1]) or not np.isreal(y12r2[0, 1]) or \
            not np.isreal(x12r2[2, 1]) or not np.isreal(y12r2[2, 1]):
        VcminPQ1 = None
        VcminPQ2 = None
        if printopt == 1:
            print(f'\n  Lower voltage limit at converter {convi}: No intersections with current limit were found.')

    if not np.isreal(x12r2[1, 1]) or not np.isreal(y12r2[1, 1]) or \
            not np.isreal(x12r2[3, 1]) or not np.isreal(y12r2[3, 1]):
        VcmaxPQ1 = None
        VcmaxPQ2 = None
        if printopt == 1:
            print(f'\n  Upper voltage limit at converter {convi}: No intersections with current limit were found.')

    # Define maximum and minimum power points
    Pmin = PminL1
    QPmin = QPminL1
    Pmax = PmaxL1
    QPmax = QPmaxL1

    # Redefine max and min power points if min/max voltage limits are high/low
    if VcminPQ1 is not None or VcminPQ2 is not None:
        if printopt == 1 and (np.imag(VcminPQ1) > QPminL1 or np.imag(VcminPQ2) > QPmaxL1):
            print(f'\n  High lower voltage limit detected at converter {convi}.')
        if VcminPQ1 is not None and np.imag(VcminPQ1) > QPminL1:
            Pmin = np.real(VcminPQ1)
            QPmin = np.imag(VcminPQ1)
        if VcminPQ2 is not None and np.imag(VcminPQ2) > QPmaxL1:
            Pmax = np.real(VcminPQ2)
            QPmax = np.imag(VcminPQ2)

    if VcmaxPQ1 is not None or VcmaxPQ2 is not None:
        if printopt == 1 and (np.imag(VcmaxPQ1) < QPminL1 or np.imag(VcmaxPQ2) < QPmaxL1):
            print(f'\n  Low upper voltage limit detected at converter {convi}.')
        if VcmaxPQ1 is not None and np.imag(VcmaxPQ1) < QPminL1:
            Pmin = np.real(VcmaxPQ1)
            QPmin = np.imag(VcmaxPQ1)
        if VcmaxPQ2 is not None and np.imag(VcmaxPQ2) < QPmaxL1:
            Pmax = np.real(VcmaxPQ2)
            QPmax = np.imag(VcmaxPQ2)

    # Limit check
    if Pmin < Ps < Pmax:
        # Maximum current limit (L1)
        if np.imag(MPL1) < Qs:
            Qs1 = np.imag(MPL1) + np.sqrt(rL1 ** 2 - (Ps - np.real(MPL1)) ** 2)
        else:
            Qs1 = np.imag(MPL1) - np.sqrt(rL1 ** 2 - (Ps - np.real(MPL1)) ** 2)

        # Minimum and maximum voltage limits (L2)
        a = 1 + (B2 / G2) ** 2 * np.ones(2)
        b = -2 * B2 / G2 * (Ps + Vsm ** 2 * G12) / (Vsm * np.array([Vcmin, Vcmax]) * G2)
        c = ((Ps + Vsm ** 2 * G12) / (Vsm * np.array([Vcmin, Vcmax]) * G2)) ** 2 - 1

        # Only positive solution retained (negative solution refers to lower part)
        sinDd = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        Dd = np.arcsin(sinDd)
        cosDd = np.cos(Dd)
        Qs2 = Vsm ** 2 * B12 + Vsm * np.array([Vcmin, Vcmax]) * (G2 * sinDd - B2 * cosDd)

        # Adopt working point to limits
        if Qs > np.imag(MPL1):
            if Qs > min(Qs1, Qs2[1]):
                convlimviol = 1
                Qs = min(Qs1, Qs2[1])
            elif Qs < Qs2[0]:
                convlimviol = 1
                Qs = Qs2[0]
            else:
                convlimviol = 0
        else:  # Qs < imag(MPL1)
            if Qs < max(Qs1, Qs2[0]):
                convlimviol = 1
                Qs = max(Qs1, Qs2[0])
            elif Qs > Qs2[1]:
                convlimviol = 1
                Qs = Qs2[1]
            else:
                convlimviol = 0

    elif Ps <= Pmin:  # Grid injected active power lower than minimum value
        convlimviol = 2
        Ps = Pmin
        Qs = QPmin

    else:  # Ps >= Pmax - Grid injected active power higher than maximum value
        convlimviol = 2
        Ps = Pmax
        Qs = QPmax

    # Define output argument Ss
    Ss = Ps + 1j * Qs

    # Remove violation when difference is small
    if np.abs(Ssold - Ss) < epslim:
        convlimviol = 0

    # Define plot arguments
    if convlimviol == 1:
        SsIcmax = Ps + 1j * Qs1
        SsVcmin = Ps + 1j * Qs2[0]
        SsVcmax = Ps + 1j * Qs2[1]
        plotarg = np.array([convlimviol, Ztf, Zf, Zc, Y1, Y2, Yf, Ytf, Vs, Icmax,
                            Vcmax, Vcmin, Ssold, Ss, SsIcmax, SsVcmax, SsVcmin], dtype=object)
    else:
        plotarg = np.array([convlimviol, Ztf, Zf, Zc, Y1, Y2, Yf, Ytf, Vs, Icmax,
                            Vcmax, Vcmin, Ssold, Ss, 0, 0, 0], dtype=object)

    return convlimviol, Ss, plotarg