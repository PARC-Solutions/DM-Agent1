#!/usr/bin/env python3
"""Runner script for the Medical Billing Denial Agent evaluation framework."""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
import datetime

# Add the project root directory to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.pipeline import EvaluationPipeline, run_evaluation
from evaluation.metrics import EvaluationMetric

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("evaluation_runner")

def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Run evaluation for the Medical Billing Denial Agent"
    )
    
    parser.add_argument(
        "--scenarios-dir",
        default="evaluation/benchmark_data",
        help="Directory containing test scenarios (default: evaluation/benchmark_data)"
    )
    
    parser.add_argument(
        "--results-dir",
        default="evaluation/results",
        help="Directory to save evaluation results (default: evaluation/results)"
    )
    
    parser.add_argument(
        "--scenario-file",
        help="Path to a specific scenario file to evaluate (instead of a directory)"
    )
    
    parser.add_argument(
        "--scenario-id",
        help="ID of a specific scenario to evaluate (must be used with --scenario-file)"
    )
    
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run scenarios sequentially (default: parallel execution)"
    )
    
    parser.add_argument(
        "--metrics",
        nargs="*",
        help="Specific metrics to evaluate (space-separated list of metric names)"
    )
    
    parser.add_argument(
        "--list-metrics",
        action="store_true",
        help="List available evaluation metrics and exit"
    )
    
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only output the summary report, not individual scenario results"
    )
    
    return parser.parse_args()

def list_available_metrics():
    """Print a list of available evaluation metrics."""
    print("\nAvailable Evaluation Metrics:\n")
    
    for metric in EvaluationMetric:
        print(f"- {metric.value}: {metric.name}")
    
    print("\nUse these metric names with the --metrics option to evaluate specific metrics.")

def load_single_scenario(file_path: str, scenario_id: Optional[str] = None) -> Dict[str, Any]:
    """Load a single scenario from a file.
    
    Args:
        file_path: Path to the scenario file
        scenario_id: Optional ID of a specific scenario to load
        
    Returns:
        Dictionary mapping scenario IDs to scenarios
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        scenarios = {}
        
        # Handle single scenario or list of scenarios
        if isinstance(data, list):
            for scenario_data in data:
                if scenario_id is None or scenario_data.get("scenario_id") == scenario_id:
                    scenarios[scenario_data["scenario_id"]] = scenario_data
        else:
            if scenario_id is None or data.get("scenario_id") == scenario_id:
                scenarios[data["scenario_id"]] = data
        
        if scenario_id and not scenarios:
            logger.error(f"Scenario with ID '{scenario_id}' not found in file {file_path}")
            sys.exit(1)
        
        return scenarios
    
    except Exception as e:
        logger.error(f"Error loading scenario from {file_path}: {e}")
        sys.exit(1)

def main():
    """Run the evaluation framework based on command-line arguments."""
    args = parse_arguments()
    
    # List metrics if requested
    if args.list_metrics:
        list_available_metrics()
        return
    
    # Parse metrics if specified
    metrics_to_evaluate = None
    if args.metrics:
        try:
            metrics_to_evaluate = [EvaluationMetric(m) for m in args.metrics]
        except ValueError as e:
            logger.error(f"Invalid metric specified: {e}")
            logger.info("Use --list-metrics to see available metrics")
            return
    
    # Handle single scenario file evaluation
    if args.scenario_file:
        if not os.path.exists(args.scenario_file):
            logger.error(f"Scenario file not found: {args.scenario_file}")
            return
        
        # Create temporary directory for the single scenario
        temp_dir = os.path.join(
            os.path.dirname(args.scenarios_dir),
            f"temp_scenarios_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        os.makedirs(temp_dir, exist_ok=True)
        
        # Load and save the scenario to the temporary directory
        scenarios = load_single_scenario(args.scenario_file, args.scenario_id)
        if not scenarios:
            logger.error("No scenarios found in the specified file")
            return
        
        temp_file = os.path.join(temp_dir, "temp_scenario.json")
        with open(temp_file, 'w') as f:
            json.dump(list(scenarios.values()), f, indent=2)
        
        # Update scenarios directory to the temporary one
        scenarios_dir = temp_dir
    else:
        scenarios_dir = args.scenarios_dir
    
    logger.info(f"Starting evaluation with scenarios from {scenarios_dir}")
    logger.info(f"Results will be saved to {args.results_dir}")
    
    # Create the pipeline and run evaluation
    pipeline = EvaluationPipeline(
        scenarios_dir=scenarios_dir,
        results_dir=args.results_dir,
        metrics_to_evaluate=metrics_to_evaluate,
        parallel_execution=not args.sequential
    )
    
    results = pipeline.evaluate_all()
    
    # Clean up temporary directory if created
    if args.scenario_file and os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)
    
    logger.info("Evaluation complete")
    
    # Print out number of scenarios evaluated
    print(f"\nEvaluated {len(results)} scenarios.")
    print(f"Results saved to {args.results_dir}")

if __name__ == "__main__":
    main()
