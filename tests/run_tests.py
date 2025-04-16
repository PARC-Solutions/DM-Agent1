#!/usr/bin/env python3
"""Test runner for the Medical Billing Denial Agent."""

import os
import sys
import argparse
import unittest
import logging
import json
import time
import datetime
from typing import Dict, List, Set, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_runner")

def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Run tests for the Medical Billing Denial Agent"
    )
    
    parser.add_argument(
        "--test-types",
        nargs="*",
        choices=["unit", "integration", "performance", "e2e", "security", "all"],
        default=["unit"],
        help="Types of tests to run (default: unit)"
    )
    
    parser.add_argument(
        "--pattern",
        default="test_*.py",
        help="Pattern for test file names (default: test_*.py)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--output-dir",
        default="test_results",
        help="Directory to save test results (default: test_results)"
    )
    
    parser.add_argument(
        "--junit-xml",
        action="store_true",
        help="Generate JUnit XML report"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--tests",
        nargs="*",
        help="Specific test files or test names to run"
    )
    
    return parser.parse_args()

def get_test_dirs(test_types: List[str]) -> Dict[str, str]:
    """Get test directories for the specified test types.
    
    Args:
        test_types: List of test types to run
    
    Returns:
        Dictionary mapping test types to directories
    """
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    test_dirs = {
        "unit": os.path.join(base_dir, "tests", "unit"),
        "integration": os.path.join(base_dir, "tests", "integration"),
        "performance": os.path.join(base_dir, "tests", "performance"),
        "e2e": os.path.join(base_dir, "tests", "e2e"),
        "security": os.path.join(base_dir, "tests", "security")
    }
    
    if "all" in test_types:
        return test_dirs
    
    return {t: d for t, d in test_dirs.items() if t in test_types}

def discover_tests(
    test_dirs: Dict[str, str],
    pattern: str,
    specific_tests: Optional[List[str]] = None
) -> Dict[str, unittest.TestSuite]:
    """Discover tests in the specified directories.
    
    Args:
        test_dirs: Dictionary mapping test types to directories
        pattern: Pattern for test file names
        specific_tests: Optional list of specific test files or test names to run
    
    Returns:
        Dictionary mapping test types to test suites
    """
    test_suites = {}
    
    for test_type, test_dir in test_dirs.items():
        if not os.path.exists(test_dir):
            logger.warning(f"Test directory not found: {test_dir}")
            continue
            
        logger.info(f"Discovering {test_type} tests in {test_dir}")
        
        if specific_tests:
            # Filter specific tests for this test type
            suite = unittest.TestSuite()
            
            for test_spec in specific_tests:
                # Check if it's a file path
                if os.path.exists(test_spec):
                    # Convert file path to module path
                    if test_spec.endswith(".py"):
                        test_spec = test_spec[:-3]
                    test_spec = test_spec.replace(os.path.sep, ".")
                
                # Try to load the test
                try:
                    if "." in test_spec:
                        # Specific test method or class
                        tests = unittest.defaultTestLoader.loadTestsFromName(test_spec)
                    else:
                        # Test module
                        tests = unittest.defaultTestLoader.loadTestsFromName(f"tests.{test_type}.{test_spec}")
                    
                    suite.addTests(tests)
                except (ImportError, AttributeError):
                    logger.warning(f"Could not find test: {test_spec}")
        else:
            # Discover all tests in the directory
            suite = unittest.defaultTestLoader.discover(test_dir, pattern=pattern)
        
        if suite.countTestCases() > 0:
            test_suites[test_type] = suite
    
    return test_suites

def setup_junit_xml():
    """Set up JUnit XML reporting.
    
    Returns:
        XMLTestRunner if available, or None
    """
    try:
        from xmlrunner import XMLTestRunner
        return XMLTestRunner
    except ImportError:
        logger.warning("xmlrunner not installed. Run 'pip install unittest-xml-reporting' for JUnit XML support.")
        return None

def setup_coverage():
    """Set up code coverage reporting.
    
    Returns:
        Coverage object if available, or None
    """
    try:
        import coverage
        cov = coverage.Coverage(
            source=["agent"],
            omit=["*/tests/*", "*/venv/*", "*/env/*"]
        )
        cov.start()
        return cov
    except ImportError:
        logger.warning("coverage not installed. Run 'pip install coverage' for code coverage support.")
        return None

def run_tests(
    test_suites: Dict[str, unittest.TestSuite],
    output_dir: str,
    verbose: bool = False,
    junit_xml: bool = False,
    coverage_obj: Any = None
) -> Dict[str, Dict[str, Any]]:
    """Run the test suites.
    
    Args:
        test_suites: Dictionary mapping test types to test suites
        output_dir: Directory to save test results
        verbose: Whether to use verbose output
        junit_xml: Whether to generate JUnit XML report
        coverage_obj: Coverage object if coverage is enabled
    
    Returns:
        Dictionary mapping test types to test results
    """
    if junit_xml:
        XMLTestRunner = setup_junit_xml()
    
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    total_tests = 0
    total_errors = 0
    total_failures = 0
    total_skipped = 0
    total_time = 0
    
    for test_type, suite in test_suites.items():
        logger.info(f"Running {test_type} tests ({suite.countTestCases()} test cases)")
        
        output_subdir = os.path.join(output_dir, test_type)
        os.makedirs(output_subdir, exist_ok=True)
        
        start_time = time.time()
        
        if junit_xml and XMLTestRunner:
            result = XMLTestRunner(
                output=output_subdir,
                verbosity=2 if verbose else 1
            ).run(suite)
        else:
            runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
            result = runner.run(suite)
        
        end_time = time.time()
        
        # Store the test result
        results[test_type] = {
            "tests": suite.countTestCases(),
            "errors": len(result.errors),
            "failures": len(result.failures),
            "skipped": len(result.skipped) if hasattr(result, "skipped") else 0,
            "time": end_time - start_time
        }
        
        # Update totals
        total_tests += results[test_type]["tests"]
        total_errors += results[test_type]["errors"]
        total_failures += results[test_type]["failures"]
        total_skipped += results[test_type]["skipped"]
        total_time += results[test_type]["time"]
    
    # Generate coverage report
    if coverage_obj:
        coverage_obj.stop()
        coverage_obj.save()
        
        # Generate HTML report
        coverage_dir = os.path.join(output_dir, "coverage")
        os.makedirs(coverage_dir, exist_ok=True)
        coverage_obj.html_report(directory=coverage_dir)
        
        # Generate console report
        coverage_report = coverage_obj.report()
        
        # Add coverage data to results
        results["coverage"] = {
            "report_directory": coverage_dir,
            "report": str(coverage_report)
        }
    
    # Generate summary report
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_tests": total_tests,
        "total_errors": total_errors,
        "total_failures": total_failures,
        "total_skipped": total_skipped,
        "total_time": total_time,
        "results_by_type": results
    }
    
    with open(os.path.join(output_dir, "summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    
    return results

def print_test_summary(results: Dict[str, Dict[str, Any]]):
    """Print a summary of test results.
    
    Args:
        results: Dictionary mapping test types to test results
    """
    total_tests = sum(r["tests"] for r in results.values())
    total_errors = sum(r["errors"] for r in results.values())
    total_failures = sum(r["failures"] for r in results.values())
    total_skipped = sum(r["skipped"] for r in results.values())
    total_time = sum(r["time"] for r in results.values())
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    # Print results for each test type
    for test_type, result in results.items():
        if test_type == "coverage":
            continue
            
        status = "PASSED"
        if result["errors"] > 0 or result["failures"] > 0:
            status = "FAILED"
        
        print(f"{test_type.upper()} TESTS: {status}")
        print(f"  Tests: {result['tests']}")
        print(f"  Errors: {result['errors']}")
        print(f"  Failures: {result['failures']}")
        print(f"  Skipped: {result['skipped']}")
        print(f"  Time: {result['time']:.2f}s")
        print()
    
    # Print overall summary
    overall_status = "PASSED"
    if total_errors > 0 or total_failures > 0:
        overall_status = "FAILED"
    
    print("="*80)
    print(f"OVERALL: {overall_status}")
    print(f"  Total tests: {total_tests}")
    print(f"  Total errors: {total_errors}")
    print(f"  Total failures: {total_failures}")
    print(f"  Total skipped: {total_skipped}")
    print(f"  Total time: {total_time:.2f}s")
    
    # Print coverage info if available
    if "coverage" in results:
        print()
        print("COVERAGE REPORT:")
        print(f"  Report directory: {results['coverage']['report_directory']}")
    
    print("="*80 + "\n")

def main():
    """Run the test runner."""
    args = parse_arguments()
    
    # Get test directories
    test_dirs = get_test_dirs(args.test_types)
    
    # Discover tests
    test_suites = discover_tests(test_dirs, args.pattern, args.tests)
    
    if not test_suites:
        logger.error("No tests discovered")
        return 1
    
    # Set up coverage
    coverage_obj = setup_coverage() if args.coverage else None
    
    # Run tests
    results = run_tests(
        test_suites,
        args.output_dir,
        args.verbose,
        args.junit_xml,
        coverage_obj
    )
    
    # Print summary
    print_test_summary(results)
    
    # Check for test failures
    total_errors = sum(r["errors"] for r in results.values() if isinstance(r, dict) and "errors" in r)
    total_failures = sum(r["failures"] for r in results.values() if isinstance(r, dict) and "failures" in r)
    
    return 1 if total_errors > 0 or total_failures > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
