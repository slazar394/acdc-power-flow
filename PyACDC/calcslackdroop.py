"""Internal slack/droop bus power injection iteration.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve


import numpy as np


def calcslackdroop(Pcspec, Qsspec, Vs, Vf, Vc, Ztf, Bf, Zc, tol, itmax):
    """Internal Newton-Raphson iteration for slack/droop bus power injections.

    Internal Newton-Raphson iteration to calculate the slack buses and voltage
    droop controlled buses power injections in the AC grid using the converter
    active power injection and the AC grid state (Vs) and the reactive power
    injection as fixed values.

    Based on:
    J. Beerten, S. Cole and R. Belmans: "Generalized Steady-State VSC MTDC
    Model for Sequential AC/DC Power Flow Algorithms", IEEE Trans. Pow.
    Syst., vol. 27, no. 2, 2012, pp. 821 - 829.

    Args:
        Pcspec: Specified converter active power injection
        Qsspec: Specified grid side reactive power injection
        Vs: Grid side complex voltage
        Vf: Filter complex voltage
        Vc: Converter complex voltage
        Ztf: Converter transformer complex impedance
        Bf: Filter susceptance
        Zc: Phase reactor complex impedance
        tol: Newton's method tolerance
        itmax: Newton's method maximum iterations

    Returns:
        tuple: (Ps, Qc, Vc)
            Ps: Grid side active power injection
            Qc: Converter side reactive power injection
            Vc: Converter complex voltage
    """
    # Initialize
    ng = len(Pcspec)  # Number of slack/droop buses

    # Define matrix indices (0-based)
    i1 = np.arange(ng)
    i2 = np.arange(ng, 2 * ng)
    i3 = np.arange(2 * ng, 3 * ng)
    i4 = np.arange(3 * ng, 4 * ng)

    # Define voltage amplitudes and angles
    Vsm = np.abs(Vs)  # Grid voltage amplitude
    Vsa = np.angle(Vs)  # Grid voltage angle
    Vfm = np.abs(Vf)  # Filter voltage amplitude
    Vfa = np.angle(Vf)  # Filter voltage angle
    Vcm = np.abs(Vc)  # Converter voltage amplitude
    Vca = np.angle(Vc)  # Converter voltage angle

    # Calculate converter admittance
    Yc = 1.0 / Zc
    Gc = np.real(Yc)
    Bc = np.imag(Yc)

    # Determine converters without and with transformers
    tf0i = np.where(Ztf == 0)[0]  # Without transformer
    tf1i = np.where(Ztf != 0)[0]  # With transformer

    # Calculate transformer admittance
    Ytf = np.where(Ztf != 0, 1.0 / (Ztf + np.finfo(float).eps), 0.0)
    Gtf = np.real(Ytf)
    Btf = np.imag(Ytf)

    # Vc slack bus iteration
    it = 0
    converged = False
    cflag = False

    # Newton-Raphson iteration
    while not converged and it < itmax:
        # Update iteration counter
        it += 1

        # Define cos and sin of angles
        cosfc = np.cos(Vfa - Vca)
        sinfc = np.sin(Vfa - Vca)
        cossf = np.cos(Vsa - Vfa)
        sinsf = np.sin(Vsa - Vfa)
        cossc = np.cos(Vsa - Vca)
        sinsc = np.sin(Vsa - Vca)

        # Converter side power
        Pc = Vcm ** 2 * Gc - Vfm * Vcm * (Gc * cosfc - Bc * sinfc)
        Qc = -Vcm ** 2 * Bc + Vfm * Vcm * (Gc * sinfc + Bc * cosfc)

        # Filter side converter power
        Pcf = -Vfm ** 2 * Gc + Vfm * Vcm * (Gc * cosfc + Bc * sinfc)
        Qcf = Vfm ** 2 * Bc + Vfm * Vcm * (Gc * sinfc - Bc * cosfc)

        # Filter reactive power
        Qf = -Bf * Vfm ** 2

        # Filter side grid power
        Psf = Vfm ** 2 * Gtf - Vfm * Vsm * (Gtf * cossf - Btf * sinsf)
        Qsf = -Vfm ** 2 * Btf + Vfm * Vsm * (Gtf * sinsf + Btf * cossf)

        # Grid side power
        Ps = ((-Vsm ** 2 * Gtf + Vfm * Vsm * (Gtf * cossf + Btf * sinsf)) * (Ztf != 0) +
              (-Vsm ** 2 * Gc + Vsm * Vcm * (Gc * cossc + Bc * sinsc)) * (Ztf == 0))

        Qs = ((Vsm ** 2 * Btf + Vfm * Vsm * (Gtf * sinsf - Btf * cossf)) * (Ztf != 0) +
              (Vsm ** 2 * (Bc + Bf) + Vsm * Vcm * (Gc * sinsc - Bc * cossc)) * (Ztf == 0))

        # Additional filter bus equations
        F1 = Pcf - Psf
        F2 = Qcf - Qsf - Qf

        # Mismatch vector
        mismatch = np.concatenate([
            Pcspec - Pc,
            Qsspec - Qs,
            -F1,
            -F2
        ])

        mismatch1 = mismatch - np.concatenate([
            np.zeros(3 * ng),
            mismatch[i4] * (Ztf == 0)
        ])
        mismatch1 = mismatch1 - np.concatenate([
            np.zeros(2 * ng),
            mismatch[i3] * (Ztf == 0),
            np.zeros(ng)
        ])

        if np.max(np.abs(mismatch1)) < tol:
            cflag = True
            break

        # Initialize Jacobian matrix (sparse)
        J = lil_matrix((4 * ng, 4 * ng))

        # Jacobian matrix elements
        J[i1, i1] = np.diag(-Qc - Vcm ** 2 * Bc)  # J11
        J[i1, i2] = np.diag((Qc + Vcm ** 2 * Bc) * (Ztf != 0))  # J12
        J[i1, i3] = np.diag(Pc + Vcm ** 2 * Gc)  # J13
        J[i1, i4] = np.diag((Pc - Vcm ** 2 * Gc) * (Ztf != 0))  # J14

        # Only included without transformer
        J[i2, i1] = np.diag((-Ps - Vsm ** 2 * Gc) * (Ztf == 0))  # J21
        J[i2, i3] = np.diag((Qs - Vsm ** 2 * (Bc + Bf)) * (Ztf == 0))  # J23

        # Only included with transformer
        J[i2, i2] = np.diag((-Ps - Vsm ** 2 * Gtf) * (Ztf != 0))  # J22
        J[i2, i4] = np.diag((Qs - Vsm ** 2 * Btf) * (Ztf != 0))  # J24

        J[i3, i1] = np.diag((Qcf - Vfm ** 2 * Bc) * (Ztf != 0))  # J31
        J[i3, i2] = np.diag((-Qcf + Qsf + Vfm ** 2 * (Bc + Btf)) * (Ztf != 0))  # J32
        J[i3, i3] = np.diag((Pcf + Vfm ** 2 * Gc) * (Ztf != 0))  # J33
        J[i3, i4] = np.diag((Pcf - Psf - Vfm ** 2 * (Gc + Gtf)) * (Ztf != 0))  # J34

        J[i4, i1] = np.diag((-Pcf - Vfm ** 2 * Gc) * (Ztf != 0))  # J41
        J[i4, i2] = np.diag((Pcf - Psf + Vfm ** 2 * (Gc + Gtf)) * (Ztf != 0))  # J42
        J[i4, i3] = np.diag((Qcf - Vfm ** 2 * Bc) * (Ztf != 0))  # J43
        J[i4, i4] = np.diag((Qcf - Qsf + Vfm ** 2 * (Bc + Btf + 2 * Bf)) * (Ztf != 0))  # J44

        # Remove rows and columns of transformerless buses
        rows_to_keep = np.concatenate([i1, i2[tf1i], i3[tf1i], i4[tf1i]])
        cols_to_keep = rows_to_keep

        J_reduced = J[rows_to_keep, :][:, cols_to_keep]
        mismatch_reduced = mismatch[rows_to_keep]

        # Convert to CSR for solving
        J_reduced = J_reduced.tocsr()

        # Calculate correction terms
        corr1 = spsolve(J_reduced, mismatch_reduced)

        # Add rows to correction vector for transformerless buses
        corr = np.zeros(4 * ng)
        corr[rows_to_keep] = corr1

        # Update converter voltage magnitude and angle
        Vca = Vca + corr[i1]
        Vfa = Vfa + corr[i2]
        Vcm = Vcm * (1.0 + corr[i3])
        Vfm = Vfm * (1.0 + corr[i4])

    # Convergence print
    if not cflag:
        print(f'\nSlackbus converter power calculation did NOT converge in {it} iterations')

    # Define cos and sin of angles for final calculation
    cosfc = np.cos(Vfa - Vca)
    sinfc = np.sin(Vfa - Vca)
    cossf = np.cos(Vsa - Vfa)
    sinsf = np.sin(Vsa - Vfa)
    cossc = np.cos(Vsa - Vca)
    sinsc = np.sin(Vsa - Vca)

    # Output update
    # Slack bus VSC grid injection active power
    Ps = ((-Vsm ** 2 * Gtf + Vfm * Vsm * (Gtf * cossf + Btf * sinsf)) * (Ztf != 0) +
          (-Vsm ** 2 * Gc + Vsm * Vcm * (Gc * cossc + Bc * sinsc)) * (Ztf == 0))

    # Slack bus converter side reactive power
    Qc = -Vcm ** 2 * Bc + Vfm * Vcm * (Gc * sinfc + Bc * cosfc)

    # Slack bus converter voltage
    Vc = Vcm * np.exp(1j * Vca)

    return Ps, Qc, Vc