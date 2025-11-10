#!/usr/bin/env python
"""Automated validation workflow for PyACDC.

This script automates the complete validation process:
1. Runs Python tests
2. Compares with MATLAB results (if available)
3. Generates reports

Usage:
    python run_validation.py [options]

Options:
    --matlab-results PATH    Path to MATLAB results file (default: matlab_results.mat)
    --python-results PATH    Path to save Python results (default: pyacdc_results.pkl)
    --run-tests             Run Python tests (default: True)
    --compare               Compare with MATLAB results (default: True if MATLAB file exists)
    --detailed TEST         Run detailed comparison for specific test
    --tolerance TOL         Tolerance for comparisons (default: 1e-5)
    --help                  Show this help message
"""
import os
import sys
import argparse
from pathlib import Path


def run_python_tests(output_file):
    """Run Python test suite."""
    print("\n" + "=" * 80)
    print("Running PyACDC Tests")
    print("=" * 80)
    
    try:
        from test_acdcpf import test_acdcpf
        results = test_acdcpf(save_results=True, output_file=output_file)
        return results
    except Exception as e:
        print(f"ERROR running tests: {e}")
        import traceback
        traceback.print_exc()
        return None


def compare_results(matlab_file, python_file, tolerance):
    """Compare MATLAB and Python results."""
    print("\n" + "=" * 80)
    print("Comparing Results")
    print("=" * 80)
    
    if not os.path.exists(matlab_file):
        print(f"WARNING: MATLAB results file not found: {matlab_file}")
        print("Skipping comparison. Run MATLAB tests first using save_matlab_results.m")
        return None
    
    try:
        from compare_results import compare_all_tests
        comparisons = compare_all_tests(
            matlab_file,
            python_file,
            rtol=tolerance,
            atol=tolerance * 100,
            save_report=True,
            report_file='comparison_report.txt'
        )
        return comparisons
    except Exception as e:
        print(f"ERROR in comparison: {e}")
        import traceback
        traceback.print_exc()
        return None


def detailed_comparison(matlab_file, python_file, test_name, tolerance):
    """Run detailed comparison for specific test."""
    print("\n" + "=" * 80)
    print(f"Detailed Comparison - {test_name}")
    print("=" * 80)
    
    try:
        from detailed_comparison import detailed_comparison as run_detailed
        run_detailed(matlab_file, python_file, test_name, tolerance)
    except Exception as e:
        print(f"ERROR in detailed comparison: {e}")
        import traceback
        traceback.print_exc()


def print_summary(test_results, comparison_results):
    """Print summary of validation results."""
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    if test_results:
        print("\nPython Tests:")
        for test_name, test_data in test_results.items():
            if 'error' in test_data:
                status = "FAILED"
            elif test_data.get('converged', False):
                status = "PASS"
            else:
                status = "NO CONVERGENCE"
            print(f"  {test_name:20s}: {status}")
    
    if comparison_results:
        print("\nComparison with MATLAB:")
        for test_name, comp_data in comparison_results.items():
            status = comp_data.get('status', 'UNKNOWN')
            
            # Check if differences are within tolerance
            all_diffs = []
            for results in ['ac_results', 'dc_results']:
                if results in comp_data:
                    for matrix, result in comp_data[results].items():
                        if 'max_abs_diff' in result:
                            all_diffs.append(result['max_abs_diff'])
            
            max_diff = max(all_diffs) if all_diffs else 0
            
            if status == 'PASS':
                print(f"  {test_name:20s}: ✓ PASS (max diff: {max_diff:.2e})")
            elif status == 'DIFFERENCES_FOUND':
                print(f"  {test_name:20s}: ⚠ DIFFERENCES (max diff: {max_diff:.2e})")
            else:
                print(f"  {test_name:20s}: ✗ {status}")
    
    print("\n" + "=" * 80)


def main():
    """Main validation workflow."""
    parser = argparse.ArgumentParser(
        description='Automated validation workflow for PyACDC',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--matlab-results',
        default='matlab_results.mat',
        help='Path to MATLAB results file (default: matlab_results.mat)'
    )
    
    parser.add_argument(
        '--python-results',
        default='pyacdc_results.pkl',
        help='Path to save Python results (default: pyacdc_results.pkl)'
    )
    
    parser.add_argument(
        '--no-run-tests',
        action='store_true',
        help='Skip running Python tests'
    )
    
    parser.add_argument(
        '--no-compare',
        action='store_true',
        help='Skip comparison with MATLAB results'
    )
    
    parser.add_argument(
        '--detailed',
        metavar='TEST',
        help='Run detailed comparison for specific test (e.g., test1_slack)'
    )
    
    parser.add_argument(
        '--tolerance',
        type=float,
        default=1e-5,
        help='Tolerance for comparisons (default: 1e-5)'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("PyACDC Validation Workflow")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  MATLAB results: {args.matlab_results}")
    print(f"  Python results: {args.python_results}")
    print(f"  Run tests: {not args.no_run_tests}")
    print(f"  Compare: {not args.no_compare}")
    print(f"  Tolerance: {args.tolerance}")
    
    test_results = None
    comparison_results = None
    
    # Run Python tests
    if not args.no_run_tests:
        test_results = run_python_tests(args.python_results)
        
        if test_results is None:
            print("\nERROR: Python tests failed. Aborting.")
            return 1
    
    # Compare with MATLAB
    if not args.no_compare:
        if os.path.exists(args.python_results):
            comparison_results = compare_results(
                args.matlab_results,
                args.python_results,
                args.tolerance
            )
        else:
            print(f"\nWARNING: Python results not found: {args.python_results}")
            print("Run tests first or specify existing results file.")
    
    # Detailed comparison
    if args.detailed:
        if os.path.exists(args.python_results) and os.path.exists(args.matlab_results):
            detailed_comparison(
                args.matlab_results,
                args.python_results,
                args.detailed,
                args.tolerance
            )
        else:
            print(f"\nERROR: Cannot run detailed comparison.")
            print(f"  Python results exist: {os.path.exists(args.python_results)}")
            print(f"  MATLAB results exist: {os.path.exists(args.matlab_results)}")
    
    # Print summary
    print_summary(test_results, comparison_results)
    
    # Check if validation passed
    if comparison_results:
        all_pass = all(
            comp.get('status') == 'PASS' 
            for comp in comparison_results.values()
        )
        
        if all_pass:
            print("\n✓ VALIDATION PASSED: All tests match MATLAB results")
            return 0
        else:
            print("\n⚠ VALIDATION ISSUES: Some tests have differences")
            print("  Run with --detailed TEST_NAME for more information")
            return 1
    else:
        print("\n⚠ VALIDATION INCOMPLETE: Comparison not performed")
        return 0


if __name__ == '__main__':
    sys.exit(main())
