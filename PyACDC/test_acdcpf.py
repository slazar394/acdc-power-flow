"""Test script to run sequential AC/DC power flow simulations.

PyACDC - Python port of MatACDC
Converted from MATLAB by Lazar Scekic
"""
from runacdcpf import runacdcpf
from macdcoption import macdcoption

import pickle


def test_acdcpf(save_results=True, output_file='pyacdc_results.pkl'):
    """Run AC/DC power flow test cases.
    
    Args:
        save_results: If True, save results to pickle file
        output_file: Path to save results
        
    Returns:
        dict: Dictionary containing all test results
    """
    print("=" * 80)
    print("PyACDC Test Suite")
    print("=" * 80)
    
    # Define options
    mdopt = macdcoption()
    mdopt[12] = 0  # no output info
    
    results = {}
    
    # Test 1: Voltage slack control
    print('\n> Test 1: Voltage slack control')
    try:
        resultsac, resultsdc, converged, timecalc = runacdcpf(
            'Cases/PowerFlowAC/case5_stagg',
            'Cases/PowerFlowDC/case5_stagg_MTDCslack',
            mdopt
        )
        results['test1_slack'] = {
            'resultsac': resultsac,
            'resultsdc': resultsdc,
            'converged': converged,
            'timecalc': timecalc,
            'case_ac': 'case5_stagg',
            'case_dc': 'case5_stagg_MTDCslack'
        }
        print(f'   -> Done. Converged: {converged}, Time: {timecalc:.4f}s')
    except Exception as e:
        print(f'   -> FAILED: {e}')
        results['test1_slack'] = {'error': str(e)}
    
    # Test 2: Voltage droop control
    print('\n> Test 2: Voltage droop control')
    try:
        resultsac, resultsdc, converged, timecalc = runacdcpf(
            'Cases/PowerFlowAC/case5_stagg',
            'Cases/PowerFlowDC/case5_stagg_MTDCdroop',
            mdopt
        )
        results['test2_droop'] = {
            'resultsac': resultsac,
            'resultsdc': resultsdc,
            'converged': converged,
            'timecalc': timecalc,
            'case_ac': 'case5_stagg',
            'case_dc': 'case5_stagg_MTDCdroop'
        }
        print(f'   -> Done. Converged: {converged}, Time: {timecalc:.4f}s')
    except Exception as e:
        print(f'   -> FAILED: {e}')
        results['test2_droop'] = {'error': str(e)}
    
    # Test 3: Infinite grid
    print('\n> Test 3: Infinite grid')
    try:
        resultsac, resultsdc, converged, timecalc = runacdcpf(
            'Cases/PowerFlowAC/case3_inf',
            'Cases/PowerFlowDC/case5_stagg_MTDCdroop',
            mdopt
        )
        results['test3_inf'] = {
            'resultsac': resultsac,
            'resultsdc': resultsdc,
            'converged': converged,
            'timecalc': timecalc,
            'case_ac': 'case3_inf',
            'case_dc': 'case5_stagg_MTDCdroop'
        }
        print(f'   -> Done. Converged: {converged}, Time: {timecalc:.4f}s')
    except Exception as e:
        print(f'   -> FAILED: {e}')
        results['test3_inf'] = {'error': str(e)}
    
    # Test 4: Multiple AC and DC systems
    print('\n> Test 4: Multiple AC and DC systems')
    try:
        resultsac, resultsdc, converged, timecalc = runacdcpf(
            'Cases/PowerFlowAC/case24_ieee_rts1996_3zones',
            'Cases/PowerFlowDC/case24_ieee_rts1996_MTDC',
            mdopt
        )
        results['test4_multi'] = {
            'resultsac': resultsac,
            'resultsdc': resultsdc,
            'converged': converged,
            'timecalc': timecalc,
            'case_ac': 'case24_ieee_rts1996_3zones',
            'case_dc': 'case24_ieee_rts1996_MTDC'
        }
        print(f'   -> Done. Converged: {converged}, Time: {timecalc:.4f}s')
    except Exception as e:
        print(f'   -> FAILED: {e}')
        results['test4_multi'] = {'error': str(e)}
    
    print('\n' + '=' * 80)
    print('Test Suite Complete')
    print('=' * 80)
    
    # Print summary
    print('\nSummary:')
    for test_name, test_result in results.items():
        if 'error' in test_result:
            print(f'  {test_name}: FAILED')
        else:
            status = 'PASS' if test_result['converged'] else 'NO CONVERGENCE'
            print(f'  {test_name}: {status}')
    
    # Save results
    if save_results:
        with open(output_file, 'wb') as f:
            pickle.dump(results, f)
        print(f'\nResults saved to: {output_file}')
    
    return results


if __name__ == '__main__':
    results = test_acdcpf(save_results=True, output_file='pyacdc_results.pkl')
