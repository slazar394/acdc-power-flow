"""Converter loss calculation.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np


def calclossac(Pc, Qc, Vc, lossa, lossb, losscr, lossci):
    """Calculates converter losses based on quadratic current-dependent loss model.

    Calculates the converter losses based on a loss model quadratically
    dependent on the converter current Ic.

    Converter loss model obtained from:
    G. Daelemans, VSC HVDC in meshed networks, Master Thesis,
    KU Leuven, July 2008.

    Args:
        Pc: Converter active power injection
        Qc: Converter reactive power injection
        Vc: Complex converter voltage
        lossa: Constant converter loss coefficient
        lossb: Linear converter loss coefficient
        losscr: Quadratic converter loss coefficient (rectifier)
        lossci: Quadratic converter loss coefficient (inverter)

    Returns:
        Ploss: Converter losses

    Loss model: Ploss = a + b*Ic + c*Ic^2
    where:
        - a: constant loss coefficient
        - b: linear loss coefficient
        - c: quadratic loss coefficient (depends on rectifier/inverter mode)
        - Ic: converter current
    """
    # Converter loss input data
    # Per unit loss coefficients
    a = lossa  # Constant loss coefficient [-]
    b = lossb  # Linear loss coefficient [-]
    c = np.column_stack([losscr, lossci])  # Quadratic loss coefficient [-]

    # Converter input data
    # Define other coefficients
    nc = len(Pc) if isinstance(Pc, np.ndarray) else 1  # Number of converters
    convmode = np.sign(Pc)  # Converter operation mode
    rectifier = (convmode > 0).astype(int)  # Rectifier mode (Pc > 0)
    inverter = (convmode < 0).astype(int)  # Inverter mode (Pc < 0)
    VMc = np.abs(Vc)  # Converter voltage magnitude

    # Select quadratic coefficient based on operating mode
    c_mtx = rectifier * c[:, 0] + inverter * c[:, 1]

    # Converter loss calculation
    # Converter current
    Ic = np.sqrt(Pc ** 2 + Qc ** 2) / VMc

    # Converter losses: Ploss = a + b*Ic + c*Ic^2
    Ploss = a * np.ones(len(Ic)) + b * Ic + c_mtx * Ic ** 2

    return Ploss


if __name__ == "__main__":
    print("Testing calclossac function:")

    # Test Case 1: Single converter in rectifier mode
    print("\n=== Test Case 1: Rectifier mode (Pc > 0) ===")
    Pc = np.array([1.0])  # 100 MW (positive = rectifier)
    Qc = np.array([0.3])  # 30 MVAr
    Vc = np.array([1.0 + 0.0j])  # converter voltage
    lossa = np.array([1.103])
    lossb = np.array([0.887])
    losscr = np.array([2.885])  # Rectifier coefficient
    lossci = np.array([4.371])  # Inverter coefficient

    Ploss = calclossac(Pc, Qc, Vc, lossa, lossb, losscr, lossci)

    Ic = np.sqrt(Pc ** 2 + Qc ** 2) / np.abs(Vc)
    print(f"Converter current: {Ic[0]:.2f} p.u.")
    print(f"Operating mode: Rectifier (Pc > 0)")
    print(f"Losses: {Ploss[0]:.3f} MW")
    print(f"Loss breakdown: a={lossa[0]:.3f} + b*Ic={lossb[0] * Ic[0]:.3f} + c*Ic^2={losscr[0] * Ic[0] ** 2:.3f}")

    # Test Case 2: Single converter in inverter mode
    print("\n=== Test Case 2: Inverter mode (Pc < 0) ===")
    Pc = np.array([-1.0])  # -100 MW (negative = inverter)
    Qc = np.array([0.3])
    Vc = np.array([1.0 + 0.0j])

    Ploss = calclossac(Pc, Qc, Vc, lossa, lossb, losscr, lossci)

    Ic = np.sqrt(Pc ** 2 + Qc ** 2) / np.abs(Vc)
    print(f"Converter current: {Ic[0]:.2f} p.u.")
    print(f"Operating mode: Inverter (Pc < 0)")
    print(f"Losses: {Ploss[0]:.3f} MW")
    print(f"Loss breakdown: a={lossa[0]:.3f} + b*Ic={lossb[0] * Ic[0]:.3f} + c*Ic^2={lossci[0] * Ic[0] ** 2:.3f}")

    # Test Case 3: Multiple converters
    print("\n=== Test Case 3: Multiple converters ===")
    Pc = np.array([1.0, -0.8, 0.6])  # Mixed modes
    Qc = np.array([0.3, -0.2, 0.15])
    Vc = np.array([1.0 + 0.0j, 0.98 + 0.05j, 1.02 - 0.03j])
    lossa = np.array([1.103, 1.103, 1.103])
    lossb = np.array([0.887, 0.887, 0.887])
    losscr = np.array([2.885, 2.885, 2.885])
    lossci = np.array([4.371, 4.371, 4.371])

    Ploss = calclossac(Pc, Qc, Vc, lossa, lossb, losscr, lossci)

    for i in range(len(Pc)):
        mode = "Rectifier" if Pc[i] > 0 else "Inverter"
        print(f"Converter {i + 1}: {mode}, Pc={Pc[i]:.1f} MW, Losses={Ploss[i]:.3f} MW")

    print("\n✓ Converter loss calculation completed successfully!")