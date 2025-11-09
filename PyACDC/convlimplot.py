"""Plots converter limits and violations in PQ capability chart.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
import matplotlib.pyplot as plt


def convlimplot(plotarg, convi):
    """Plots converter limits and violations in PQ capability chart.

    Graphical representation of converter limit violations.

    Implementation based on:
    J. Beerten, S. Cole and R. Belmans: "Generalized Steady-State VSC MTDC
    Model for Sequential AC/DC Power Flow Algorithms", IEEE Trans. Pow.
    Syst., vol. 27, no. 2, 2012, pp. 821 - 829.

    Args:
        plotarg: Arguments for converter limit plot
            Index - Name       Description
            0   - VIOL         Converter limit violation type
                                0 - no limit hit
                                1 - reactive power violation
                                2 - active power violation
            1   - ZTF          Transformer impedance
            2   - ZF           Filter impedance
            3   - ZC           Converter impedance
            4   - Y1           Pi-equivalent admittance 1
            5   - Y2           Pi-equivalent admittance 2
            6   - YF           Filter admittance
            7   - YTF          Transformer admittance
            8   - VS           Grid voltage
            9   - ICMAX        Converter current limit
            10  - VCMMAX       Converter upper voltage limit
            11  - VCMMIN       Converter lower voltage limit
            12  - SSOLD        Grid side apparent power before limiting
            13  - SSNEW        Grid side apparent power after limiting
            14  - SSICMAX      Grid side apparent power: converter current limit (Ps constant)
            15  - SSVCMAX      Grid side apparent power: converter upper voltage limit (Ps constant)
            16  - SSVCMIN      Grid side apparent power: converter lower voltage limit (Ps constant)
        convi: Converter number

    Plot assumptions:
        - Vs = Vsm * exp(j*0) with Vsm constant
        - Converter upper and lower voltage limit: Vc = Vcm * exp(Vca)
        - Converter current limit: Ic = Icm * exp(Ica)
    """
    # Initialization - define arguments
    viol = int(np.real(plotarg[0]))
    Ztf = plotarg[1]
    Zf = plotarg[2]
    Zc = plotarg[3]
    Y1 = plotarg[4]
    Y2 = plotarg[5]
    Yf = plotarg[6]
    Ytf = plotarg[7]
    Vs = plotarg[8]
    Icmax = np.real(plotarg[9])
    Vcmmax = np.real(plotarg[10])
    Vcmmin = np.real(plotarg[11])
    Ssold = plotarg[12]
    Ssnew = plotarg[13]
    SsIcmax = plotarg[14]
    SsVcmax = plotarg[15]
    SsVcmin = plotarg[16]

    # Grid side voltage amplitude
    Vsm = np.abs(Vs)

    # Current limits
    # Current limit with current converter set-up
    i1 = 0.001  # Plot current angle step size
    Ica = np.arange(0, 2 * np.pi, i1)

    # Determine factor based on transformer and filter presence
    if Ztf != 0 and Yf != 0:
        factor = np.conj(Ytf) / (np.conj(Ytf) + np.conj(Yf))
    else:
        factor = 1

    SsIlim = (Vs * Icmax * np.exp(-1j * Ica) * factor -
              Vsm ** 2 * np.ones(len(Ica)) * (1 / (np.conj(Zf) + np.conj(Ztf))))

    SsIlimMP = -Vsm ** 2 * (1 / (np.conj(Zf) + np.conj(Ztf)))  # Center of figure

    # Current limit without filter
    SsIlim1 = Vs * Icmax * np.exp(-1j * Ica)

    # Voltage limits
    # Voltage limits with current converter set-up
    i2 = 0.001  # Plot voltage angle step size
    Vca = np.arange(0, 2 * np.pi, i2)

    SsVmax = -Vsm ** 2 * np.conj(Y1 + Y2) + Vs * Vcmmax * np.exp(-1j * Vca) * np.conj(Y2)
    SsVmin = -Vsm ** 2 * np.conj(Y1 + Y2) + Vs * Vcmmin * np.exp(-1j * Vca) * np.conj(Y2)

    # Voltage limits without filter
    Y_no_filter = 1 / (Ztf + Zc)
    SsVmax1 = -Vsm ** 2 * np.conj(Y_no_filter) + Vs * Vcmmax * np.exp(-1j * Vca) * np.conj(Y_no_filter)
    SsVmin1 = -Vsm ** 2 * np.conj(Y_no_filter) + Vs * Vcmmin * np.exp(-1j * Vca) * np.conj(Y_no_filter)

    # Plot converter limits
    # Plot options
    xmin = -1.5 / 1.2 * Icmax
    xmax = 1.5 / 1.2 * Icmax
    ymin = -1.5 / 1.2 * Icmax
    ymax = 1.5 / 1.2 * Icmax
    ix = 0.001
    iy = 0.001
    xx = np.arange(xmin, xmax, ix)
    yy = np.arange(ymin, ymax, iy)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('P$_s$ (p.u.)', fontsize=12)
    ax.set_ylabel('Q$_s$ (p.u.)', fontsize=12)

    # Plot graph title
    if viol != 0:
        ax.set_title(f'Converter station {convi} operating outside its limits.', fontsize=14)
    else:
        ax.set_title(f'Normal operation of converter station {convi}', fontsize=14)

    # Plot axes
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)

    # Center of current limit
    ax.scatter(np.real(SsIlimMP), np.imag(SsIlimMP), c='b', marker='+', s=100,
               label='Current limit center', zorder=5)

    # Old active and reactive powers
    ax.scatter(np.real(Ssold), np.imag(Ssold), c='k', marker='o', s=100,
               label='Operating point (before)', zorder=5)

    # New active and reactive powers
    ax.scatter(np.real(Ssnew), np.imag(Ssnew), c='k', marker='^', s=100,
               label='Operating point (after)', zorder=5)

    # Actual limit plots
    ax.plot(np.real(SsIlim), np.imag(SsIlim), 'b-', linewidth=2,
            label='Current limit (I$_{max}$)')
    ax.plot(np.real(SsVmax), np.imag(SsVmax), 'r-', linewidth=2,
            label='Upper voltage limit (V$_{max}$)')
    ax.plot(np.real(SsVmin), np.imag(SsVmin), 'g-', linewidth=2,
            label='Lower voltage limit (V$_{min}$)')

    # Limit plots neglecting filter effect
    ax.plot(np.real(SsIlim1), np.imag(SsIlim1), 'b:', linewidth=1.5,
            label='Current limit (no filter)', alpha=0.6)
    ax.plot(np.real(SsVmax1), np.imag(SsVmax1), 'r:', linewidth=1.5,
            label='Upper voltage limit (no filter)', alpha=0.6)
    ax.plot(np.real(SsVmin1), np.imag(SsVmin1), 'g:', linewidth=1.5,
            label='Lower voltage limit (no filter)', alpha=0.6)

    # Plot limit points
    if viol == 1:
        ax.scatter(np.real(SsIcmax), np.imag(SsIcmax), c='b', marker='x', s=150,
                   linewidths=3, label='Current limit violation point', zorder=5)
        ax.scatter(np.real(SsVcmax), np.imag(SsVcmax), c='r', marker='x', s=150,
                   linewidths=3, label='Upper voltage limit point', zorder=5)
        ax.scatter(np.real(SsVcmin), np.imag(SsVcmin), c='g', marker='x', s=150,
                   linewidths=3, label='Lower voltage limit point', zorder=5)

    # Add legend
    ax.legend(loc='best', fontsize=10)

    plt.tight_layout()
    plt.show()
