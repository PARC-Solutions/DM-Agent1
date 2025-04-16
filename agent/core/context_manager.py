"""
Context Management System

This module implements the context management system for maintaining and passing context
between agents in the Medical Billing Denial Agent system. It handles context enrichment,
truncation, and persistence across conversation turns.

Features:
- Context storage and retrieval
- Context enrichment with relevant information
- Context truncation to maintain manageable context size
- Context passing between agents
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Union
from collections import deque

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Context Manager for maintaining and passing context between agents.
    
    This class provides functionality to store, retrieve, and manipulate context
    information throughout a conversation, ensuring relevant information is maintained
    while keeping context size manageable.
    """
    
    def __init__(self, max_context_size: int = 2048):
        """
        Initialize the context manager.
        
        Args:
            max_context_size: Maximum size of context in tokens
                             (approximate, based on character count)
        """
        self.max_context_size = max_context_size
        self.token_approx_ratio = 4  # Approximate characters per token
        
    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate the token count of a string.
        
        This is a simple approximation. In production, this would use
        a more accurate token counting method based on the tokenizer
        used by the LLM.
        
        Args:
            text: The text to estimate token count for
            
        Returns:
            Estimated token count
        """
        return len(text) // self.token_approx_ratio
    
    def _truncate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Truncate context to fit within the maximum token limit.
        
        This method applies different truncation strategies based on the
        content type:
        - Conversation history: Keep most recent entries
        - Document content: Summarize or truncate to key sections
        - Metadata: Preserve all
        
        Args:
            context: The context to truncate
            
        Returns:
            Truncated context
        """
        truncated = context.copy()
        
        # Estimate token count of serialized context
        context_str = json.dumps(truncated)
        estimated_tokens = self._estimate_token_count(context_str)
        
        if estimated_tokens <= self.max_context_size:
            return truncated
        
        # We need to truncate, focusing on large text fields first
        # Handle conversation history if present
        if "conversation_history" in truncated and isinstance(truncated["conversation_history"], list):
            # Keep most recent conversations, dropping oldest first
            while estimated_tokens > self.max_context_size and truncated["conversation_history"]:
                # Remove oldest conversation turn
                truncated["conversation_history"].pop(0)
                # Re-estimate token count
                context_str = json.dumps(truncated)
                estimated_tokens = self._estimate_token_count(context_str)
        
        # Handle document content if present
        for doc_key in ["document_content", "documents", "extracted_text"]:
            if doc_key in truncated and estimated_tokens > self.max_context_size:
                # For document content, we could apply more sophisticated truncation
                # like extracting key sections or summarizing, but for now we'll
                # simply truncate to a percentage of the original
                if isinstance(truncated[doc_key], str):
                    content_tokens = self._estimate_token_count(truncated[doc_key])
                    # Calculate what percentage we can keep
                    keep_ratio = max(0.1, (self.max_context_size - (estimated_tokens - content_tokens)) / content_tokens)
                    # Truncate the content
                    keep_chars = int(len(truncated[doc_key]) * keep_ratio)
                    truncated[doc_key] = truncated[doc_key][:keep_chars] + " [...truncated...]"
                    # Re-estimate token count
                    context_str = json.dumps(truncated)
                    estimated_tokens = self._estimate_token_count(context_str)
                elif isinstance(truncated[doc_key], list):
                    # If it's a list of documents, truncate each one or remove some
                    while estimated_tokens > self.max_context_size and truncated[doc_key]:
                        truncated[doc_key].pop(0)  # Remove oldest document
                        context_str = json.dumps(truncated)
                        estimated_tokens = self._estimate_token_count(context_str)
        
        # If we still exceed token count, make more aggressive cuts
        if estimated_tokens > self.max_context_size:
            # Remove lower priority fields that can be regenerated or aren't critical
            lower_priority_fields = [
                "extracted_entities", "similar_cases", "reference_materials",
                "debug_info", "previous_analysis"
            ]
            
            for field in lower_priority_fields:
                if field in truncated and estimated_tokens > self.max_context_size:
                    del truncated[field]
                    context_str = json.dumps(truncated)
                    estimated_tokens = self._estimate_token_count(context_str)
        
        # Log that truncation occurred
        logger.info(f"Context truncated from {self._estimate_token_count(json.dumps(context))} to {estimated_tokens} estimated tokens")
        
        return truncated
    
    def enrich_context(self, context: Dict[str, Any], 
                       supplementary_info: Dict[str, Any],
                       priority_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich context with supplementary information.
        
        This method adds new information to the context, prioritizing certain
        fields if specified, and ensures the context stays within token limits.
        
        Args:
            context: The base context to enrich
            supplementary_info: Additional information to add to the context
            priority_fields: Optional list of field names to prioritize
            
        Returns:
            Enriched context
        """
        # Start with a copy of the original context
        enriched = context.copy()
        
        # Add supplementary info, handling special cases for certain fields
        for key, value in supplementary_info.items():
            if key in enriched:
                # Special handling for lists that should be appended
                if isinstance(enriched[key], list) and isinstance(value, list):
                    enriched[key].extend(value)
                # Special handling for dictionaries that should be merged
                elif isinstance(enriched[key], dict) and isinstance(value, dict):
                    enriched[key].update(value)
                # Special handling for conversation history
                elif key == "conversation_history" and isinstance(value, dict):
                    if "conversation_history" not in enriched:
                        enriched["conversation_history"] = []
                    enriched["conversation_history"].append(value)
                # Default case: overwrite existing value
                else:
                    enriched[key] = value
            else:
                # Key doesn't exist in original context, so add it
                enriched[key] = value
        
        # If we have priority fields, ensure they're included even during truncation
        if priority_fields:
            # Create a priority subset for truncation
            priority_data = {k: enriched[k] for k in priority_fields if k in enriched}
            
            # Truncate the context
            truncated = self._truncate_context(enriched)
            
            # Ensure priority fields are preserved
            for key, value in priority_data.items():
                truncated[key] = value
                
            return truncated
        else:
            # No priority fields, just truncate normally
            return self._truncate_context(enriched)
    
    def extract_agent_specific_context(self, context: Dict[str, Any], 
                                      agent_name: str,
                                      required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Extract context specific to a particular agent.
        
        This method filters the context to include only information relevant
        to the specified agent, based on agent-specific rules and required fields.
        
        Args:
            context: The full context
            agent_name: The name of the agent to extract context for
            required_fields: Optional list of field names that must be included
            
        Returns:
            Agent-specific context
        """
        # Define agent-specific context rules
        agent_context_rules = {
            "denial_classifier": [
                "carc_code", "rarc_code", "group_code", "denial_codes",
                "payer_information", "claim_details"
            ],
            "claims_analyzer": [
                "document_content", "documents", "extracted_text", "claim_details",
                "patient_information", "provider_information", "procedure_codes",
                "diagnosis_codes"
            ],
            "remediation_advisor": [
                "denial_type", "carc_code", "rarc_code", "claim_details",
                "previous_analysis", "provider_information", "payer_information"
            ],
            # Default rule includes basic conversation and metadata
            "default": [
                "conversation_history", "session_id", "user_id", "timestamps",
                "metadata"
            ]
        }
        
        # Get the list of fields relevant for this agent
        agent_fields = agent_context_rules.get(agent_name, [])
        agent_fields.extend(agent_context_rules["default"])
        
        # If required fields were specified, add them
        if required_fields:
            agent_fields.extend(required_fields)
            
        # Remove duplicates while preserving order
        agent_fields = list(dict.fromkeys(agent_fields))
        
        # Extract only the relevant fields
        agent_context = {field: context[field] for field in agent_fields if field in context}
        
        # Add agent_name to help the agent identify itself
        agent_context["agent_name"] = agent_name
        
        # Add a timestamp for when this context was extracted
        agent_context["context_timestamp"] = time.time()
        
        return agent_context
    
    def merge_agent_results(self, base_context: Dict[str, Any],
                           agent_results: List[Dict[str, Any]],
                           preserve_fields: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Merge results from multiple agents into a unified context.
        
        This method combines the results from different agents, resolving conflicts
        and maintaining the most relevant and recent information.
        
        Args:
            base_context: The starting context
            agent_results: List of result contexts from different agents
            preserve_fields: Optional set of field names to always preserve from base_context
            
        Returns:
            Merged context
        """
        # Start with a copy of the base context
        merged = base_context.copy()
        
        # Fields that should be preserved from the base context if present
        if preserve_fields is None:
            preserve_fields = {
                "session_id", "user_id", "conversation_history", 
                "timestamps", "metadata", "documents"
            }
        
        # Track conflicts for logging
        conflicts = {}
        
        # Process each agent's results
        for result in agent_results:
            for key, value in result.items():
                # Skip agent identification fields
                if key in {"agent_name", "context_timestamp"}:
                    continue
                    
                # If the field is in preserve_fields, don't overwrite it
                if key in preserve_fields:
                    continue
                    
                # Handle special cases
                if key in merged:
                    # If it's a list, extend it
                    if isinstance(merged[key], list) and isinstance(value, list):
                        merged[key].extend(value)
                        # Remove duplicates while preserving order
                        merged[key] = list(dict.fromkeys(merged[key]))
                    # If it's a dict, update it
                    elif isinstance(merged[key], dict) and isinstance(value, dict):
                        merged[key].update(value)
                    # Otherwise, potential conflict
                    else:
                        # Track the conflict
                        if key not in conflicts:
                            conflicts[key] = []
                        conflicts[key].append((result.get("agent_name", "unknown"), value))
                        
                        # For now, newer values overwrite older ones
                        # In a more sophisticated system, we could use confidence scores
                        # or agent priorities to resolve conflicts
                        merged[key] = value
                else:
                    # No conflict, just add the new value
                    merged[key] = value
        
        # Log conflicts if any
        if conflicts:
            conflict_info = {
                field: [f"{agent}: {value}" for agent, value in agents]
                for field, agents in conflicts.items()
            }
            logger.info(f"Resolved context conflicts: {json.dumps(conflict_info)}")
        
        # Ensure context doesn't exceed token limits
        return self._truncate_context(merged)
