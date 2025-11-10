"""Compare power flow results between MatACDC (MATLAB) and PyACDC (Python).

This script compares numerical results from both implementations to validate
the Python port.
"""
import numpy as np
import pickle
import scipy.io as sio


def load_matlab_results(mat_file):
    """Load results from MATLAB .mat file as nested Python dicts."""
    def _todict(matobj):
        result = {}
        for field_name in matobj._fieldnames:
            elem = getattr(matobj, field_name)
            if isinstance(elem, sio.matlab.mio5_params.mat_struct):
                result[field_name] = _todict(elem)
            else:
                result[field_name] = elem
        return result

    def _check_keys(d):
        for key in d:
            if isinstance(d[key], sio.matlab.mio5_params.mat_struct):
                d[key] = _todict(d[key])
        return d

    mat_data = sio.loadmat(mat_file, struct_as_record=False, squeeze_me=True)
    return _check_keys(mat_data)



def load_python_results(pkl_file):
    """Load results from Python pickle file.
    
    Args:
        pkl_file: Path to pickle file with Python results
        
    Returns:
        dict: Dictionary with test results
    """
    with open(pkl_file, 'rb') as f:
        return pickle.load(f)


def compare_arrays(arr1, arr2, name, rtol=1e-5, atol=1e-8):
    """Compare two arrays and return statistics.
    
    Args:
        arr1: First array (e.g., MATLAB)
        arr2: Second array (e.g., Python)
        name: Name of the quantity being compared
        rtol: Relative tolerance
        atol: Absolute tolerance
        
    Returns:
        dict: Comparison statistics
    """
    if arr1.shape != arr2.shape:
        return {
            'name': name,
            'match': False,
            'error': f'Shape mismatch: {arr1.shape} vs {arr2.shape}'
        }
    
    # Calculate differences
    diff = arr1 - arr2
    abs_diff = np.abs(diff)
    max_abs_diff = np.max(abs_diff)
    mean_abs_diff = np.mean(abs_diff)
    
    # Relative error (avoid division by zero)
    with np.errstate(divide='ignore', invalid='ignore'):
        rel_diff = abs_diff / (np.abs(arr1) + 1e-12)
    max_rel_diff = np.nanmax(rel_diff)
    mean_rel_diff = np.nanmean(rel_diff)
    
    # Check if arrays are close
    is_close = np.allclose(arr1, arr2, rtol=rtol, atol=atol)
    
    return {
        'name': name,
        'match': is_close,
        'max_abs_diff': max_abs_diff,
        'mean_abs_diff': mean_abs_diff,
        'max_rel_diff': max_rel_diff,
        'mean_rel_diff': mean_rel_diff,
        'shape': arr1.shape
    }


def compare_test_results(matlab_test, python_test, test_name, rtol=1e-5, atol=1e-8):
    """Compare results from a single test case.
    
    Args:
        matlab_test: MATLAB test results
        python_test: Python test results
        test_name: Name of the test
        rtol: Relative tolerance
        atol: Absolute tolerance
        
    Returns:
        dict: Detailed comparison results
    """
    print(f"\n{'=' * 80}")
    print(f"Comparing: {test_name}")
    print('=' * 80)
    
    # Check convergence
    matlab_conv = matlab_test.get('converged', False)
    python_conv = python_test.get('converged', False)
    
    print(f"\nConvergence:")
    print(f"  MATLAB: {matlab_conv}")
    print(f"  Python: {python_conv}")
    
    if matlab_conv != python_conv:
        print("  WARNING: Convergence status differs!")
    
    comparison = {
        'test': test_name,
        'matlab_converged': matlab_conv,
        'python_converged': python_conv,
        'ac_results': {},
        'dc_results': {}
    }
    
    # Compare AC results
    print(f"\n{'-' * 40}")
    print("AC Network Results:")
    print('-' * 40)
    
    matlab_ac = matlab_test['resultsac']
    python_ac = python_test['resultsac']
    
    # Compare bus data
    if 'bus' in matlab_ac and 'bus' in python_ac:
        result = compare_arrays(matlab_ac['bus'], python_ac['bus'], 
                               'bus', rtol, atol)
        comparison['ac_results']['bus'] = result
        print(f"\nBus matrix:")
        print(f"  Shape: {result['shape']}")
        print(f"  Match: {result['match']}")
        print(f"  Max abs diff: {result['max_abs_diff']:.2e}")
        print(f"  Max rel diff: {result['max_rel_diff']:.2e}")
    
    # Compare gen data
    if 'gen' in matlab_ac and 'gen' in python_ac:
        result = compare_arrays(matlab_ac['gen'], python_ac['gen'], 
                               'gen', rtol, atol)
        comparison['ac_results']['gen'] = result
        print(f"\nGen matrix:")
        print(f"  Shape: {result['shape']}")
        print(f"  Match: {result['match']}")
        print(f"  Max abs diff: {result['max_abs_diff']:.2e}")
        print(f"  Max rel diff: {result['max_rel_diff']:.2e}")
    
    # Compare branch data
    if 'branch' in matlab_ac and 'branch' in python_ac:
        result = compare_arrays(matlab_ac['branch'], python_ac['branch'], 
                               'branch', rtol, atol)
        comparison['ac_results']['branch'] = result
        print(f"\nBranch matrix:")
        print(f"  Shape: {result['shape']}")
        print(f"  Match: {result['match']}")
        print(f"  Max abs diff: {result['max_abs_diff']:.2e}")
        print(f"  Max rel diff: {result['max_rel_diff']:.2e}")
    
    # Compare DC results
    print(f"\n{'-' * 40}")
    print("DC Network Results:")
    print('-' * 40)
    
    matlab_dc = matlab_test['resultsdc']
    python_dc = python_test['resultsdc']
    
    # Compare busdc data
    if 'busdc' in matlab_dc and 'busdc' in python_dc:
        result = compare_arrays(matlab_dc['busdc'], python_dc['busdc'], 
                               'busdc', rtol, atol)
        comparison['dc_results']['busdc'] = result
        print(f"\nDC Bus matrix:")
        print(f"  Shape: {result['shape']}")
        print(f"  Match: {result['match']}")
        print(f"  Max abs diff: {result['max_abs_diff']:.2e}")
        print(f"  Max rel diff: {result['max_rel_diff']:.2e}")
    
    # Compare convdc data
    if 'convdc' in matlab_dc and 'convdc' in python_dc:
        result = compare_arrays(matlab_dc['convdc'], python_dc['convdc'], 
                               'convdc', rtol, atol)
        comparison['dc_results']['convdc'] = result
        print(f"\nConverter matrix:")
        print(f"  Shape: {result['shape']}")
        print(f"  Match: {result['match']}")
        print(f"  Max abs diff: {result['max_abs_diff']:.2e}")
        print(f"  Max rel diff: {result['max_rel_diff']:.2e}")
    
    # Compare branchdc data
    if 'branchdc' in matlab_dc and 'branchdc' in python_dc:
        result = compare_arrays(matlab_dc['branchdc'], python_dc['branchdc'], 
                               'branchdc', rtol, atol)
        comparison['dc_results']['branchdc'] = result
        print(f"\nDC Branch matrix:")
        print(f"  Shape: {result['shape']}")
        print(f"  Match: {result['match']}")
        print(f"  Max abs diff: {result['max_abs_diff']:.2e}")
        print(f"  Max rel diff: {result['max_rel_diff']:.2e}")
    
    # Overall status
    all_match = all(
        result.get('match', False) 
        for results in [comparison['ac_results'], comparison['dc_results']]
        for result in results.values()
    )
    
    comparison['status'] = 'PASS' if all_match else 'DIFFERENCES_FOUND'
    
    print(f"\n{'=' * 80}")
    print(f"Overall Status: {comparison['status']}")
    print('=' * 80)
    
    return comparison


def compare_all_tests(matlab_file, python_file, rtol=1e-5, atol=1e-8, 
                     save_report=True, report_file='comparison_report.txt'):
    """Compare all test results between MATLAB and Python.
    
    Args:
        matlab_file: Path to MATLAB results file
        python_file: Path to Python results file
        rtol: Relative tolerance
        atol: Absolute tolerance
        save_report: If True, save detailed report
        report_file: Path for report file
        
    Returns:
        dict: Comparison results for all tests
    """
    print("\n" + "=" * 80)
    print("MatACDC vs PyACDC Comparison")
    print("=" * 80)
    
    # Load results
    print(f"\nLoading MATLAB results from: {matlab_file}")
    matlab_results = load_matlab_results(matlab_file)
    
    print(f"Loading Python results from: {python_file}")
    python_results = load_python_results(python_file)
    
    # Map test names between MATLAB and Python
    test_mapping = {
        'test1_slack': 'test1_slack',
        'test2_droop': 'test2_droop',
        'test3_inf': 'test3_inf',
        'test4_multi': 'test4_multi'
    }
    
    all_comparisons = {}
    
    # Compare each test
    for matlab_name, python_name in test_mapping.items():
        if matlab_name in matlab_results and python_name in python_results:
            comparison = compare_test_results(
                matlab_results[matlab_name],
                python_results[python_name],
                python_name,
                rtol,
                atol
            )
            all_comparisons[python_name] = comparison
        else:
            print(f"\nWARNING: Test {python_name} not found in both result sets")
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for test_name, comparison in all_comparisons.items():
        status = comparison.get('status', 'UNKNOWN')
        print(f"{test_name:20s}: {status}")
    
    # Save report
    if save_report:
        with open(report_file, 'w') as f:
            f.write("MatACDC vs PyACDC Comparison Report\n")
            f.write("=" * 80 + "\n\n")
            
            for test_name, comparison in all_comparisons.items():
                f.write(f"\nTest: {test_name}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Status: {comparison.get('status', 'UNKNOWN')}\n")
                f.write(f"MATLAB Converged: {comparison.get('matlab_converged', 'N/A')}\n")
                f.write(f"Python Converged: {comparison.get('python_converged', 'N/A')}\n\n")
                
                f.write("AC Results:\n")
                for matrix, result in comparison.get('ac_results', {}).items():
                    f.write(f"  {matrix}:\n")
                    f.write(f"    Match: {result.get('match', 'N/A')}\n")
                    f.write(f"    Max abs diff: {result.get('max_abs_diff', 'N/A'):.2e}\n")
                    f.write(f"    Max rel diff: {result.get('max_rel_diff', 'N/A'):.2e}\n")
                
                f.write("\nDC Results:\n")
                for matrix, result in comparison.get('dc_results', {}).items():
                    f.write(f"  {matrix}:\n")
                    f.write(f"    Match: {result.get('match', 'N/A')}\n")
                    f.write(f"    Max abs diff: {result.get('max_abs_diff', 'N/A'):.2e}\n")
                    f.write(f"    Max rel diff: {result.get('max_rel_diff', 'N/A'):.2e}\n")
                
                f.write("\n")
        
        print(f"\nDetailed report saved to: {report_file}")
    
    return all_comparisons


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) >= 3:
        matlab_file = sys.argv[1]
        python_file = sys.argv[2]
    else:
        matlab_file = 'matlab_results.mat'
        python_file = 'pyacdc_results.pkl'
    
    print(f"Comparing results:")
    print(f"  MATLAB: {matlab_file}")
    print(f"  Python: {python_file}")
    
    try:
        comparisons = compare_all_tests(
            matlab_file,
            python_file,
            rtol=1e-5,
            atol=1e-8,
            save_report=True,
            report_file='comparison_report.txt'
        )
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("\nUsage: python compare_results.py [matlab_file] [python_file]")
