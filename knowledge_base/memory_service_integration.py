"""
Memory Service Integration

This module integrates the various knowledge bases with the VertexAIRagMemoryService
and provides a unified interface for the agent to access the knowledge.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from google.adk.memory import VertexAIRagMemoryService

class DenialManagementMemoryService:
    """
    A service that integrates all knowledge bases through VertexAIRagMemoryService
    and provides methods for efficient knowledge retrieval.
    """
    
    def __init__(self, project_id: str, location: str):
        """
        Initialize the memory service with Google Cloud project settings.
        
        Args:
            project_id: The Google Cloud project ID
            location: The Google Cloud region (e.g., us-central1)
        """
        self.project_id = project_id
        self.location = location
        
        # Initialize paths to knowledge base files
        self.carc_rarc_path = os.path.join("knowledge_base", "carc_rarc", "carc_rarc_knowledge.json")
        self.dont_bill_together_path = os.path.join("knowledge_base", "dont_bill_together", "dont_bill_together_knowledge.json")
        self.resolution_path = os.path.join("knowledge_base", "resolution", "resolution_knowledge.json")
        
        # Load knowledge bases
        self.carc_rarc_kb = self._load_json(self.carc_rarc_path)
        self.dont_bill_together_kb = self._load_json(self.dont_bill_together_path)
        self.resolution_kb = self._load_json(self.resolution_path)
        
        # Initialize memory services
        self.carc_rarc_memory = self._initialize_memory_service("carc-rarc-knowledge")
        self.dont_bill_together_memory = self._initialize_memory_service("dont-bill-together-knowledge")
        self.resolution_memory = self._initialize_memory_service("resolution-knowledge")
        
        # Session context storage
        self.session_memory = {}
        
        # Performance metrics
        self.metrics = {
            "query_count": 0,
            "total_query_time": 0,
            "average_query_time": 0,
            "successful_queries": 0,
            "failed_queries": 0
        }
    
    def _load_json(self, file_path: str) -> Dict[str, Any]:
        """
        Load JSON data from a file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing the JSON data
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                print(f"Warning: {file_path} does not exist. Returning empty dictionary.")
                return {}
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}
    
    def _initialize_memory_service(self, index_id: str) -> VertexAIRagMemoryService:
        """
        Initialize a VertexAIRagMemoryService for a specific knowledge base.
        
        Args:
            index_id: The ID of the vector index to use
            
        Returns:
            Configured VertexAIRagMemoryService
        """
        # Note: In a real implementation, this would connect to an actual Vertex AI vector index
        # For this project implementation, we'll simulate this functionality
        return VertexAIRagMemoryService(
            project=self.project_id,
            location=self.location,
            index_id=index_id
        )
    
    def _measure_query_performance(self, fn):
        """
        Decorator to measure query performance.
        
        Args:
            fn: Function to measure
            
        Returns:
            Wrapped function with performance measurement
        """
        def wrapper(*args, **kwargs):
            start_time = time.time()
            self.metrics["query_count"] += 1
            
            try:
                result = fn(*args, **kwargs)
                self.metrics["successful_queries"] += 1
                return result
            except Exception as e:
                self.metrics["failed_queries"] += 1
                raise e
            finally:
                query_time = time.time() - start_time
                self.metrics["total_query_time"] += query_time
                self.metrics["average_query_time"] = (
                    self.metrics["total_query_time"] / self.metrics["query_count"]
                )
        
        return wrapper
    
    def initialize_session(self, session_id: str) -> None:
        """
        Initialize a session context for storing conversation history and context.
        
        Args:
            session_id: Unique identifier for the session
        """
        self.session_memory[session_id] = {
            "conversation_history": [],
            "context": {},
            "documents": {},
            "created_at": time.time()
        }
        print(f"Session {session_id} initialized.")
    
    def add_to_session_context(self, session_id: str, key: str, value: Any) -> None:
        """
        Add information to the session context.
        
        Args:
            session_id: Unique identifier for the session
            key: Context key
            value: Context value
        """
        if session_id not in self.session_memory:
            self.initialize_session(session_id)
        
        self.session_memory[session_id]["context"][key] = value
    
    def add_conversation_turn(self, session_id: str, user_message: str, agent_response: str) -> None:
        """
        Add a conversation turn to the session history.
        
        Args:
            session_id: Unique identifier for the session
            user_message: Message from the user
            agent_response: Response from the agent
        """
        if session_id not in self.session_memory:
            self.initialize_session(session_id)
        
        self.session_memory[session_id]["conversation_history"].append({
            "user": user_message,
            "agent": agent_response,
            "timestamp": time.time()
        })
    
    def get_session_context(self, session_id: str, key: Optional[str] = None) -> Any:
        """
        Get information from the session context.
        
        Args:
            session_id: Unique identifier for the session
            key: Optional specific context key to retrieve
            
        Returns:
            The context value for the key, or the entire context if key is None
        """
        if session_id not in self.session_memory:
            return None
        
        if key is None:
            return self.session_memory[session_id]["context"]
        
        return self.session_memory[session_id]["context"].get(key)
    
    def get_conversation_history(self, session_id: str, max_turns: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Unique identifier for the session
            max_turns: Maximum number of turns to retrieve (most recent)
            
        Returns:
            List of conversation turns
        """
        if session_id not in self.session_memory:
            return []
        
        history = self.session_memory[session_id]["conversation_history"]
        
        if max_turns is not None:
            return history[-max_turns:]
        
        return history
    
    @_measure_query_performance
    def query_carc_information(self, carc_code: str) -> Dict[str, Any]:
        """
        Query information about a specific CARC code.
        
        Args:
            carc_code: The CARC code to look up
            
        Returns:
            Dictionary containing CARC information
        """
        # In a real implementation, this would query the vector index
        # For this implementation, we'll look it up directly from the loaded knowledge base
        carc_codes = self.carc_rarc_kb.get("carc_codes", [])
        for code in carc_codes:
            if code.get("code") == carc_code:
                return code
        
        return {"error": f"CARC code {carc_code} not found"}
    
    @_measure_query_performance
    def query_rarc_information(self, rarc_code: str) -> Dict[str, Any]:
        """
        Query information about a specific RARC code.
        
        Args:
            rarc_code: The RARC code to look up
            
        Returns:
            Dictionary containing RARC information
        """
        rarc_codes = self.carc_rarc_kb.get("rarc_codes", [])
        for code in rarc_codes:
            if code.get("code") == rarc_code:
                return code
        
        return {"error": f"RARC code {rarc_code} not found"}
    
    @_measure_query_performance
    def check_code_compatibility(self, code1: str, code2: str) -> Dict[str, Any]:
        """
        Check if two procedure codes can be billed together.
        
        Args:
            code1: First procedure code
            code2: Second procedure code
            
        Returns:
            Dictionary with compatibility information
        """
        code_pairs = self.dont_bill_together_kb.get("code_pairs", {})
        
        # Check in modifier not allowed pairs
        for pair in code_pairs.get("modifier_not_allowed", []):
            if (pair.get("column1_code") == code1 and pair.get("column2_code") == code2) or \
               (pair.get("column1_code") == code2 and pair.get("column2_code") == code1):
                return {
                    "compatible": False,
                    "modifier_allowed": False,
                    "reason": "These codes cannot be billed together (NCCI edit with modifier indicator 0)",
                    "guidance": pair.get("resolution_guidance", []),
                    "documentation": pair.get("documentation_requirements", [])
                }
        
        # Check in modifier allowed pairs
        for pair in code_pairs.get("modifier_allowed", []):
            if (pair.get("column1_code") == code1 and pair.get("column2_code") == code2) or \
               (pair.get("column1_code") == code2 and pair.get("column2_code") == code1):
                return {
                    "compatible": True,
                    "modifier_allowed": True,
                    "reason": "These codes may be billed together with an appropriate modifier (NCCI edit with modifier indicator 1)",
                    "guidance": pair.get("resolution_guidance", []),
                    "documentation": pair.get("documentation_requirements", [])
                }
        
        # If not found in either list, they are compatible by default
        return {
            "compatible": True,
            "modifier_allowed": False,
            "reason": "No NCCI edits found for these codes - they can be billed together"
        }
    
    @_measure_query_performance
    def get_denial_resolution_strategy(self, 
                                      carc_code: Optional[str] = None, 
                                      denial_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get resolution strategy for a denial based on CARC code or denial type.
        
        Args:
            carc_code: Optional CARC code to look up
            denial_type: Optional denial type to look up
            
        Returns:
            Dictionary containing resolution strategy
        """
        if carc_code is not None:
            # First get CARC information to identify denial type
            carc_info = self.query_carc_information(carc_code)
            denial_type = carc_info.get("denial_type", "other")
        
        if denial_type is not None:
            strategies = self.resolution_kb.get("resolution_strategies", {})
            strategy = strategies.get(denial_type)
            
            if strategy:
                return {
                    "denial_type": denial_type,
                    "strategy": strategy
                }
        
        return {"error": "No resolution strategy found for the specified criteria"}
    
    @_measure_query_performance
    def semantic_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform semantic search across all knowledge bases.
        
        Args:
            query: Natural language query
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing search results
        """
        # In a real implementation, this would be a semantic search using vector embeddings
        # For this implementation, we'll simulate by matching keywords in descriptions
        
        results = []
        
        # Search in CARC codes
        for carc in self.carc_rarc_kb.get("carc_codes", []):
            score = self._calculate_relevance_score(query, carc.get("description", ""))
            if score > 0.5:  # Arbitrary threshold for this simulation
                results.append({
                    "type": "CARC",
                    "data": carc,
                    "score": score
                })
        
        # Search in RARC codes
        for rarc in self.carc_rarc_kb.get("rarc_codes", []):
            score = self._calculate_relevance_score(query, rarc.get("description", ""))
            if score > 0.5:
                results.append({
                    "type": "RARC",
                    "data": rarc,
                    "score": score
                })
        
        # Search in resolution strategies
        for denial_type, strategy in self.resolution_kb.get("resolution_strategies", {}).items():
            score = self._calculate_relevance_score(query, strategy.get("description", ""))
            if score > 0.5:
                results.append({
                    "type": "Resolution",
                    "denial_type": denial_type,
                    "data": strategy,
                    "score": score
                })
        
        # Sort by score and return top k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _calculate_relevance_score(self, query: str, text: str) -> float:
        """
        Calculate relevance score between query and text.
        This is a simple keyword matching simulation.
        
        Args:
            query: The search query
            text: The text to match against
            
        Returns:
            Float between 0 and 1 representing relevance
        """
        query_words = query.lower().split()
        text_lower = text.lower()
        
        # Count how many query words appear in the text
        matches = sum(1 for word in query_words if word in text_lower)
        
        # Calculate score based on proportion of matching words
        if not query_words:
            return 0
        
        return matches / len(query_words)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get the current performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        return self.metrics
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear a session from memory.
        
        Args:
            session_id: Unique identifier for the session
        """
        if session_id in self.session_memory:
            del self.session_memory[session_id]
            print(f"Session {session_id} cleared from memory.")


def run_memory_service_integration_example():
    """
    Example usage of the DenialManagementMemoryService.
    """
    # Initialize the memory service
    memory_service = DenialManagementMemoryService(
        project_id="medical-billing-agent",
        location="us-central1"
    )
    
    # Initialize a session
    session_id = "sample-session-1"
    memory_service.initialize_session(session_id)
    
    # Example: Query CARC information
    carc_info = memory_service.query_carc_information("16")
    print("\nCARC Information Example:")
    print(json.dumps(carc_info, indent=2))
    
    # Example: Check code compatibility
    compatibility = memory_service.check_code_compatibility("80061", "82465")
    print("\nCode Compatibility Example:")
    print(json.dumps(compatibility, indent=2))
    
    # Example: Get denial resolution strategy
    resolution = memory_service.get_denial_resolution_strategy(carc_code="16")
    print("\nDenial Resolution Strategy Example:")
    print(json.dumps(resolution, indent=2))
    
    # Example: Semantic search
    search_results = memory_service.semantic_search("missing information claim")
    print("\nSemantic Search Example:")
    print(json.dumps(search_results, indent=2))
    
    # Example: Add conversation turn
    memory_service.add_conversation_turn(
        session_id=session_id,
        user_message="Why was my claim denied with code 16?",
        agent_response="Your claim was denied due to missing information. The specific CARC code 16 indicates that your claim lacks required information or has a submission error."
    )
    
    # Example: Get conversation history
    history = memory_service.get_conversation_history(session_id)
    print("\nConversation History Example:")
    print(json.dumps(history, indent=2))
    
    # Example: Get performance metrics
    metrics = memory_service.get_performance_metrics()
    print("\nPerformance Metrics Example:")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    # First run the conversion scripts to generate the knowledge base files
    import sys
    import subprocess
    
    print("Running CARC-RARC conversion script...")
    subprocess.run([sys.executable, "knowledge_base/carc_rarc/conversion_script.py"], check=True)
    
    print("Running Don't Bill Together conversion script...")
    subprocess.run([sys.executable, "knowledge_base/dont_bill_together/conversion_script.py"], check=True)
    
    print("Running Resolution Knowledge Base script...")
    subprocess.run([sys.executable, "knowledge_base/resolution/resolution_knowledge_base.py"], check=True)
    
    print("Running Memory Service Integration example...")
    run_memory_service_integration_example()
