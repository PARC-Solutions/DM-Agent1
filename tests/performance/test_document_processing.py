"""Performance tests for document processing functionality."""

import time
import unittest
import sys
import os
import glob
from typing import List, Dict, Any

# Add the root directory to the path so we can import from agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.performance.test_performance_base import PerformanceTestBase, performance_test
from agent.tools.document_processing.cms1500_parser import CMS1500Parser
from agent.tools.document_processing.eob_parser import EOBParser
from agent.tools.document_processing.artifact_manager import ArtifactManager

class DocumentProcessingPerformanceTest(PerformanceTestBase):
    """Test the performance of document processing tools."""
    
    def setUp(self):
        """Set up test environment with document parsers."""
        super().setUp()
        
        # Initialize parsers
        self.cms1500_parser = CMS1500Parser()
        self.eob_parser = EOBParser()
        self.artifact_manager = ArtifactManager()
        
        # Paths to test documents
        self.cms1500_docs_path = os.path.join(
            os.path.dirname(__file__), 
            '../../Project Documentation/Denials_Example/CMS-1500/'
        )
        self.eob_docs_path = os.path.join(
            os.path.dirname(__file__), 
            '../../Project Documentation/Denials_Example/'
        )
        
        # Get test document paths
        self.cms1500_docs = self._get_test_documents(self.cms1500_docs_path, '*.pdf')
        self.eob_docs = self._get_test_documents(self.eob_docs_path, 'ERN.pdf')
        
    def _get_test_documents(self, path: str, pattern: str) -> List[str]:
        """Get list of test document paths matching the pattern.
        
        Args:
            path: Directory path to search
            pattern: File pattern to match
            
        Returns:
            List of document paths
        """
        if not os.path.exists(path):
            print(f"Warning: Test document path does not exist: {path}")
            return []
            
        documents = glob.glob(os.path.join(path, pattern))
        
        if not documents:
            print(f"Warning: No test documents found at {path} with pattern {pattern}")
            
        return documents
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_DOCUMENT_PROCESSING,
        test_case="cms1500_parse_single"
    )
    def test_cms1500_parse_performance(self):
        """Test performance of parsing a single CMS-1500 form."""
        if not self.cms1500_docs:
            self.skipTest("No CMS-1500 test documents available")
            
        document_path = self.cms1500_docs[0]
        
        # Parse the document
        result = self.cms1500_parser.parse(document_path)
        
        # Verify successful parsing
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        
        return result
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_DOCUMENT_PROCESSING,
        test_case="eob_parse_single"
    )
    def test_eob_parse_performance(self):
        """Test performance of parsing a single EOB document."""
        if not self.eob_docs:
            self.skipTest("No EOB test documents available")
            
        document_path = self.eob_docs[0]
        
        # Parse the document
        result = self.eob_parser.parse(document_path)
        
        # Verify successful parsing
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        
        return result
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_DOCUMENT_PROCESSING,
        test_case="cms1500_batch_parse",
        threshold=30.0  # Higher threshold for batch processing
    )
    def test_cms1500_batch_parse_performance(self):
        """Test performance of parsing multiple CMS-1500 forms."""
        if not self.cms1500_docs:
            self.skipTest("No CMS-1500 test documents available")
            
        batch_size = min(5, len(self.cms1500_docs))
        batch_docs = self.cms1500_docs[:batch_size]
        
        results = []
        for doc_path in batch_docs:
            result = self.cms1500_parser.parse(doc_path)
            results.append(result)
            
        # Record the batch size used
        self.record_metric(
            metric="batch_size",
            value=batch_size,
            category=self.CATEGORY_DOCUMENT_PROCESSING,
            test_case="cms1500_batch_parse"
        )
        
        # Verify all documents were processed
        self.assertEqual(len(results), batch_size)
        for result in results:
            self.assertIsNotNone(result)
            self.assertTrue(len(result) > 0)
            
        return results
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_DOCUMENT_PROCESSING,
        test_case="detect_carc_rarc_codes"
    )
    def test_detect_carc_rarc_codes_performance(self):
        """Test performance of detecting CARC/RARC codes in EOB documents."""
        if not self.eob_docs:
            self.skipTest("No EOB test documents available")
            
        document_path = self.eob_docs[0]
        
        # Parse the document
        parsed_data = self.eob_parser.parse(document_path)
        
        # Extract CARC/RARC codes
        codes = self.eob_parser.extract_denial_codes(parsed_data)
        
        # Verify code extraction
        self.assertIsNotNone(codes)
        self.assertIn("carc_codes", codes)
        self.assertIn("rarc_codes", codes)
        
        return codes
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_DOCUMENT_PROCESSING,
        test_case="artifact_store_retrieve"
    )
    def test_artifact_management_performance(self):
        """Test performance of artifact storage and retrieval."""
        if not self.cms1500_docs:
            self.skipTest("No CMS-1500 test documents available")
            
        document_path = self.cms1500_docs[0]
        session_id = "test_session_123"
        
        # Read document content
        with open(document_path, 'rb') as f:
            document_data = f.read()
            
        # Store document
        artifact_id = self.artifact_manager.store_document(
            session_id=session_id,
            document_data=document_data,
            document_type="cms1500",
            filename=os.path.basename(document_path)
        )
        
        # Retrieve document
        retrieved_document = self.artifact_manager.retrieve_document(artifact_id)
        
        # Verify retrieval
        self.assertIsNotNone(retrieved_document)
        self.assertEqual(retrieved_document["session_id"], session_id)
        self.assertEqual(retrieved_document["document_type"], "cms1500")
        
        # Clean up
        self.artifact_manager.delete_document(artifact_id)
        
        return retrieved_document
    
    def test_document_processing_throughput(self):
        """Test document processing throughput for multiple documents."""
        if not self.cms1500_docs or len(self.cms1500_docs) < 2:
            self.skipTest("Not enough CMS-1500 test documents available")
            
        # Number of documents to process
        num_docs = min(10, len(self.cms1500_docs))
        docs_to_process = self.cms1500_docs[:num_docs]
        
        # Process documents and measure time
        start_time = time.time()
        
        results = []
        for doc_path in docs_to_process:
            result = self.cms1500_parser.parse(doc_path)
            results.append(result)
            
        end_time = time.time()
        
        # Calculate throughput (documents per minute)
        elapsed_time = end_time - start_time
        throughput = (num_docs / elapsed_time) * 60
        
        # Record and assert throughput
        result = self.record_metric(
            metric="throughput",
            value=throughput,
            category=self.CATEGORY_DOCUMENT_PROCESSING,
            test_case="document_batch_processing",
            threshold=self.DEFAULT_THROUGHPUT_THRESHOLD
        )
        
        self.assert_performance_metric(result)
        
        # Verify all documents were processed
        self.assertEqual(len(results), num_docs)
        
        return throughput
    
    @performance_test(
        category=PerformanceTestBase.CATEGORY_DOCUMENT_PROCESSING,
        test_case="document_ocr",
        threshold=10.0  # Higher threshold for OCR operations
    )
    def test_document_ocr_performance(self):
        """Test performance of OCR operations in document processing."""
        if not self.cms1500_docs:
            self.skipTest("No CMS-1500 test documents available")
            
        document_path = self.cms1500_docs[0]
        
        # Parse with explicit OCR
        result = self.cms1500_parser.parse(document_path, force_ocr=True)
        
        # Verify successful parsing
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        
        return result

if __name__ == '__main__':
    unittest.main()
