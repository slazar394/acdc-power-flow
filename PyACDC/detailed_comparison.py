"""Detailed field-by-field comparison for power flow results.

This script provides detailed analysis of differences between MatACDC and PyACDC,
including per-bus, per-generator, and per-converter comparisons.
"""
import numpy as np
import pickle
import scipy.io as sio
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc
from pypower.idx_bus import BUS_I, BUS_TYPE, PD, QD, VM, VA
from pypower.idx_gen import GEN_BUS, PG, QG
from pypower.idx_brch import F_BUS, T_BUS, PF, QF, PT, QT


def detailed_bus_comparison(matlab_bus, python_bus, test_name, tol=1e-5):
    """Detailed comparison of bus results.
    
    Args:
        matlab_bus: MATLAB bus matrix
        python_bus: Python bus matrix
        test_name: Name of test
        tol: Tolerance for comparison
    """
    print(f"\n{'=' * 80}")
    print(f"Detailed Bus Comparison - {test_name}")
    print('=' * 80)
    
    n_buses = matlab_bus.shape[0]
    
    # Compare voltage magnitudes
    vm_diff = np.abs(matlab_bus[:, VM] - python_bus[:, VM])
    va_diff = np.abs(matlab_bus[:, VA] - python_bus[:, VA])
    
    print(f"\nVoltage Magnitude (VM):")
    print(f"  Max difference: {np.max(vm_diff):.2e} p.u.")
    print(f"  Mean difference: {np.mean(vm_diff):.2e} p.u.")
    
    if np.max(vm_diff) > tol:
        print(f"  Buses with VM diff > {tol}:")
        large_diff = np.where(vm_diff > tol)[0]
        for bus_idx in large_diff[:10]:  # Show first 10
            bus_num = int(matlab_bus[bus_idx, BUS_I])
            print(f"    Bus {bus_num}: MATLAB={matlab_bus[bus_idx, VM]:.6f}, "
                  f"Python={python_bus[bus_idx, VM]:.6f}, "
                  f"Diff={vm_diff[bus_idx]:.2e}")
    
    print(f"\nVoltage Angle (VA):")
    print(f"  Max difference: {np.max(va_diff):.2e} degrees")
    print(f"  Mean difference: {np.mean(va_diff):.2e} degrees")
    
    if np.max(va_diff) > tol:
        print(f"  Buses with VA diff > {tol}:")
        large_diff = np.where(va_diff > tol)[0]
        for bus_idx in large_diff[:10]:  # Show first 10
            bus_num = int(matlab_bus[bus_idx, BUS_I])
            print(f"    Bus {bus_num}: MATLAB={matlab_bus[bus_idx, VA]:.6f}, "
                  f"Python={python_bus[bus_idx, VA]:.6f}, "
                  f"Diff={va_diff[bus_idx]:.2e}")


def detailed_gen_comparison(matlab_gen, python_gen, test_name, tol=1e-5):
    """Detailed comparison of generator results.
    
    Args:
        matlab_gen: MATLAB gen matrix
        python_gen: Python gen matrix
        test_name: Name of test
        tol: Tolerance for comparison
    """
    print(f"\n{'=' * 80}")
    print(f"Detailed Generator Comparison - {test_name}")
    print('=' * 80)
    
    # Compare active power
    pg_diff = np.abs(matlab_gen[:, PG] - python_gen[:, PG])
    qg_diff = np.abs(matlab_gen[:, QG] - python_gen[:, QG])
    
    print(f"\nActive Power (PG):")
    print(f"  Max difference: {np.max(pg_diff):.2e} MW")
    print(f"  Mean difference: {np.mean(pg_diff):.2e} MW")
    print(f"  Total MATLAB: {np.sum(matlab_gen[:, PG]):.2f} MW")
    print(f"  Total Python: {np.sum(python_gen[:, PG]):.2f} MW")
    
    if np.max(pg_diff) > tol:
        print(f"  Generators with PG diff > {tol}:")
        large_diff = np.where(pg_diff > tol)[0]
        for gen_idx in large_diff[:10]:  # Show first 10
            bus_num = int(matlab_gen[gen_idx, GEN_BUS])
            print(f"    Gen at bus {bus_num}: MATLAB={matlab_gen[gen_idx, PG]:.4f}, "
                  f"Python={python_gen[gen_idx, PG]:.4f}, "
                  f"Diff={pg_diff[gen_idx]:.2e}")
    
    print(f"\nReactive Power (QG):")
    print(f"  Max difference: {np.max(qg_diff):.2e} MVAr")
    print(f"  Mean difference: {np.mean(qg_diff):.2e} MVAr")
    print(f"  Total MATLAB: {np.sum(matlab_gen[:, QG]):.2f} MVAr")
    print(f"  Total Python: {np.sum(python_gen[:, QG]):.2f} MVAr")
    
    if np.max(qg_diff) > tol:
        print(f"  Generators with QG diff > {tol}:")
        large_diff = np.where(qg_diff > tol)[0]
        for gen_idx in large_diff[:10]:  # Show first 10
            bus_num = int(matlab_gen[gen_idx, GEN_BUS])
            print(f"    Gen at bus {bus_num}: MATLAB={matlab_gen[gen_idx, QG]:.4f}, "
                  f"Python={python_gen[gen_idx, QG]:.4f}, "
                  f"Diff={qg_diff[gen_idx]:.2e}")


def detailed_dc_comparison(matlab_dc, python_dc, test_name, tol=1e-5):
    """Detailed comparison of DC network results.
    
    Args:
        matlab_dc: MATLAB DC results
        python_dc: Python DC results
        test_name: Name of test
        tol: Tolerance for comparison
    """
    print(f"\n{'=' * 80}")
    print(f"Detailed DC Network Comparison - {test_name}")
    print('=' * 80)
    
    # Get named indices
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()
    
    DCDROOP, DCSLACK, DCNOSLACK, PVC, PQC, CONV_BUS, CONVTYPE_DC, \
        CONVTYPE_AC, PCONV, QCONV, VCONV, RTF, XTF, BF, RCONV, XCONV, \
        BASEKVC, VCMAX, VCMIN, ICMAX, CONVSTATUS, LOSSA, LOSSB, LOSSCR, \
        LOSSCI, DROOP, PDCSET, VDCSET, DVDCSET, VMC, VAC, PCCONV, QCCONV, \
        PCLOSS, VMF, VAF, PFIL, QCONVF, QCCONVF = idx_convdc()
    
    # Compare DC bus voltages
    matlab_busdc = matlab_dc['busdc']
    python_busdc = python_dc['busdc']
    
    vdc_diff = np.abs(matlab_busdc[:, VDC] - python_busdc[:, VDC])
    pdc_diff = np.abs(matlab_busdc[:, PDC] - python_busdc[:, PDC])
    
    print(f"\nDC Bus Voltages (VDC):")
    print(f"  Max difference: {np.max(vdc_diff):.2e} p.u.")
    print(f"  Mean difference: {np.mean(vdc_diff):.2e} p.u.")
    
    if np.max(vdc_diff) > tol:
        print(f"  DC Buses with VDC diff > {tol}:")
        large_diff = np.where(vdc_diff > tol)[0]
        for bus_idx in large_diff:
            bus_num = int(matlab_busdc[bus_idx, BUSDC_I])
            print(f"    DC Bus {bus_num}: MATLAB={matlab_busdc[bus_idx, VDC]:.6f}, "
                  f"Python={python_busdc[bus_idx, VDC]:.6f}, "
                  f"Diff={vdc_diff[bus_idx]:.2e}")
    
    print(f"\nDC Bus Powers (PDC):")
    print(f"  Max difference: {np.max(pdc_diff):.2e} MW")
    print(f"  Mean difference: {np.mean(pdc_diff):.2e} MW")
    
    # Compare converter results
    matlab_convdc = matlab_dc['convdc']
    python_convdc = python_dc['convdc']
    
    pconv_diff = np.abs(matlab_convdc[:, PCONV] - python_convdc[:, PCONV])
    qconv_diff = np.abs(matlab_convdc[:, QCONV] - python_convdc[:, QCONV])
    ploss_diff = np.abs(matlab_convdc[:, PCLOSS] - python_convdc[:, PCLOSS])
    
    print(f"\nConverter Active Power (PCONV):")
    print(f"  Max difference: {np.max(pconv_diff):.2e} MW")
    print(f"  Mean difference: {np.mean(pconv_diff):.2e} MW")
    print(f"  Total MATLAB: {np.sum(matlab_convdc[:, PCONV]):.2f} MW")
    print(f"  Total Python: {np.sum(python_convdc[:, PCONV]):.2f} MW")
    
    if np.max(pconv_diff) > tol:
        print(f"  Converters with PCONV diff > {tol}:")
        large_diff = np.where(pconv_diff > tol)[0]
        for conv_idx in large_diff:
            bus_num = int(matlab_convdc[conv_idx, CONV_BUS])
            print(f"    Conv at DC bus {bus_num}: MATLAB={matlab_convdc[conv_idx, PCONV]:.4f}, "
                  f"Python={python_convdc[conv_idx, PCONV]:.4f}, "
                  f"Diff={pconv_diff[conv_idx]:.2e}")
    
    print(f"\nConverter Reactive Power (QCONV):")
    print(f"  Max difference: {np.max(qconv_diff):.2e} MVAr")
    print(f"  Mean difference: {np.mean(qconv_diff):.2e} MVAr")
    
    print(f"\nConverter Losses (PCLOSS):")
    print(f"  Max difference: {np.max(ploss_diff):.2e} MW")
    print(f"  Mean difference: {np.mean(ploss_diff):.2e} MW")
    print(f"  Total MATLAB: {np.sum(matlab_convdc[:, PCLOSS]):.2f} MW")
    print(f"  Total Python: {np.sum(python_convdc[:, PCLOSS]):.2f} MW")


def detailed_comparison(matlab_file, python_file, test_name='test1_slack', tol=1e-5):
    """Perform detailed comparison for a specific test.
    
    Args:
        matlab_file: Path to MATLAB results
        python_file: Path to Python results
        test_name: Name of test to compare
        tol: Tolerance for flagging differences
    """
    # Load results
    print(f"Loading results for detailed comparison...")
    mat_data = sio.loadmat(matlab_file, struct_as_record=False, squeeze_me=True)
    
    with open(python_file, 'rb') as f:
        py_data = pickle.load(f)
    
    # Get test data
    if test_name not in mat_data or test_name not in py_data:
        print(f"ERROR: Test {test_name} not found in both result sets")
        return
    
    matlab_test = mat_data[test_name]
    python_test = py_data[test_name]
    
    # Check for errors
    if hasattr(matlab_test, 'error') or 'error' in python_test:
        print(f"ERROR: Test has errors and cannot be compared")
        return
    
    # AC network comparison
    matlab_ac = matlab_test.resultsac
    python_ac = python_test['resultsac']
    
    if hasattr(matlab_ac, 'bus') and 'bus' in python_ac:
        detailed_bus_comparison(matlab_ac.bus, python_ac['bus'], test_name, tol)
    
    if hasattr(matlab_ac, 'gen') and 'gen' in python_ac:
        detailed_gen_comparison(matlab_ac.gen, python_ac['gen'], test_name, tol)
    
    # DC network comparison
    matlab_dc = {
        'busdc': matlab_test.resultsdc.busdc,
        'convdc': matlab_test.resultsdc.convdc,
        'branchdc': matlab_test.resultsdc.branchdc
    }
    python_dc = python_test['resultsdc']
    
    detailed_dc_comparison(matlab_dc, python_dc, test_name, tol)
    
    print(f"\n{'=' * 80}")
    print("Detailed comparison complete")
    print('=' * 80)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) >= 3:
        matlab_file = sys.argv[1]
        python_file = sys.argv[2]
        test_name = sys.argv[3] if len(sys.argv) >= 4 else 'test1_slack'
        tol = float(sys.argv[4]) if len(sys.argv) >= 5 else 1e-5
    else:
        matlab_file = 'matlab_results.mat'
        python_file = 'pyacdc_results.pkl'
        test_name = 'test1_slack'
        tol = 1e-5
    
    print(f"Detailed comparison:")
    print(f"  MATLAB: {matlab_file}")
    print(f"  Python: {python_file}")
    print(f"  Test: {test_name}")
    print(f"  Tolerance: {tol}")
    
    try:
        detailed_comparison(matlab_file, python_file, test_name, tol)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
