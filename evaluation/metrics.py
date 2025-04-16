"""Metrics definitions for evaluating agent responses."""

from enum import Enum
from typing import Dict, Any, List, Optional, Union, Callable
import json
import os
import re
import datetime
import statistics

class EvaluationMetric(Enum):
    """Enumeration of evaluation metrics with descriptions."""
    
    # Accuracy metrics
    DENIAL_CODE_ACCURACY = "denial_code_accuracy"
    REMEDIATION_RELEVANCE = "remediation_relevance"
    PROCEDURAL_ACCURACY = "procedural_accuracy"
    BILLING_RULE_ACCURACY = "billing_rule_accuracy"
    
    # Clarity metrics
    EXPLANATION_CLARITY = "explanation_clarity"
    INSTRUCTION_CLARITY = "instruction_clarity"
    
    # Completeness metrics
    INFORMATION_COMPLETENESS = "information_completeness"
    REMEDIATION_COMPLETENESS = "remediation_completeness"
    
    # Efficiency metrics
    RESPONSE_CONCISENESS = "response_conciseness"
    WORKFLOW_EFFICIENCY = "workflow_efficiency"
    
    # User experience metrics
    HELPFULNESS = "helpfulness"
    PROFESSIONALISM = "professionalism"
    USABILITY = "usability"

class MetricCategory(Enum):
    """Categories of evaluation metrics."""
    
    ACCURACY = "accuracy"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    EFFICIENCY = "efficiency"
    USER_EXPERIENCE = "user_experience"
    
    @classmethod
    def get_category_for_metric(cls, metric: EvaluationMetric) -> 'MetricCategory':
        """Get the category for a given metric.
        
        Args:
            metric: The evaluation metric
            
        Returns:
            The category the metric belongs to
        """
        category_map = {
            EvaluationMetric.DENIAL_CODE_ACCURACY: cls.ACCURACY,
            EvaluationMetric.REMEDIATION_RELEVANCE: cls.ACCURACY,
            EvaluationMetric.PROCEDURAL_ACCURACY: cls.ACCURACY,
            EvaluationMetric.BILLING_RULE_ACCURACY: cls.ACCURACY,
            
            EvaluationMetric.EXPLANATION_CLARITY: cls.CLARITY,
            EvaluationMetric.INSTRUCTION_CLARITY: cls.CLARITY,
            
            EvaluationMetric.INFORMATION_COMPLETENESS: cls.COMPLETENESS,
            EvaluationMetric.REMEDIATION_COMPLETENESS: cls.COMPLETENESS,
            
            EvaluationMetric.RESPONSE_CONCISENESS: cls.EFFICIENCY,
            EvaluationMetric.WORKFLOW_EFFICIENCY: cls.EFFICIENCY,
            
            EvaluationMetric.HELPFULNESS: cls.USER_EXPERIENCE,
            EvaluationMetric.PROFESSIONALISM: cls.USER_EXPERIENCE,
            EvaluationMetric.USABILITY: cls.USER_EXPERIENCE
        }
        
        return category_map.get(metric, cls.ACCURACY)

class ScoreRange(Enum):
    """Standard score ranges for metrics."""
    
    BINARY = "binary"  # 0 or 1
    SCALE_5 = "scale_5"  # 0-5 scale
    SCALE_10 = "scale_10"  # 0-10 scale
    PERCENTAGE = "percentage"  # 0-100%

class EvaluationScore:
    """Representation of an evaluation score."""
    
    def __init__(
        self, 
        metric: EvaluationMetric, 
        score: float,
        score_range: ScoreRange,
        evaluator: str,
        notes: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        """Initialize an evaluation score.
        
        Args:
            metric: The metric being evaluated
            score: The score value
            score_range: The range the score falls within
            evaluator: Identifier of who/what performed the evaluation
            notes: Optional notes on the score
            timestamp: Optional timestamp of when the evaluation was performed
        """
        self.metric = metric
        self.score = score
        self.score_range = score_range
        self.evaluator = evaluator
        self.notes = notes
        self.timestamp = timestamp or datetime.datetime.now().timestamp()
        
        # Validate score is within range
        self._validate_score()
        
    def _validate_score(self):
        """Validate that the score is within the specified range."""
        if self.score_range == ScoreRange.BINARY and self.score not in [0, 1]:
            raise ValueError(f"Binary score must be 0 or 1, got {self.score}")
        elif self.score_range == ScoreRange.SCALE_5 and (self.score < 0 or self.score > 5):
            raise ValueError(f"Scale-5 score must be between 0 and 5, got {self.score}")
        elif self.score_range == ScoreRange.SCALE_10 and (self.score < 0 or self.score > 10):
            raise ValueError(f"Scale-10 score must be between 0 and 10, got {self.score}")
        elif self.score_range == ScoreRange.PERCENTAGE and (self.score < 0 or self.score > 100):
            raise ValueError(f"Percentage score must be between 0 and 100, got {self.score}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the score to a dictionary representation.
        
        Returns:
            Dictionary representation of the score
        """
        return {
            "metric": self.metric.value,
            "score": self.score,
            "score_range": self.score_range.value,
            "evaluator": self.evaluator,
            "notes": self.notes,
            "timestamp": self.timestamp,
            "category": MetricCategory.get_category_for_metric(self.metric).value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationScore':
        """Create an EvaluationScore from a dictionary representation.
        
        Args:
            data: Dictionary representation of a score
            
        Returns:
            EvaluationScore instance
        """
        return cls(
            metric=EvaluationMetric(data["metric"]),
            score=data["score"],
            score_range=ScoreRange(data["score_range"]),
            evaluator=data["evaluator"],
            notes=data.get("notes"),
            timestamp=data.get("timestamp")
        )
    
    def normalize(self, target_range: ScoreRange = ScoreRange.PERCENTAGE) -> float:
        """Normalize the score to a target range.
        
        Args:
            target_range: The target range to normalize to
            
        Returns:
            Normalized score value
        """
        # First normalize to 0-1 scale
        normalized = self.score
        
        if self.score_range == ScoreRange.BINARY:
            normalized = self.score  # Already 0 or 1
        elif self.score_range == ScoreRange.SCALE_5:
            normalized = self.score / 5.0
        elif self.score_range == ScoreRange.SCALE_10:
            normalized = self.score / 10.0
        elif self.score_range == ScoreRange.PERCENTAGE:
            normalized = self.score / 100.0
            
        # Then convert to target range
        if target_range == ScoreRange.BINARY:
            return 1 if normalized >= 0.5 else 0
        elif target_range == ScoreRange.SCALE_5:
            return normalized * 5.0
        elif target_range == ScoreRange.SCALE_10:
            return normalized * 10.0
        elif target_range == ScoreRange.PERCENTAGE:
            return normalized * 100.0
            
        return normalized

class EvaluationResult:
    """Container for evaluation results for a specific scenario."""
    
    def __init__(
        self,
        scenario_id: str,
        scenario_type: str,
        scores: List[EvaluationScore],
        agent_response: str,
        expected_response: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize an evaluation result.
        
        Args:
            scenario_id: Identifier for the test scenario
            scenario_type: Type of scenario (e.g., 'denial_classification')
            scores: List of evaluation scores
            agent_response: The agent's response text
            expected_response: Optional expected or gold-standard response
            metadata: Optional additional metadata about the evaluation
        """
        self.scenario_id = scenario_id
        self.scenario_type = scenario_type
        self.scores = scores
        self.agent_response = agent_response
        self.expected_response = expected_response
        self.metadata = metadata or {}
        self.timestamp = datetime.datetime.now().timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the evaluation result to a dictionary representation.
        
        Returns:
            Dictionary representation of the evaluation result
        """
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type,
            "scores": [score.to_dict() for score in self.scores],
            "agent_response": self.agent_response,
            "expected_response": self.expected_response,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "summary": self.get_summary()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationResult':
        """Create an EvaluationResult from a dictionary representation.
        
        Args:
            data: Dictionary representation of an evaluation result
            
        Returns:
            EvaluationResult instance
        """
        return cls(
            scenario_id=data["scenario_id"],
            scenario_type=data["scenario_type"],
            scores=[EvaluationScore.from_dict(score) for score in data["scores"]],
            agent_response=data["agent_response"],
            expected_response=data.get("expected_response"),
            metadata=data.get("metadata", {})
        )
    
    def add_score(self, score: EvaluationScore):
        """Add a new evaluation score.
        
        Args:
            score: Evaluation score to add
        """
        self.scores.append(score)
    
    def get_score_by_metric(self, metric: EvaluationMetric) -> Optional[EvaluationScore]:
        """Get the evaluation score for a specific metric.
        
        Args:
            metric: The metric to get the score for
            
        Returns:
            The evaluation score, or None if not found
        """
        for score in self.scores:
            if score.metric == metric:
                return score
        return None
    
    def get_category_scores(self) -> Dict[MetricCategory, List[EvaluationScore]]:
        """Group scores by category.
        
        Returns:
            Dictionary mapping categories to lists of scores
        """
        category_scores = {}
        for score in self.scores:
            category = MetricCategory.get_category_for_metric(score.metric)
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        return category_scores
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate a summary of evaluation scores.
        
        Returns:
            Dictionary with summary statistics
        """
        # Normalize all scores to percentage for summary
        normalized_scores = [score.normalize(ScoreRange.PERCENTAGE) for score in self.scores]
        
        summary = {
            "overall_score": statistics.mean(normalized_scores) if normalized_scores else 0,
            "num_metrics": len(self.scores),
            "by_category": {}
        }
        
        # Calculate averages by category
        category_scores = self.get_category_scores()
        for category, scores in category_scores.items():
            normalized = [score.normalize(ScoreRange.PERCENTAGE) for score in scores]
            summary["by_category"][category.value] = {
                "average": statistics.mean(normalized) if normalized else 0,
                "count": len(scores)
            }
            
        return summary
        
    def save_to_file(self, file_path: str):
        """Save the evaluation result to a file.
        
        Args:
            file_path: Path to save the result to
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

class MetricDefinition:
    """Definition of how to evaluate a specific metric."""
    
    def __init__(
        self,
        metric: EvaluationMetric,
        description: str,
        score_range: ScoreRange,
        evaluation_function: Optional[Callable] = None,
        required_inputs: Optional[List[str]] = None,
        weight: float = 1.0
    ):
        """Initialize a metric definition.
        
        Args:
            metric: The metric being defined
            description: Description of the metric
            score_range: The range for scores of this metric
            evaluation_function: Optional function to evaluate the metric
            required_inputs: List of required inputs for evaluation
            weight: Weight of this metric in overall scoring
        """
        self.metric = metric
        self.description = description
        self.score_range = score_range
        self.evaluation_function = evaluation_function
        self.required_inputs = required_inputs or []
        self.weight = weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metric definition to a dictionary representation.
        
        Returns:
            Dictionary representation of the metric definition
        """
        return {
            "metric": self.metric.value,
            "description": self.description,
            "score_range": self.score_range.value,
            "required_inputs": self.required_inputs,
            "weight": self.weight,
            "category": MetricCategory.get_category_for_metric(self.metric).value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricDefinition':
        """Create a MetricDefinition from a dictionary representation.
        
        Args:
            data: Dictionary representation of a metric definition
            
        Returns:
            MetricDefinition instance
        """
        return cls(
            metric=EvaluationMetric(data["metric"]),
            description=data["description"],
            score_range=ScoreRange(data["score_range"]),
            required_inputs=data.get("required_inputs", []),
            weight=data.get("weight", 1.0)
        )

# Standard metric definitions
STANDARD_METRICS = [
    MetricDefinition(
        metric=EvaluationMetric.DENIAL_CODE_ACCURACY,
        description="Accuracy of denial code interpretation and explanation",
        score_range=ScoreRange.SCALE_10,
        required_inputs=["agent_response", "expected_codes", "expected_descriptions"],
        weight=1.5
    ),
    MetricDefinition(
        metric=EvaluationMetric.REMEDIATION_RELEVANCE,
        description="Relevance of remediation steps to the specific denial scenario",
        score_range=ScoreRange.SCALE_10,
        required_inputs=["agent_response", "denial_context", "expected_remediation"],
        weight=1.5
    ),
    MetricDefinition(
        metric=EvaluationMetric.PROCEDURAL_ACCURACY,
        description="Accuracy of procedural steps in claim remediation",
        score_range=ScoreRange.SCALE_10,
        required_inputs=["agent_response", "procedural_requirements"],
        weight=1.2
    ),
    MetricDefinition(
        metric=EvaluationMetric.BILLING_RULE_ACCURACY,
        description="Accuracy of billing rule interpretation and application",
        score_range=ScoreRange.SCALE_10,
        required_inputs=["agent_response", "billing_rules"],
        weight=1.2
    ),
    MetricDefinition(
        metric=EvaluationMetric.EXPLANATION_CLARITY,
        description="Clarity and understandability of code explanations",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["agent_response"],
        weight=1.0
    ),
    MetricDefinition(
        metric=EvaluationMetric.INSTRUCTION_CLARITY,
        description="Clarity and specificity of remediation instructions",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["agent_response"],
        weight=1.0
    ),
    MetricDefinition(
        metric=EvaluationMetric.INFORMATION_COMPLETENESS,
        description="Completeness of information provided in responses",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["agent_response", "required_information"],
        weight=1.0
    ),
    MetricDefinition(
        metric=EvaluationMetric.REMEDIATION_COMPLETENESS,
        description="Completeness of remediation guidance for the specific denial",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["agent_response", "required_remediation_steps"],
        weight=1.0
    ),
    MetricDefinition(
        metric=EvaluationMetric.RESPONSE_CONCISENESS,
        description="Conciseness and efficiency of responses without unnecessary detail",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["agent_response"],
        weight=0.8
    ),
    MetricDefinition(
        metric=EvaluationMetric.WORKFLOW_EFFICIENCY,
        description="Efficiency of the conversation flow toward resolution",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["conversation_history"],
        weight=0.8
    ),
    MetricDefinition(
        metric=EvaluationMetric.HELPFULNESS,
        description="Overall helpfulness of the response in resolving the issue",
        score_range=ScoreRange.SCALE_10,
        required_inputs=["agent_response", "user_query"],
        weight=1.3
    ),
    MetricDefinition(
        metric=EvaluationMetric.PROFESSIONALISM,
        description="Professionalism and appropriate tone of the response",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["agent_response"],
        weight=0.8
    ),
    MetricDefinition(
        metric=EvaluationMetric.USABILITY,
        description="Usability and actionability of the provided information",
        score_range=ScoreRange.SCALE_5,
        required_inputs=["agent_response"],
        weight=1.0
    )
]

def get_metric_definition(metric: EvaluationMetric) -> Optional[MetricDefinition]:
    """Get the standard definition for a metric.
    
    Args:
        metric: The metric to get the definition for
        
    Returns:
        MetricDefinition or None if not found
    """
    for definition in STANDARD_METRICS:
        if definition.metric == metric:
            return definition
    return None
