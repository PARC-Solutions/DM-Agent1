"""Base class and utilities for performance testing the Medical Billing Denial Agent."""

import time
import statistics
import unittest
from functools import wraps
from typing import List, Dict, Any, Callable, Optional, Type
import json
import os
import datetime

class PerformanceTestBase(unittest.TestCase):
    """Base class for all performance tests.
    
    Provides utilities for measuring and recording performance metrics,
    as well as comparing against baseline performance expectations.
    """
    
    # Default thresholds
    DEFAULT_RESPONSE_TIME_THRESHOLD = 5.0  # seconds
    DEFAULT_THROUGHPUT_THRESHOLD = 10  # requests per minute
    DEFAULT_MEMORY_USAGE_THRESHOLD = 500  # MB
    
    # Test categories
    CATEGORY_AGENT_RESPONSE = "agent_response"
    CATEGORY_DOCUMENT_PROCESSING = "document_processing"
    CATEGORY_KNOWLEDGE_ACCESS = "knowledge_access"
    CATEGORY_WORKFLOW_EXECUTION = "workflow_execution"
    
    def setUp(self):
        """Set up the performance test environment."""
        self.results = []
        self.test_start_time = time.time()
        self.baseline_data = self._load_baseline_data()
        
    def tearDown(self):
        """Clean up after test execution and record results."""
        self.test_end_time = time.time()
        self.test_duration = self.test_end_time - self.test_start_time
        
        # Save results if any were collected
        if self.results:
            self._save_results()
    
    def _load_baseline_data(self) -> Dict[str, Any]:
        """Load baseline performance data for comparison.
        
        Returns:
            Dict containing baseline metrics
        """
        baseline_path = os.path.join(
            os.path.dirname(__file__), 
            "baselines", 
            f"{self.__class__.__name__}_baseline.json"
        )
        
        if os.path.exists(baseline_path):
            try:
                with open(baseline_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load baseline data: {e}")
        
        # Return empty baseline if file doesn't exist or couldn't be read
        return {}
    
    def _save_results(self):
        """Save performance test results for future comparison."""
        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(
            results_dir,
            f"{self.__class__.__name__}_{timestamp}.json"
        )
        
        result_data = {
            "test_name": self.__class__.__name__,
            "timestamp": timestamp,
            "duration": self.test_duration,
            "results": self.results,
            "summary": self._calculate_summary()
        }
        
        with open(results_path, 'w') as f:
            json.dump(result_data, f, indent=2)
            
        print(f"Performance results saved to {results_path}")
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics from test results.
        
        Returns:
            Dict containing summary metrics
        """
        if not self.results:
            return {}
            
        # Group results by metric
        metrics = {}
        for result in self.results:
            metric = result["metric"]
            if metric not in metrics:
                metrics[metric] = []
            metrics[metric].append(result["value"])
        
        # Calculate statistics for each metric
        summary = {}
        for metric, values in metrics.items():
            summary[metric] = {
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values)
            }
            
            # Add standard deviation if we have enough values
            if len(values) > 1:
                summary[metric]["std_dev"] = statistics.stdev(values)
                
            # Add comparison to baseline if available
            if self.baseline_data and metric in self.baseline_data:
                baseline = self.baseline_data[metric]["mean"]
                current = summary[metric]["mean"]
                change_pct = ((current - baseline) / baseline) * 100
                summary[metric]["baseline_comparison"] = {
                    "baseline": baseline,
                    "change_pct": change_pct,
                    "improved": change_pct < 0 if metric != "throughput" else change_pct > 0
                }
                
        return summary
    
    def measure_time(self, func: Callable, *args, **kwargs) -> float:
        """Measure execution time of a function.
        
        Args:
            func: Function to measure
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Execution time in seconds
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        return execution_time, result
    
    def record_metric(self, metric: str, value: float, category: str, 
                     test_case: str, threshold: Optional[float] = None):
        """Record a performance metric.
        
        Args:
            metric: Name of the metric (e.g., 'response_time', 'throughput')
            value: Measured value
            category: Test category
            test_case: Specific test case identifier
            threshold: Optional threshold value for pass/fail determination
        """
        result = {
            "timestamp": time.time(),
            "metric": metric,
            "value": value,
            "category": category,
            "test_case": test_case
        }
        
        if threshold is not None:
            if metric in ["throughput"]:
                # For throughput, higher is better
                result["passed"] = value >= threshold
            else:
                # For response time, memory usage, etc., lower is better
                result["passed"] = value <= threshold
            result["threshold"] = threshold
        
        self.results.append(result)
        
        # Log the result
        threshold_info = f" (threshold: {threshold})" if threshold is not None else ""
        pass_info = ""
        if threshold is not None:
            pass_info = " - PASSED" if result["passed"] else " - FAILED"
        
        print(f"{category} - {test_case} - {metric}: {value}{threshold_info}{pass_info}")
        
        return result
    
    def assert_performance_metric(self, result: Dict[str, Any], 
                                  message: Optional[str] = None):
        """Assert that a performance metric meets its threshold.
        
        Args:
            result: Result dictionary from record_metric
            message: Optional message for assertion failure
        """
        if "passed" not in result:
            return
            
        if message is None:
            message = (f"Performance metric '{result['metric']}' failed: "
                      f"value={result['value']}, threshold={result['threshold']}")
                
        self.assertTrue(result["passed"], message)


def performance_test(category: str, test_case: str, threshold: Optional[float] = None):
    """Decorator for measuring function performance.
    
    Args:
        category: Test category
        test_case: Specific test case identifier
        threshold: Optional threshold value for pass/fail determination
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not isinstance(self, PerformanceTestBase):
                raise TypeError("Performance test decorator can only be used on "
                              "methods of PerformanceTestBase subclasses")
                
            start_time = time.time()
            result = func(self, *args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Use the provided threshold or a default based on category
            actual_threshold = threshold
            if actual_threshold is None:
                if category == PerformanceTestBase.CATEGORY_AGENT_RESPONSE:
                    actual_threshold = self.DEFAULT_RESPONSE_TIME_THRESHOLD
                elif category == PerformanceTestBase.CATEGORY_DOCUMENT_PROCESSING:
                    actual_threshold = self.DEFAULT_RESPONSE_TIME_THRESHOLD * 2
                else:
                    actual_threshold = self.DEFAULT_RESPONSE_TIME_THRESHOLD
            
            # Record the performance metric
            perf_result = self.record_metric(
                metric="response_time",
                value=execution_time,
                category=category,
                test_case=test_case,
                threshold=actual_threshold
            )
            
            # Assert that performance meets the threshold
            self.assert_performance_metric(perf_result)
            
            return result
        return wrapper
    return decorator
