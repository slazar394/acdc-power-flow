"""Load dc system data from .py or .pkl files or dict.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import os
import importlib.util
import pickle
import numpy as np


def loadcasedc(casefile):
    """Load dc system data from file or dict.

    Args:
        casefile: dict, .py file path, or .pkl file path with dc grid data

    Returns:
        If single output: dict with keys baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc
        If multiple outputs: tuple (baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc)

    Examples:
        # Load as dict
        mpcdc = loadcasedc('case5_stagg_HVDCptp')

        # Load as separate variables
        baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = loadcasedc('case5_stagg_HVDCptp')
    """

    # Read data into dict
    if isinstance(casefile, str):
        rootname = casefile
        extension = None

        # Check for explicit extension
        if casefile.endswith('.py'):
            rootname = casefile[:-3]
            extension = '.py'
        elif casefile.endswith('.pkl'):
            rootname = casefile[:-4]
            extension = '.pkl'

        # Set extension if not specified
        if extension is None:
            if os.path.exists(casefile + '.pkl'):
                extension = '.pkl'
            elif os.path.exists(casefile + '.py'):
                extension = '.py'
            else:
                raise FileNotFoundError(f"Case file not found: {casefile}")

        # Load file
        if extension == '.pkl':
            with open(rootname + '.pkl', 'rb') as f:
                s = pickle.load(f)
                if not isinstance(s, dict):
                    raise ValueError("Pickle file must contain a dict")
        elif extension == '.py':
            spec = importlib.util.spec_from_file_location("casemodule", rootname + '.py')
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module: {rootname}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get function name from file
            func_name = os.path.basename(rootname)
            if hasattr(module, func_name):
                result = getattr(module, func_name)()
                if isinstance(result, dict):
                    s = result
                else:
                    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = result
                    s = {
                        'baseMVAac': baseMVAac,
                        'baseMVAdc': baseMVAdc,
                        'pol': pol,
                        'busdc': busdc,
                        'convdc': convdc,
                        'branchdc': branchdc
                    }
            else:
                raise AttributeError(f"Function {func_name} not found in {rootname}.py")

    elif isinstance(casefile, dict):
        s = casefile
    else:
        raise TypeError("Input must be a dict or string containing a filename")

    # Check for required fields
    required_fields = ['baseMVAac', 'baseMVAdc', 'busdc', 'convdc', 'branchdc']
    missing = [f for f in required_fields if f not in s]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    mpc = s.copy()

    # Add voltage droop parameters if not defined
    if mpc['convdc'].shape[1] < 24:
        ii = 24 - mpc['convdc'].shape[1]
        mpc['convdc'] = np.column_stack([
            mpc['convdc'],
            np.zeros((mpc['convdc'].shape[0], ii))
        ])

    return mpc


if __name__ == "__main__":
    # Test loading
    print("Testing loadcasedc function:")

    try:
        mpc = loadcasedc('Cases/PowerFlowDC/case5_stagg_HVDCptp')
        print(f"\nLoaded case5_stagg_HVDCptp as dict:")
        print(f"  baseMVAac: {mpc['baseMVAac']}")
        print(f"  baseMVAdc: {mpc['baseMVAdc']}")
        print(f"  pol: {mpc['pol']}")
        print(f"  busdc shape: {mpc['busdc'].shape}")
        print(f"  convdc shape: {mpc['convdc'].shape}")
        print(f"  branchdc shape: {mpc['branchdc'].shape}")
    except Exception as e:
        print(f"Error: {e}")