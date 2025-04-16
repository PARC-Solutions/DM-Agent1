"""End-to-end tests for the complete denial resolution workflow."""

import unittest
import sys
import os
import uuid
import time
import json

# Add the root directory to the path so we can import from agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent.core.session_manager import SessionManager
from agent.core.coordinator import CoordinatorAgent
from agent.core.sequential_agent import SequentialAgent
from agent.core.workflow import WorkflowEngine, WorkflowDefinition
from agent.classifiers.denial_classifier import DenialClassifierAgent
from agent.analyzers.claims_analyzer import ClaimsAnalyzerAgent
from agent.advisors.remediation_advisor import RemediationAdvisorAgent
from agent.tools.document_processing.artifact_manager import ArtifactManager
from agent.tools.document_processing.cms1500_parser import CMS1500Parser
from agent.tools.document_processing.eob_parser import EOBParser
from agent.security.phi_detector import PHIDetector

class DenialResolutionE2ETest(unittest.TestCase):
    """End-to-end tests for the complete denial resolution workflow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Initialize common components
        cls.session_manager = SessionManager()
        cls.artifact_manager = ArtifactManager()
        cls.cms1500_parser = CMS1500Parser()
        cls.eob_parser = EOBParser()
        cls.phi_detector = PHIDetector()
        
        # Initialize specialized agents
        cls.denial_classifier = DenialClassifierAgent()
        cls.claims_analyzer = ClaimsAnalyzerAgent()
        cls.remediation_advisor = RemediationAdvisorAgent()
        
        # Initialize coordinator agent
        cls.coordinator = CoordinatorAgent()
        cls.coordinator.register_specialized_agent("denial_classifier", cls.denial_classifier)
        cls.coordinator.register_specialized_agent("claims_analyzer", cls.claims_analyzer)
        cls.coordinator.register_specialized_agent("remediation_advisor", cls.remediation_advisor)
        
        # Initialize and configure sequential agent with workflow
        cls.sequential_agent = SequentialAgent()
        cls.sequential_agent.register_specialized_agent("denial_classifier", cls.denial_classifier)
        cls.sequential_agent.register_specialized_agent("claims_analyzer", cls.claims_analyzer)
        cls.sequential_agent.register_specialized_agent("remediation_advisor", cls.remediation_advisor)
        
        # Path to test documents
        cls.test_doc_cms1500 = os.path.join(
            os.path.dirname(__file__),
            '../../Project Documentation/Denials_Example/CMS-1500/Print-Claim-748155-060420241000.pdf'
        )
        cls.test_doc_eob = os.path.join(
            os.path.dirname(__file__),
            '../../Project Documentation/Denials_Example/ERN.pdf'
        )
        
        # Skip tests if documents don't exist
        if not os.path.exists(cls.test_doc_cms1500) or not os.path.exists(cls.test_doc_eob):
            raise unittest.SkipTest("Test documents not found")
    
    def setUp(self):
        """Set up a new session for each test."""
        self.session_id = self.session_manager.create_session()
        
    def tearDown(self):
        """Clean up after each test."""
        # Clean up artifacts associated with the session
        artifacts = self.artifact_manager.get_artifacts_by_session(self.session_id)
        for artifact_id in artifacts:
            self.artifact_manager.delete_document(artifact_id)
            
    def test_complete_workflow_with_all_documents(self):
        """Test complete workflow with both CMS-1500 and EOB documents."""
        # Step 1: Upload and process CMS-1500 document
        cms1500_artifact_id = self._upload_cms1500_document()
        
        # Step 2: Upload and process EOB document
        eob_artifact_id = self._upload_eob_document()
        
        # Step 3: Process initial query
        initial_query = "I have a denied claim that I need help with. Can you analyze it and provide remediation steps?"
        self._process_query(initial_query)
        
        # Step 4: Request to analyze documents
        analysis_query = "Can you analyze the documents I've uploaded and tell me why the claim was denied?"
        analysis_response = self._process_query(analysis_query)
        
        # Step 5: Request remediation steps
        remediation_query = "What steps should I take to fix this denial and resubmit the claim?"
        remediation_response = self._process_query(remediation_query)
        
        # Verify appropriate responses
        self._verify_workflow_responses(analysis_response, remediation_response)

    def test_workflow_with_session_persistence(self):
        """Test workflow with session persistence across multiple interactions."""
        # Step 1: Initial conversation and document upload
        self._process_query("Hello, I need help with a denied claim.")
        cms1500_artifact_id = self._upload_cms1500_document()
        
        # Step 2: Export session state
        session_state = self.session_manager.export_session(self.session_id)
        self.assertIsNotNone(session_state)
        
        # Step 3: Create new session with imported state
        new_session_id = self.session_manager.create_session()
        self.session_manager.import_session(new_session_id, session_state)
        
        # Step 4: Continue conversation in new session
        old_session_id = self.session_id
        self.session_id = new_session_id
        
        # Step 5: Process query in continued session
        response = self._process_query("Can you analyze the claim I uploaded earlier?")
        
        # Verify session continuity
        self.assertIn("document", response.lower())
        
        # Clean up original session
        artifacts = self.artifact_manager.get_artifacts_by_session(old_session_id)
        for artifact_id in artifacts:
            self.artifact_manager.delete_document(artifact_id)
    
    def test_workflow_with_sequential_agent(self):
        """Test the complete workflow using the sequential agent."""
        # Step 1: Upload documents
        cms1500_artifact_id = self._upload_cms1500_document()
        eob_artifact_id = self._upload_eob_document()
        
        # Step 2: Create context for sequential processing
        context = {
            "query": "I have a denied claim with code CO-16 and N290. How do I fix it?",
            "session_id": self.session_id,
            "document_references": [cms1500_artifact_id, eob_artifact_id]
        }
        
        # Step 3: Process with workflow
        start_time = time.time()
        workflow_result = self.sequential_agent.process_with_workflow(context)
        end_time = time.time()
        
        # Log performance
        print(f"Sequential workflow execution time: {end_time - start_time:.2f} seconds")
        
        # Verify workflow result
        self.assertIsNotNone(workflow_result)
        self.assertIn("remediation", workflow_result.lower())
    
    def test_security_integration_in_workflow(self):
        """Test security component integration in the workflow."""
        # Step 1: Upload documents
        cms1500_artifact_id = self._upload_cms1500_document()
        
        # Step 2: Process query with PHI
        query_with_phi = "Patient John Smith with SSN 123-45-6789 had a denial for service on 4/15/2025"
        response = self._process_query(query_with_phi)
        
        # Verify PHI handling
        self.assertNotIn("123-45-6789", response)  # SSN should be redacted
        
        # Check PHI detection explicitly
        phi_result = self.phi_detector.detect_phi(query_with_phi)
        self.assertTrue(any(category == "SSN" for _, category in phi_result))
    
    def _upload_cms1500_document(self):
        """Helper to upload and process a CMS-1500 document."""
        with open(self.test_doc_cms1500, 'rb') as f:
            document_data = f.read()
            
        # Store document
        artifact_id = self.artifact_manager.store_document(
            session_id=self.session_id,
            document_data=document_data,
            document_type="cms1500",
            filename=os.path.basename(self.test_doc_cms1500)
        )
        
        # Add document reference to session
        self.session_manager.add_document_reference(
            session_id=self.session_id,
            document_reference={
                "id": artifact_id,
                "type": "cms1500",
                "filename": os.path.basename(self.test_doc_cms1500)
            }
        )
        
        # Parse document
        retrieved_document = self.artifact_manager.retrieve_document(artifact_id)
        parsed_data = self.cms1500_parser.parse(document_data=retrieved_document["document_data"])
        
        # Add parsed data to session context
        self.session_manager.update_context(
            session_id=self.session_id,
            context_updates={"cms1500_data": parsed_data}
        )
        
        return artifact_id
    
    def _upload_eob_document(self):
        """Helper to upload and process an EOB document."""
        with open(self.test_doc_eob, 'rb') as f:
            document_data = f.read()
            
        # Store document
        artifact_id = self.artifact_manager.store_document(
            session_id=self.session_id,
            document_data=document_data,
            document_type="eob",
            filename=os.path.basename(self.test_doc_eob)
        )
        
        # Add document reference to session
        self.session_manager.add_document_reference(
            session_id=self.session_id,
            document_reference={
                "id": artifact_id,
                "type": "eob",
                "filename": os.path.basename(self.test_doc_eob)
            }
        )
        
        # Parse document
        retrieved_document = self.artifact_manager.retrieve_document(artifact_id)
        parsed_data = self.eob_parser.parse(document_data=retrieved_document["document_data"])
        
        # Extract denial codes
        denial_codes = self.eob_parser.extract_denial_codes(parsed_data)
        
        # Add parsed data to session context
        self.session_manager.update_context(
            session_id=self.session_id,
            context_updates={
                "eob_data": parsed_data,
                "carc_codes": denial_codes.get("carc_codes", []),
                "rarc_codes": denial_codes.get("rarc_codes", [])
            }
        )
        
        return artifact_id
    
    def _process_query(self, query):
        """Helper to process a query through the coordinator."""
        response = self.coordinator.process_query(query, self.session_id)
        self.assertIsNotNone(response)
        return response
    
    def _verify_workflow_responses(self, analysis_response, remediation_response):
        """Verify that workflow responses contain expected information."""
        # Analysis response should mention denial codes
        self.assertTrue(
            any(code in analysis_response for code in ["CO-16", "CO16", "N290"]),
            "Analysis response should mention denial codes"
        )
        
        # Remediation response should include action steps
        remediation_keywords = ["resubmit", "correct", "update", "documentation", "appeal"]
        self.assertTrue(
            any(keyword in remediation_response.lower() for keyword in remediation_keywords),
            "Remediation response should include action steps"
        )

if __name__ == '__main__':
    unittest.main()
