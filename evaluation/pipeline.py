"""Evaluation pipeline for the Medical Billing Denial Agent."""

import os
import json
import time
import datetime
import uuid
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
import concurrent.futures
from functools import partial

from agent.core.session_manager import SessionManager
from agent.core.coordinator import CoordinatorAgent
from agent.core.sequential_agent import SequentialAgent
from agent.classifiers.denial_classifier import DenialClassifierAgent
from agent.analyzers.claims_analyzer import ClaimsAnalyzerAgent
from agent.advisors.remediation_advisor import RemediationAdvisorAgent
from agent.tools.document_processing.artifact_manager import ArtifactManager

from evaluation.metrics import (
    EvaluationMetric, 
    MetricCategory, 
    ScoreRange, 
    EvaluationScore,
    EvaluationResult,
    MetricDefinition,
    get_metric_definition
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("evaluation_pipeline")

class TestScenario:
    """Representation of a test scenario for evaluation."""
    
    def __init__(
        self,
        scenario_id: str,
        scenario_type: str,
        user_query: str,
        expected_response: Optional[str] = None,
        documents: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        evaluation_criteria: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a test scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
            scenario_type: Type of scenario (e.g., 'denial_classification')
            user_query: User query to process
            expected_response: Expected agent response
            documents: Optional list of document references
            context: Optional session context
            evaluation_criteria: Optional specific evaluation criteria
            metadata: Optional additional metadata
        """
        self.scenario_id = scenario_id
        self.scenario_type = scenario_type
        self.user_query = user_query
        self.expected_response = expected_response
        self.documents = documents or []
        self.context = context or {}
        self.evaluation_criteria = evaluation_criteria or {}
        self.metadata = metadata or {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestScenario':
        """Create a TestScenario from a dictionary.
        
        Args:
            data: Dictionary representation of a test scenario
            
        Returns:
            TestScenario instance
        """
        return cls(
            scenario_id=data["scenario_id"],
            scenario_type=data["scenario_type"],
            user_query=data["user_query"],
            expected_response=data.get("expected_response"),
            documents=data.get("documents", []),
            context=data.get("context", {}),
            evaluation_criteria=data.get("evaluation_criteria", {}),
            metadata=data.get("metadata", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the test scenario to a dictionary.
        
        Returns:
            Dictionary representation of the test scenario
        """
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type,
            "user_query": self.user_query,
            "expected_response": self.expected_response,
            "documents": self.documents,
            "context": self.context,
            "evaluation_criteria": self.evaluation_criteria,
            "metadata": self.metadata
        }

class ScenarioRunner:
    """Runner for test scenarios."""
    
    def __init__(self):
        """Initialize the scenario runner."""
        # Initialize agent components
        self.session_manager = SessionManager()
        self.artifact_manager = ArtifactManager()
        
        # Initialize specialized agents
        self.denial_classifier = DenialClassifierAgent()
        self.claims_analyzer = ClaimsAnalyzerAgent()
        self.remediation_advisor = RemediationAdvisorAgent()
        
        # Initialize coordinator agent
        self.coordinator = CoordinatorAgent()
        self.coordinator.register_specialized_agent("denial_classifier", self.denial_classifier)
        self.coordinator.register_specialized_agent("claims_analyzer", self.claims_analyzer)
        self.coordinator.register_specialized_agent("remediation_advisor", self.remediation_advisor)
        
        # Initialize sequential agent
        self.sequential_agent = SequentialAgent()
        self.sequential_agent.register_specialized_agent("denial_classifier", self.denial_classifier)
        self.sequential_agent.register_specialized_agent("claims_analyzer", self.claims_analyzer)
        self.sequential_agent.register_specialized_agent("remediation_advisor", self.remediation_advisor)
    
    def run_scenario(self, scenario: TestScenario) -> Tuple[str, Dict[str, Any]]:
        """Run a test scenario through the agent.
        
        Args:
            scenario: Test scenario to run
            
        Returns:
            Tuple of (agent_response, run_metadata)
        """
        start_time = time.time()
        
        # Create a new session
        session_id = self.session_manager.create_session()
        
        # Add initial context if provided
        if scenario.context:
            self.session_manager.update_context(session_id, scenario.context)
        
        # Load documents if provided
        document_metadata = []
        for doc in scenario.documents:
            if "file_path" in doc:
                doc_id = self._load_document(session_id, doc)
                document_metadata.append({
                    "id": doc_id,
                    "type": doc.get("type", "unknown"),
                    "filename": os.path.basename(doc["file_path"])
                })
        
        # Process the query
        agent_response = self.coordinator.process_query(scenario.user_query, session_id)
        
        end_time = time.time()
        
        # Collect run metadata
        run_metadata = {
            "session_id": session_id,
            "execution_time": end_time - start_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "documents": document_metadata,
            "final_context": self.session_manager.get_context(session_id)
        }
        
        # Clean up
        self._cleanup_session(session_id)
        
        return agent_response, run_metadata
    
    def _load_document(self, session_id: str, doc_info: Dict[str, Any]) -> str:
        """Load a document into the session.
        
        Args:
            session_id: Session ID
            doc_info: Document information
            
        Returns:
            Document artifact ID
        """
        file_path = doc_info["file_path"]
        doc_type = doc_info.get("type", "unknown")
        
        # Read document data
        with open(file_path, 'rb') as f:
            document_data = f.read()
        
        # Store document
        artifact_id = self.artifact_manager.store_document(
            session_id=session_id,
            document_data=document_data,
            document_type=doc_type,
            filename=os.path.basename(file_path)
        )
        
        # Add document reference to session
        self.session_manager.add_document_reference(
            session_id=session_id,
            document_reference={
                "id": artifact_id,
                "type": doc_type,
                "filename": os.path.basename(file_path)
            }
        )
        
        return artifact_id
    
    def _cleanup_session(self, session_id: str):
        """Clean up a session and its artifacts.
        
        Args:
            session_id: Session ID to clean up
        """
        # Clean up artifacts
        artifacts = self.artifact_manager.get_artifacts_by_session(session_id)
        for artifact_id in artifacts:
            self.artifact_manager.delete_document(artifact_id)

class AutomaticEvaluator:
    """Automatic evaluator for agent responses."""
    
    def __init__(self, metrics_to_evaluate: Optional[List[EvaluationMetric]] = None):
        """Initialize the automatic evaluator.
        
        Args:
            metrics_to_evaluate: List of metrics to evaluate
        """
        self.metrics_to_evaluate = metrics_to_evaluate or [
            EvaluationMetric.DENIAL_CODE_ACCURACY,
            EvaluationMetric.REMEDIATION_RELEVANCE,
            EvaluationMetric.PROCEDURAL_ACCURACY,
            EvaluationMetric.EXPLANATION_CLARITY,
            EvaluationMetric.INSTRUCTION_CLARITY,
            EvaluationMetric.INFORMATION_COMPLETENESS,
            EvaluationMetric.REMEDIATION_COMPLETENESS,
            EvaluationMetric.RESPONSE_CONCISENESS,
            EvaluationMetric.WORKFLOW_EFFICIENCY,
            EvaluationMetric.HELPFULNESS,
            EvaluationMetric.PROFESSIONALISM,
            EvaluationMetric.USABILITY
        ]
    
    def evaluate(
        self, 
        scenario: TestScenario, 
        agent_response: str, 
        run_metadata: Dict[str, Any]
    ) -> EvaluationResult:
        """Evaluate the agent's response.
        
        Args:
            scenario: The test scenario
            agent_response: The agent's response
            run_metadata: Metadata from the scenario run
            
        Returns:
            Evaluation result
        """
        scores = []
        
        # Create evaluation context
        eval_context = {
            "agent_response": agent_response,
            "user_query": scenario.user_query,
            "expected_response": scenario.expected_response,
            "run_metadata": run_metadata,
            "scenario": scenario
        }
        
        # Add scenario-specific evaluation criteria
        for key, value in scenario.evaluation_criteria.items():
            eval_context[key] = value
        
        # Evaluate each metric
        for metric in self.metrics_to_evaluate:
            metric_def = get_metric_definition(metric)
            if not metric_def:
                logger.warning(f"No definition found for metric {metric.value}, skipping")
                continue
                
            # Check if we have all required inputs
            has_all_inputs = True
            for input_name in metric_def.required_inputs:
                if input_name not in eval_context:
                    logger.warning(
                        f"Missing required input '{input_name}' for metric {metric.value}, skipping"
                    )
                    has_all_inputs = False
                    break
            
            if not has_all_inputs:
                continue
                
            # Evaluate the metric
            try:
                score = self._evaluate_metric(metric, metric_def, eval_context)
                scores.append(score)
            except Exception as e:
                logger.error(f"Error evaluating metric {metric.value}: {e}")
        
        # Create evaluation result
        result = EvaluationResult(
            scenario_id=scenario.scenario_id,
            scenario_type=scenario.scenario_type,
            scores=scores,
            agent_response=agent_response,
            expected_response=scenario.expected_response,
            metadata={
                "run_metadata": run_metadata,
                "evaluation_context": {
                    k: v for k, v in eval_context.items() 
                    if k not in ["agent_response", "expected_response", "run_metadata", "scenario"]
                }
            }
        )
        
        return result
    
    def _evaluate_metric(
        self, 
        metric: EvaluationMetric, 
        metric_def: MetricDefinition,
        context: Dict[str, Any]
    ) -> EvaluationScore:
        """Evaluate a specific metric.
        
        Args:
            metric: The metric to evaluate
            metric_def: The metric definition
            context: Evaluation context
            
        Returns:
            Evaluation score
        """
        # Use automated evaluation based on metric type
        score = None
        notes = None
        
        # Extract required inputs
        inputs = {name: context[name] for name in metric_def.required_inputs}
        
        # If the metric has an evaluation function, use it
        if metric_def.evaluation_function:
            score, notes = metric_def.evaluation_function(**inputs)
        else:
            # Use default evaluation methods based on metric
            if metric == EvaluationMetric.DENIAL_CODE_ACCURACY:
                score, notes = self._evaluate_denial_code_accuracy(**inputs)
            elif metric == EvaluationMetric.REMEDIATION_RELEVANCE:
                score, notes = self._evaluate_remediation_relevance(**inputs)
            elif metric == EvaluationMetric.EXPLANATION_CLARITY:
                score, notes = self._evaluate_explanation_clarity(**inputs)
            # Add other metric evaluations here
            else:
                # For metrics without specific evaluation, use a placeholder
                score = 5.0 if metric_def.score_range == ScoreRange.SCALE_10 else 3.0
                notes = "Automated evaluation not implemented for this metric"
        
        # Create and return the score
        return EvaluationScore(
            metric=metric,
            score=score,
            score_range=metric_def.score_range,
            evaluator="automatic",
            notes=notes
        )
    
    def _evaluate_denial_code_accuracy(
        self, 
        agent_response: str, 
        expected_codes: List[str], 
        expected_descriptions: Dict[str, str],
        **kwargs
    ) -> Tuple[float, str]:
        """Evaluate denial code accuracy.
        
        Args:
            agent_response: The agent's response
            expected_codes: Expected denial codes
            expected_descriptions: Expected descriptions for each code
            
        Returns:
            Tuple of (score, notes)
        """
        # Check if all expected codes are mentioned in the response
        code_presence = sum(1 for code in expected_codes if code in agent_response)
        code_accuracy = code_presence / len(expected_codes) if expected_codes else 0
        
        # Check if descriptions match expectations
        description_matches = 0
        for code, description in expected_descriptions.items():
            # Look for description near the code
            code_index = agent_response.find(code)
            if code_index >= 0:
                # Check surrounding text for description elements
                context = agent_response[max(0, code_index - 100):code_index + 400]
                description_matches += sum(1 for key_phrase in description.split(".")[0].split() if key_phrase.lower() in context.lower()) / len(description.split(".")[0].split())
        
        description_accuracy = description_matches / len(expected_descriptions) if expected_descriptions else 0
        
        # Combine code presence and description accuracy
        score = (code_accuracy * 0.4 + description_accuracy * 0.6) * 10
        score = min(10.0, max(0.0, score))  # Ensure within range
        
        notes = (
            f"Code presence: {code_presence}/{len(expected_codes) if expected_codes else 0}. "
            f"Description accuracy: {description_accuracy:.2f}"
        )
        
        return score, notes
    
    def _evaluate_remediation_relevance(
        self,
        agent_response: str,
        denial_context: Dict[str, Any],
        expected_remediation: str,
        **kwargs
    ) -> Tuple[float, str]:
        """Evaluate remediation relevance.
        
        Args:
            agent_response: The agent's response
            denial_context: Context about the denial
            expected_remediation: Expected remediation steps
            
        Returns:
            Tuple of (score, notes)
        """
        # Extract key phrases from expected remediation
        key_phrases = [phrase.strip().lower() for phrase in expected_remediation.split(".") if phrase.strip()]
        
        # Count how many key phrases are present in the response
        response_lower = agent_response.lower()
        matches = sum(1 for phrase in key_phrases if phrase in response_lower)
        
        # Calculate relevance score
        relevance = matches / len(key_phrases) if key_phrases else 0
        score = relevance * 10
        score = min(10.0, max(0.0, score))
        
        notes = f"Found {matches}/{len(key_phrases) if key_phrases else 0} key remediation elements"
        
        return score, notes
    
    def _evaluate_explanation_clarity(self, agent_response: str, **kwargs) -> Tuple[float, str]:
        """Evaluate explanation clarity.
        
        Args:
            agent_response: The agent's response
            
        Returns:
            Tuple of (score, notes)
        """
        # Simple heuristics for clarity evaluation
        
        # Check for short paragraphs (more readable)
        paragraphs = [p for p in agent_response.split("\n\n") if p.strip()]
        avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        para_score = 5.0 if avg_para_length < 100 else (3.0 if avg_para_length < 150 else 1.0)
        
        # Check for structured content (bullets, numbering)
        has_bullets = any(line.strip().startswith(("-", "*", "•")) for line in agent_response.split("\n"))
        has_numbering = any(line.strip().startswith((f"{i}." for i in range(1, 10))) for line in agent_response.split("\n"))
        structure_score = 5.0 if (has_bullets or has_numbering) else 3.0
        
        # Check for technical jargon without explanation
        jargon_terms = ["adjudication", "capitation", "HIPAA", "Medicare", "Medicaid", "remittance"]
        unexplained_jargon = sum(1 for term in jargon_terms if term.lower() in agent_response.lower() and f"{term} is" not in agent_response and f"{term} refers" not in agent_response)
        jargon_score = 5.0 if unexplained_jargon == 0 else (3.0 if unexplained_jargon <= 2 else 1.0)
        
        # Combine scores
        combined_score = (para_score + structure_score + jargon_score) / 3
        
        notes = (
            f"Paragraph length: {avg_para_length:.1f} words (score: {para_score}). "
            f"Structure: {'good' if has_bullets or has_numbering else 'could improve'} (score: {structure_score}). "
            f"Jargon explanation: {unexplained_jargon} unexplained terms (score: {jargon_score})."
        )
        
        return combined_score, notes

class EvaluationPipeline:
    """Pipeline for evaluating the Medical Billing Denial Agent."""
    
    def __init__(
        self,
        scenarios_dir: str = "evaluation/benchmark_data",
        results_dir: str = "evaluation/results",
        metrics_to_evaluate: Optional[List[EvaluationMetric]] = None,
        parallel_execution: bool = True
    ):
        """Initialize the evaluation pipeline.
        
        Args:
            scenarios_dir: Directory containing test scenarios
            results_dir: Directory to save evaluation results
            metrics_to_evaluate: List of metrics to evaluate
            parallel_execution: Whether to run scenarios in parallel
        """
        self.scenarios_dir = scenarios_dir
        self.results_dir = results_dir
        self.parallel_execution = parallel_execution
        
        # Create directories if they don't exist
        os.makedirs(scenarios_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        # Initialize components
        self.scenario_runner = ScenarioRunner()
        self.evaluator = AutomaticEvaluator(metrics_to_evaluate)
        
        # Load scenarios
        self.scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> Dict[str, TestScenario]:
        """Load test scenarios from files.
        
        Returns:
            Dictionary mapping scenario IDs to TestScenario objects
        """
        scenarios = {}
        
        # Find scenario files
        scenario_files = []
        for root, _, files in os.walk(self.scenarios_dir):
            for file in files:
                if file.endswith(".json"):
                    scenario_files.append(os.path.join(root, file))
        
        # Load scenarios from files
        for file_path in scenario_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Handle single scenario or list of scenarios
                if isinstance(data, list):
                    for scenario_data in data:
                        scenario = TestScenario.from_dict(scenario_data)
                        scenarios[scenario.scenario_id] = scenario
                else:
                    scenario = TestScenario.from_dict(data)
                    scenarios[scenario.scenario_id] = scenario
                    
            except Exception as e:
                logger.error(f"Error loading scenario from {file_path}: {e}")
        
        logger.info(f"Loaded {len(scenarios)} test scenarios")
        return scenarios
    
    def evaluate_scenario(self, scenario: TestScenario) -> EvaluationResult:
        """Evaluate a single test scenario.
        
        Args:
            scenario: Test scenario to evaluate
            
        Returns:
            Evaluation result
        """
        logger.info(f"Evaluating scenario {scenario.scenario_id}")
        
        try:
            # Run the scenario
            agent_response, run_metadata = self.scenario_runner.run_scenario(scenario)
            
            # Evaluate the response
            result = self.evaluator.evaluate(scenario, agent_response, run_metadata)
            
            # Save the result
            self._save_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating scenario {scenario.scenario_id}: {e}")
            raise
    
    def evaluate_all(self) -> Dict[str, EvaluationResult]:
        """Evaluate all loaded test scenarios.
        
        Returns:
            Dictionary mapping scenario IDs to evaluation results
        """
        results = {}
        
        if self.parallel_execution:
            # Run scenarios in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_scenario = {
                    executor.submit(self.evaluate_scenario, scenario): scenario_id
                    for scenario_id, scenario in self.scenarios.items()
                }
                
                for future in concurrent.futures.as_completed(future_to_scenario):
                    scenario_id = future_to_scenario[future]
                    try:
                        result = future.result()
                        results[scenario_id] = result
                    except Exception as e:
                        logger.error(f"Error in scenario {scenario_id}: {e}")
        else:
            # Run scenarios sequentially
            for scenario_id, scenario in self.scenarios.items():
                try:
                    result = self.evaluate_scenario(scenario)
                    results[scenario_id] = result
                except Exception as e:
                    logger.error(f"Error in scenario {scenario_id}: {e}")
        
        # Generate summary report
        self._generate_summary_report(results)
        
        return results
    
    def _save_result(self, result: EvaluationResult):
        """Save an evaluation result to a file.
        
        Args:
            result: Evaluation result to save
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(
            self.results_dir,
            f"{result.scenario_id}_{timestamp}.json"
        )
        
        result.save_to_file(file_path)
        logger.info(f"Saved evaluation result to {file_path}")
    
    def _generate_summary_report(self, results: Dict[str, EvaluationResult]):
        """Generate a summary report of evaluation results.
        
        Args:
            results: Dictionary mapping scenario IDs to evaluation results
        """
        if not results:
            logger.warning("No results to generate summary report")
            return
            
        # Calculate overall statistics
        overall_scores = []
        category_scores = {}
        metric_scores = {}
        
        for result in results.values():
            # Get overall score
            summary = result.get_summary()
            overall_scores.append(summary["overall_score"])
            
            # Get category scores
            for category, data in summary["by_category"].items():
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(data["average"])
            
            # Get metric scores
            for score in result.scores:
                metric = score.metric.value
                if metric not in metric_scores:
                    metric_scores[metric] = []
                metric_scores[metric].append(score.normalize(ScoreRange.PERCENTAGE))
        
        # Create summary report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "num_scenarios": len(results),
            "overall_score": {
                "mean": statistics.mean(overall_scores),
                "min": min(overall_scores),
                "max": max(overall_scores)
            },
            "by_category": {
                category: {
                    "mean": statistics.mean(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
                for category, scores in category_scores.items()
            },
            "by_metric": {
                metric: {
                    "mean": statistics.mean(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
                for metric, scores in metric_scores.items()
            },
            "scenario_summaries": {
                scenario_id: {
                    "type": result.scenario_type,
                    "overall_score": result.get_summary()["overall_score"]
                }
                for scenario_id, result in results.items()
            }
        }
        
        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.results_dir, f"summary_report_{timestamp}.json")
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Generated summary report at {report_path}")
        
        # Print summary to console
        print("\n===== EVALUATION SUMMARY =====")
        print(f"Scenarios evaluated: {len(results)}")
        print(f"Overall score: {report['overall_score']['mean']:.2f} (min: {report['overall_score']['min']:.2f}, max: {report['overall_score']['max']:.2f})")
        print("\nScores by category:")
        for category, stats in report["by_category"].items():
            print(f"  {category}: {stats['mean']:.2f} (min: {stats['min']:.2f}, max: {stats['max']:.2f})")
        print("\nScores by metric:")
        for metric, stats in report["by_metric"].items():
            print(f"  {metric}: {stats['mean']:.2f} (min: {stats['min']:.2f}, max: {stats['max']:.2f})")
        print("==============================\n")
        
        return report

def run_evaluation(
    scenarios_dir: str = "evaluation/benchmark_data",
    results_dir: str = "evaluation/results",
    parallel: bool = True
):
    """Run the evaluation pipeline.
    
    Args:
        scenarios_dir: Directory containing test scenarios
        results_dir: Directory to save evaluation results
        parallel: Whether to run scenarios in parallel
    """
    pipeline = EvaluationPipeline(
        scenarios_dir=scenarios_dir,
        results_dir=results_dir,
        parallel_execution=parallel
    )
    
    results = pipeline.evaluate_all()
    
    return results

if __name__ == "__main__":
    run_evaluation()
