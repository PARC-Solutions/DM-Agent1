"""Parameter tuning framework for the Medical Billing Denial Agent."""

import os
import json
import time
import datetime
import uuid
import logging
import copy
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
import concurrent.futures

from evaluation.pipeline import EvaluationPipeline, TestScenario

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("parameter_tuning")

class ModelParameter:
    """Representation of a model parameter for tuning."""
    
    def __init__(
        self,
        name: str,
        parameter_type: str,
        default_value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        choices: Optional[List[Any]] = None,
        description: Optional[str] = None
    ):
        """Initialize a model parameter.
        
        Args:
            name: Parameter name
            parameter_type: Parameter type (float, int, bool, string, categorical)
            default_value: Default value for the parameter
            min_value: Optional minimum value for numerical parameters
            max_value: Optional maximum value for numerical parameters
            choices: Optional list of valid values for categorical parameters
            description: Optional description of the parameter
        """
        self.name = name
        self.parameter_type = parameter_type
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.choices = choices
        self.description = description
        
        # Validate parameter configuration
        self._validate()
    
    def _validate(self):
        """Validate parameter configuration."""
        # Check parameter type
        if self.parameter_type not in ["float", "int", "bool", "string", "categorical"]:
            raise ValueError(f"Invalid parameter type: {self.parameter_type}")
            
        # Check numerical parameters
        if self.parameter_type in ["float", "int"]:
            if self.min_value is not None and self.max_value is not None:
                if self.min_value > self.max_value:
                    raise ValueError(f"Min value ({self.min_value}) > max value ({self.max_value})")
                    
                if self.default_value < self.min_value or self.default_value > self.max_value:
                    raise ValueError(f"Default value ({self.default_value}) outside range [{self.min_value}, {self.max_value}]")
                    
        # Check categorical parameters
        if self.parameter_type == "categorical":
            if not self.choices:
                raise ValueError("Categorical parameter must have choices")
                
            if self.default_value not in self.choices:
                raise ValueError(f"Default value ({self.default_value}) not in choices: {self.choices}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameter to dictionary.
        
        Returns:
            Dictionary representation of the parameter
        """
        result = {
            "name": self.name,
            "parameter_type": self.parameter_type,
            "default_value": self.default_value
        }
        
        if self.min_value is not None:
            result["min_value"] = self.min_value
            
        if self.max_value is not None:
            result["max_value"] = self.max_value
            
        if self.choices:
            result["choices"] = self.choices
            
        if self.description:
            result["description"] = self.description
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelParameter':
        """Create parameter from dictionary.
        
        Args:
            data: Dictionary representation of parameter
            
        Returns:
            ModelParameter instance
        """
        return cls(
            name=data["name"],
            parameter_type=data["parameter_type"],
            default_value=data["default_value"],
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            choices=data.get("choices"),
            description=data.get("description")
        )

class ModelConfiguration:
    """Representation of a model configuration for tuning."""
    
    def __init__(
        self,
        config_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ):
        """Initialize a model configuration.
        
        Args:
            config_id: Configuration ID (generated if not provided)
            parameters: Dictionary of parameter values
            metadata: Optional metadata for the configuration
            description: Optional description of the configuration
        """
        self.config_id = config_id or str(uuid.uuid4())
        self.parameters = parameters or {}
        self.metadata = metadata or {}
        self.description = description
        self.timestamp = datetime.datetime.now().timestamp()
        self.evaluation_results = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "config_id": self.config_id,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "description": self.description,
            "timestamp": self.timestamp,
            "evaluation_results": self.evaluation_results
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """Create configuration from dictionary.
        
        Args:
            data: Dictionary representation of configuration
            
        Returns:
            ModelConfiguration instance
        """
        config = cls(
            config_id=data["config_id"],
            parameters=data["parameters"],
            metadata=data.get("metadata", {}),
            description=data.get("description")
        )
        
        config.timestamp = data.get("timestamp", datetime.datetime.now().timestamp())
        config.evaluation_results = data.get("evaluation_results", {})
        
        return config

class ParameterTuner:
    """Framework for tuning model parameters."""
    
    def __init__(
        self,
        base_configuration: ModelConfiguration,
        parameter_definitions: Dict[str, ModelParameter],
        evaluation_scenarios_dir: str,
        results_dir: str,
        max_concurrent_evaluations: int = 3
    ):
        """Initialize parameter tuner.
        
        Args:
            base_configuration: Base configuration to tune from
            parameter_definitions: Dictionary of parameter definitions
            evaluation_scenarios_dir: Directory containing evaluation scenarios
            results_dir: Directory to save tuning results
            max_concurrent_evaluations: Maximum number of concurrent evaluations
        """
        self.base_configuration = base_configuration
        self.parameter_definitions = parameter_definitions
        self.evaluation_scenarios_dir = evaluation_scenarios_dir
        self.results_dir = results_dir
        self.max_concurrent_evaluations = max_concurrent_evaluations
        
        # Create directories if they don't exist
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize parameters with default values if not in base configuration
        for param_name, param_def in parameter_definitions.items():
            if param_name not in self.base_configuration.parameters:
                self.base_configuration.parameters[param_name] = param_def.default_value
    
    def generate_configurations(
        self,
        parameters_to_tune: List[str],
        num_variations: int = 3,
        variation_strategy: str = "linear"
    ) -> List[ModelConfiguration]:
        """Generate variations of the base configuration.
        
        Args:
            parameters_to_tune: List of parameter names to tune
            num_variations: Number of variations to generate per parameter
            variation_strategy: Strategy for generating variations (linear or random)
            
        Returns:
            List of configuration variations
        """
        configurations = []
        
        # Add base configuration
        configurations.append(self.base_configuration)
        
        # Generate variations for each parameter
        for param_name in parameters_to_tune:
            if param_name not in self.parameter_definitions:
                logger.warning(f"Parameter {param_name} not found in definitions, skipping")
                continue
                
            param_def = self.parameter_definitions[param_name]
            variations = self._generate_parameter_variations(param_def, num_variations, variation_strategy)
            
            # Create a new configuration for each variation
            for variation_value in variations:
                config = copy.deepcopy(self.base_configuration)
                config.config_id = str(uuid.uuid4())
                config.parameters[param_name] = variation_value
                config.metadata = {
                    "varied_parameter": param_name,
                    "variation_strategy": variation_strategy,
                    "base_config_id": self.base_configuration.config_id
                }
                config.description = f"Variation of {param_name} = {variation_value}"
                
                configurations.append(config)
        
        return configurations
    
    def _generate_parameter_variations(
        self,
        param_def: ModelParameter,
        num_variations: int,
        strategy: str
    ) -> List[Any]:
        """Generate variations for a single parameter.
        
        Args:
            param_def: Parameter definition
            num_variations: Number of variations to generate
            strategy: Strategy for generating variations
            
        Returns:
            List of parameter values
        """
        import random
        
        if param_def.parameter_type == "bool":
            # Boolean has only two possible values
            return [True, False]
            
        elif param_def.parameter_type == "categorical":
            # For categorical, return all available choices
            return param_def.choices
            
        elif param_def.parameter_type in ["float", "int"]:
            # For numerical parameters, generate variations based on strategy
            if param_def.min_value is None or param_def.max_value is None:
                # Without range bounds, use multipliers around default
                default = param_def.default_value
                if strategy == "linear":
                    multipliers = [0.5, 0.75, 1.25, 1.5, 2.0][:num_variations]
                    return [default * m for m in multipliers]
                else:  # random
                    return [default * random.uniform(0.5, 2.0) for _ in range(num_variations)]
            else:
                # With range bounds, generate values within the range
                min_val, max_val = param_def.min_value, param_def.max_value
                if strategy == "linear":
                    step = (max_val - min_val) / (num_variations + 1)
                    values = [min_val + step * (i + 1) for i in range(num_variations)]
                else:  # random
                    values = [random.uniform(min_val, max_val) for _ in range(num_variations)]
                
                # Convert to int if needed
                if param_def.parameter_type == "int":
                    values = [int(v) for v in values]
                
                return values
                
        elif param_def.parameter_type == "string":
            # String variations not supported - return empty list
            logger.warning("String parameter variations not supported")
            return []
            
        else:
            logger.warning(f"Unsupported parameter type: {param_def.parameter_type}")
            return []
    
    def evaluate_configuration(
        self,
        configuration: ModelConfiguration,
        apply_config_func: Callable[[Dict[str, Any]], None]
    ) -> Dict[str, float]:
        """Evaluate a single configuration.
        
        Args:
            configuration: Configuration to evaluate
            apply_config_func: Function to apply configuration parameters
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info(f"Evaluating configuration {configuration.config_id}")
        
        # Apply configuration
        apply_config_func(configuration.parameters)
        
        # Create results directory for this configuration
        config_results_dir = os.path.join(
            self.results_dir,
            f"config_{configuration.config_id}"
        )
        os.makedirs(config_results_dir, exist_ok=True)
        
        # Run evaluation
        pipeline = EvaluationPipeline(
            scenarios_dir=self.evaluation_scenarios_dir,
            results_dir=config_results_dir,
            parallel_execution=True
        )
        
        results = pipeline.evaluate_all()
        
        # Extract summary metrics
        metrics = {}
        overall_scores = []
        category_scores = {}
        
        for result in results.values():
            summary = result.get_summary()
            overall_scores.append(summary["overall_score"])
            
            # Aggregate category scores
            for category, data in summary["by_category"].items():
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(data["average"])
        
        # Calculate averages
        import statistics
        
        metrics["overall_score"] = statistics.mean(overall_scores) if overall_scores else 0
        
        for category, scores in category_scores.items():
            metrics[f"category_{category}"] = statistics.mean(scores) if scores else 0
        
        # Store evaluation results in the configuration
        configuration.evaluation_results = metrics
        
        # Save configuration results
        self._save_configuration(configuration)
        
        return metrics
    
    def evaluate_configurations(
        self,
        configurations: List[ModelConfiguration],
        apply_config_func: Callable[[Dict[str, Any]], None]
    ) -> Dict[str, Dict[str, float]]:
        """Evaluate multiple configurations.
        
        Args:
            configurations: List of configurations to evaluate
            apply_config_func: Function to apply configuration parameters
            
        Returns:
            Dictionary mapping configuration IDs to evaluation metrics
        """
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_concurrent_evaluations
        ) as executor:
            # Create a copy of apply_config_func for each configuration
            future_to_config = {
                executor.submit(self.evaluate_configuration, config, apply_config_func): config
                for config in configurations
            }
            
            for future in concurrent.futures.as_completed(future_to_config):
                config = future_to_config[future]
                try:
                    metrics = future.result()
                    results[config.config_id] = metrics
                except Exception as e:
                    logger.error(f"Error evaluating configuration {config.config_id}: {e}")
        
        return results
    
    def _save_configuration(self, configuration: ModelConfiguration):
        """Save configuration to file.
        
        Args:
            configuration: Configuration to save
        """
        file_path = os.path.join(
            self.results_dir,
            f"config_{configuration.config_id}.json"
        )
        
        with open(file_path, 'w') as f:
            json.dump(configuration.to_dict(), f, indent=2)
            
        logger.info(f"Saved configuration to {file_path}")
    
    def find_best_configuration(
        self,
        evaluated_configs: Dict[str, Dict[str, float]],
        metric: str = "overall_score"
    ) -> Tuple[str, ModelConfiguration]:
        """Find the best configuration based on a metric.
        
        Args:
            evaluated_configs: Dictionary mapping configuration IDs to metrics
            metric: Metric to optimize
            
        Returns:
            Tuple of (config_id, configuration)
        """
        if not evaluated_configs:
            return None, None
            
        # Find config with highest metric value
        best_config_id = max(
            evaluated_configs.keys(),
            key=lambda cid: evaluated_configs[cid].get(metric, 0)
        )
        
        # Load the configuration
        config_path = os.path.join(
            self.results_dir,
            f"config_{best_config_id}.json"
        )
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            best_config = ModelConfiguration.from_dict(config_data)
            
        return best_config_id, best_config
    
    def generate_optimization_report(
        self,
        evaluated_configs: Dict[str, Dict[str, float]],
        metric: str = "overall_score"
    ) -> Dict[str, Any]:
        """Generate optimization report.
        
        Args:
            evaluated_configs: Dictionary mapping configuration IDs to metrics
            metric: Metric to compare
            
        Returns:
            Report dictionary
        """
        if not evaluated_configs:
            return {"error": "No configurations evaluated"}
            
        # Sort configurations by metric
        sorted_configs = sorted(
            evaluated_configs.items(),
            key=lambda x: x[1].get(metric, 0),
            reverse=True
        )
        
        # Extract parameter values
        config_params = {}
        for config_id, _ in sorted_configs:
            config_path = os.path.join(
                self.results_dir,
                f"config_{config_id}.json"
            )
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                config_params[config_id] = {
                    "parameters": config_data["parameters"],
                    "metadata": config_data.get("metadata", {})
                }
        
        # Generate report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "metric": metric,
            "num_configurations": len(evaluated_configs),
            "base_configuration": self.base_configuration.to_dict(),
            "results": [
                {
                    "config_id": config_id,
                    "parameters": config_params[config_id]["parameters"],
                    "metadata": config_params[config_id]["metadata"],
                    "metrics": metrics
                }
                for config_id, metrics in sorted_configs
            ]
        }
        
        # Identify best configuration
        best_config_id, _ = self.find_best_configuration(evaluated_configs, metric)
        report["best_configuration_id"] = best_config_id
        
        # Save report
        report_path = os.path.join(
            self.results_dir,
            f"optimization_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated optimization report at {report_path}")
        
        return report

def apply_default_configuration(parameters: Dict[str, Any]):
    """Apply default configuration to the model.
    
    This function serves as an example of how to apply configuration
    parameters to the actual model. In a real implementation, this
    would interact with the model's configuration.
    
    Args:
        parameters: Dictionary of parameter values
    """
    # This is a placeholder. In a real implementation, this would
    # apply the parameters to the model.
    logger.info(f"Applying configuration: {parameters}")
    
    # Example of parameter application:
    # - temperature affects randomness
    # - top_p affects diversity
    # - max_tokens affects response length
    # - etc.
    
    # Simulated delay to represent parameter application time
    time.sleep(0.5)

# Define standard model parameters
STANDARD_PARAMETERS = {
    "temperature": ModelParameter(
        name="temperature",
        parameter_type="float",
        default_value=0.7,
        min_value=0.0,
        max_value=1.0,
        description="Controls randomness in the model response. Higher values mean more random completions."
    ),
    "top_p": ModelParameter(
        name="top_p",
        parameter_type="float",
        default_value=0.9,
        min_value=0.0,
        max_value=1.0,
        description="Controls diversity of model response. 0.5 means half of probability mass is considered."
    ),
    "frequency_penalty": ModelParameter(
        name="frequency_penalty",
        parameter_type="float",
        default_value=0.0,
        min_value=-2.0,
        max_value=2.0,
        description="Penalizes repeated tokens. Positive values reduce repetition."
    ),
    "presence_penalty": ModelParameter(
        name="presence_penalty",
        parameter_type="float",
        default_value=0.0,
        min_value=-2.0,
        max_value=2.0,
        description="Penalizes new tokens based on their presence in the text so far. Positive values increase likelihood of diverse topics."
    ),
    "max_tokens": ModelParameter(
        name="max_tokens",
        parameter_type="int",
        default_value=1024,
        min_value=64,
        max_value=4096,
        description="Maximum number of tokens in the response."
    ),
    "response_format": ModelParameter(
        name="response_format",
        parameter_type="categorical",
        default_value="auto",
        choices=["auto", "json", "text"],
        description="Format of the model response."
    )
}

def create_default_configuration() -> ModelConfiguration:
    """Create default model configuration.
    
    Returns:
        Default model configuration
    """
    parameters = {
        param_name: param_def.default_value
        for param_name, param_def in STANDARD_PARAMETERS.items()
    }
    
    return ModelConfiguration(
        config_id="default",
        parameters=parameters,
        description="Default configuration with standard parameter values"
    )

def run_parameter_tuning(
    parameters_to_tune: List[str] = None,
    num_variations: int = 3,
    evaluation_scenarios_dir: str = "evaluation/benchmark_data",
    results_dir: str = "optimization/tuning_results"
):
    """Run parameter tuning process.
    
    Args:
        parameters_to_tune: List of parameters to tune
        num_variations: Number of variations per parameter
        evaluation_scenarios_dir: Directory containing evaluation scenarios
        results_dir: Directory to save tuning results
    """
    # Use default parameters if none specified
    if parameters_to_tune is None:
        parameters_to_tune = ["temperature", "top_p", "frequency_penalty"]
    
    # Create base configuration
    base_configuration = create_default_configuration()
    
    # Initialize tuner
    tuner = ParameterTuner(
        base_configuration=base_configuration,
        parameter_definitions=STANDARD_PARAMETERS,
        evaluation_scenarios_dir=evaluation_scenarios_dir,
        results_dir=results_dir
    )
    
    # Generate configuration variations
    configurations = tuner.generate_configurations(
        parameters_to_tune=parameters_to_tune,
        num_variations=num_variations
    )
    
    logger.info(f"Generated {len(configurations)} configurations")
    
    # Evaluate configurations
    evaluated_configs = tuner.evaluate_configurations(
        configurations=configurations,
        apply_config_func=apply_default_configuration
    )
    
    # Generate report
    report = tuner.generate_optimization_report(evaluated_configs)
    
    # Find best configuration
    best_config_id, best_config = tuner.find_best_configuration(evaluated_configs)
    
    logger.info(f"Best configuration: {best_config_id}")
    logger.info(f"Best configuration parameters: {best_config.parameters}")
    logger.info(f"Best configuration performance: {best_config.evaluation_results}")
    
    return report

if __name__ == "__main__":
    run_parameter_tuning()
