"""Performance tests for agent response time and throughput."""

import time
import unittest
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Add the root directory to the path so we can import from agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.performance.test_performance_base import PerformanceTestBase, performance_test
from agent.core.session_manager import SessionManager
from agent.core.coordinator import CoordinatorAgent
from agent.classifiers.denial_classifier import DenialClassifierAgent
from agent.analyzers.claims_analyzer import ClaimsAnalyzerAgent
from agent.advisors.remediation_advisor import RemediationAdvisorAgent
from agent.core.sequential_agent import SequentialAgent

class AgentResponsePerformanceTest(PerformanceTestBase):
    """Test the performance of agent responses for different query types."""
    
    def setUp(self):
        """Set up test environment with agent instances."""
        super().setUp()
        
        # Initialize session manager
        self.session_manager = SessionManager()
        
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
        
        # Sample queries
        self.sample_queries = {
            "greeting": "Hello, I need help with a claim denial.",
            "claim_info": "I have a denial with code CO-16 for service date 4/10/2025.",
            "explanation": "Can you explain what CARC code 16 means?",
            "remediation": "How do I fix a claim denied with CO-16 and N290?",
            "complex": "I have a CMS-1500 claim with CPT 99213 that was denied with CO-16 and N290. The patient has Medicare and secondary coverage with BC/BS. The date of service was 4/10/2025 and the provider is Dr. Smith at Internal Medicine Associates. How do I fix this?"
        }
        
    @performance_test(
        category=PerformanceTestBase.CATEGORY_AGENT_RESPONSE,
        test_case="coordinator_greeting", 
        threshold=3.0  # Faster threshold for simple greeting
    )
    def test_coordinator_greeting_response(self):
        """Test response time for a simple greeting query."""
        query = self.sample_queries["greeting"]
        session_id = self.session_manager.create_session()
        
        response = self.coordinator.process_query(query, session_id)
        
        self.assertIsNotNone(response)
        return response
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_AGENT_RESPONSE,
        test_case="coordinator_claim_info"
    )
    def test_coordinator_claim_info_response(self):
        """Test response time for a claim information query."""
        query = self.sample_queries["claim_info"]
        session_id = self.session_manager.create_session()
        
        response = self.coordinator.process_query(query, session_id)
        
        self.assertIsNotNone(response)
        return response
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_AGENT_RESPONSE,
        test_case="denial_classifier"
    )
    def test_denial_classifier_response(self):
        """Test response time for the denial classifier agent."""
        query = self.sample_queries["explanation"]
        
        # Create context with CARC/RARC codes
        context = {
            "carc_codes": ["CO-16"],
            "rarc_codes": ["N290"]
        }
        
        response = self.denial_classifier.classify_denial(
            carc_codes=context["carc_codes"],
            rarc_codes=context["rarc_codes"]
        )
        
        self.assertIsNotNone(response)
        return response
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_AGENT_RESPONSE,
        test_case="remediation_advisor"
    )
    def test_remediation_advisor_response(self):
        """Test response time for the remediation advisor agent."""
        # Create context with denial classification
        context = {
            "denial_type": "medical_necessity",
            "carc_codes": ["CO-16"],
            "rarc_codes": ["N290"],
            "service_code": "99213"
        }
        
        response = self.remediation_advisor.get_remediation_steps(
            denial_type=context["denial_type"],
            carc_codes=context["carc_codes"],
            rarc_codes=context["rarc_codes"],
            service_code=context["service_code"]
        )
        
        self.assertIsNotNone(response)
        return response
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_AGENT_RESPONSE,
        test_case="sequential_workflow",
        threshold=15.0  # Higher threshold for workflow execution
    )
    def test_sequential_workflow_response(self):
        """Test response time for a complete sequential workflow."""
        query = self.sample_queries["complex"]
        session_id = self.session_manager.create_session()
        
        # Process with workflow
        context = {
            "query": query,
            "session_id": session_id,
            "document_references": []
        }
        
        response = self.sequential_agent.process_with_workflow(context)
        
        self.assertIsNotNone(response)
        return response
    
    def test_agent_throughput(self):
        """Test agent throughput for processing multiple queries concurrently."""
        # Number of concurrent requests to simulate
        num_requests = 10
        
        # Create multiple session IDs
        session_ids = [self.session_manager.create_session() for _ in range(num_requests)]
        
        # Create list of queries (using different query types)
        query_types = list(self.sample_queries.keys())
        queries = [self.sample_queries[query_types[i % len(query_types)]] 
                  for i in range(num_requests)]
        
        # Function to process a single query
        def process_query(i):
            return self.coordinator.process_query(queries[i], session_ids[i])
        
        # Process queries concurrently
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_query, range(num_requests)))
        
        end_time = time.time()
        
        # Calculate throughput (requests per minute)
        elapsed_time = end_time - start_time
        throughput = (num_requests / elapsed_time) * 60
        
        # Record and assert throughput
        result = self.record_metric(
            metric="throughput",
            value=throughput,
            category=self.CATEGORY_AGENT_RESPONSE,
            test_case="concurrent_requests",
            threshold=self.DEFAULT_THROUGHPUT_THRESHOLD
        )
        
        self.assert_performance_metric(result)
        
        # Verify all requests were processed
        self.assertEqual(len(results), num_requests)
        for response in results:
            self.assertIsNotNone(response)
            
        return throughput

if __name__ == '__main__':
    unittest.main()
