"""
Don't Bill Together Knowledge Base Conversion Script

This script extracts code pair edits from the markdown documentation
and converts them into a structured JSON format for the knowledge base.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional

# Define the path to the Don't Bill Together markdown file
MARKDOWN_FILE = "../../Project Documentation/Dont_Bill_Together.md"
OUTPUT_FILE = "dont_bill_together_knowledge.json"

def extract_code_pairs(content: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract code pairs that should not be billed together from the markdown content.
    
    Args:
        content: The markdown content
        
    Returns:
        Dictionary with two keys: "modifier_not_allowed" and "modifier_allowed",
        each containing a list of code pair dictionaries
    """
    # Extract the two main sections
    modifier_not_allowed_section = re.search(
        r'## Code Pairs with Modifier Indicator \*\*0\*\* \(Modifier Not Allowed\)(.*?)## Code Pairs with Modifier Indicator',
        content, 
        re.DOTALL
    )
    
    modifier_allowed_section = re.search(
        r'## Code Pairs with Modifier Indicator \*\*1\*\* \(Modifier Allowed\)(.*?)---',
        content,
        re.DOTALL
    )
    
    result = {
        "modifier_not_allowed": [],
        "modifier_allowed": []
    }
    
    # Process the modifier not allowed section
    if modifier_not_allowed_section:
        section_content = modifier_not_allowed_section.group(1)
        table_rows = re.findall(r'\|\s*\*\*([^\*]+)\*\*[^|]*\|\s*\*\*([^\*]+)\*\*[^|]*\|\s*(\d)\s*\|\s*(\d+)\s*\|\s*([^|]*)\|', section_content)
        
        for row in table_rows:
            col1_code, col2_code, modifier_indicator, effective_date, deletion_date = row
            
            # Clean up and extract the base code without description
            col1_code = extract_code(col1_code)
            col2_code = extract_code(col2_code)
            
            # Create the entry
            entry = {
                "column1_code": col1_code,
                "column2_code": col2_code,
                "modifier_indicator": "0",  # Always 0 in this section
                "effective_date": effective_date.strip(),
                "deletion_date": deletion_date.strip() if deletion_date.strip() != "–" else None
            }
            
            result["modifier_not_allowed"].append(entry)
    
    # Process the modifier allowed section
    if modifier_allowed_section:
        section_content = modifier_allowed_section.group(1)
        table_rows = re.findall(r'\|\s*\*\*([^\*]+)\*\*[^|]*\|\s*\*\*([^\*]+)\*\*[^|]*\|\s*(\d)\s*\|\s*(\d+)\s*\|\s*([^|]*)\|', section_content)
        
        for row in table_rows:
            col1_code, col2_code, modifier_indicator, effective_date, deletion_date = row
            
            # Clean up and extract the base code without description
            col1_code = extract_code(col1_code)
            col2_code = extract_code(col2_code)
            
            # Create the entry
            entry = {
                "column1_code": col1_code,
                "column2_code": col2_code,
                "modifier_indicator": "1",  # Always 1 in this section
                "effective_date": effective_date.strip(),
                "deletion_date": deletion_date.strip() if deletion_date.strip() != "–" else None
            }
            
            result["modifier_allowed"].append(entry)
    
    return result

def extract_code(code_text: str) -> str:
    """
    Extract the CPT/HCPCS code from a text that may include a description.
    
    Args:
        code_text: Text containing a code possibly followed by a description
        
    Returns:
        The code portion only
    """
    # Pattern to match a code at the beginning of the text
    match = re.match(r'(\d{5}|\d{4}[A-Z]|[A-Z]\d{4})', code_text.strip())
    if match:
        return match.group(1)
    
    # If not found, try to get the whole string up to the first space or dash
    parts = re.split(r'[\s–-]', code_text.strip(), 1)
    return parts[0].strip()

def extract_allowed_modifiers() -> List[str]:
    """
    Extract the list of allowed NCCI modifiers that can be used to bypass edits.
    
    Returns:
        List of modifier codes
    """
    # These are the standard NCCI-associated modifiers that may allow code pairs to be billed together
    return [
        "24", "25", "27", "57", "58", "59", "78", "79", 
        "91", "E1", "E2", "E3", "E4", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9",
        "FA", "FB", "FC", "GG", "GL", "GN", "GS", "GU", "GX", "GY", "GZ", "KX", "LT", "RT", 
        "TC", "XE", "XP", "XS", "XU"
    ]

def add_resolution_guidance(code_pairs: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Add resolution guidance to each code pair based on its modifier indicator.
    
    Args:
        code_pairs: Dictionary with modifier_not_allowed and modifier_allowed lists
    """
    # Add guidance for modifier not allowed pairs
    for pair in code_pairs["modifier_not_allowed"]:
        pair["resolution_guidance"] = [
            f"These codes ({pair['column1_code']} and {pair['column2_code']}) cannot be billed together under any circumstances.",
            "This is a hard edit in NCCI and cannot be bypassed with any modifier.",
            "If both services were truly provided, you may only bill for the Column 1 code.",
            "If both services were provided at separate encounters on the same day, consider using different dates of service if appropriate.",
            "Check if an alternative code combination could accurately represent the services provided."
        ]
    
    # Add guidance for modifier allowed pairs
    for pair in code_pairs["modifier_allowed"]:
        pair["resolution_guidance"] = [
            f"These codes ({pair['column1_code']} and {pair['column2_code']}) cannot be billed together unless the services are distinct and separate.",
            "If the services were performed at different sites, different sessions, or for different conditions, you may append an appropriate modifier to the Column 2 code.",
            "Appropriate modifiers include: 59 (Distinct procedural service), XE (Separate encounter), XS (Separate structure), XP (Separate practitioner), or XU (Unusual non-overlapping service).",
            "Document thoroughly why the services are separate and distinct.",
            "Ensure medical necessity for both services is clearly established in the documentation."
        ]

def add_examples_and_documentation_requirements(code_pairs: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Add example scenarios and documentation requirements for code pairs.
    
    Args:
        code_pairs: Dictionary with modifier_not_allowed and modifier_allowed lists
    """
    # Add general examples based on code patterns
    for category in ["modifier_not_allowed", "modifier_allowed"]:
        for pair in code_pairs[category]:
            col1_code = pair["column1_code"]
            col2_code = pair["column2_code"]
            
            # Lab panel examples (80000 series)
            if col1_code.startswith("80") and col2_code.startswith("8"):
                pair["example_scenario"] = (
                    f"Panel code {col1_code} includes the individual test {col2_code}. "
                    "Example: A lipid panel (80061) includes cholesterol (82465), so billing both would be duplicate billing."
                )
                pair["documentation_requirements"] = [
                    "Document only the panel code when all components were performed.",
                    "If additional tests beyond the panel were performed, document their medical necessity separately."
                ]
            
            # Surgery examples (10000-69999 series)
            elif re.match(r"^[1-6]\d{4}$", col1_code) and re.match(r"^[1-6]\d{4}$", col2_code):
                pair["example_scenario"] = (
                    f"Surgical procedure {col1_code} typically includes {col2_code} as part of the same operative session. "
                    "Example: When a more comprehensive procedure includes a lesser one as a component."
                )
                pair["documentation_requirements"] = [
                    "Operative report must clearly document each procedure performed.",
                    "For modifier-allowed pairs, document why procedures were distinct (different site, session, etc.).",
                    "Include anatomical details, separate incisions, or timing differences if applicable."
                ]
            
            # Therapy examples (90000-99999 series)
            elif re.match(r"^9\d{4}$", col1_code) and re.match(r"^9\d{4}$", col2_code):
                pair["example_scenario"] = (
                    f"Therapy codes {col1_code} and {col2_code} represent services that overlap or are mutually exclusive. "
                    "Example: Certain therapy modalities that cannot be reasonably provided during the same session."
                )
                pair["documentation_requirements"] = [
                    "Document start and end times for each therapy service.",
                    "For modifier-allowed pairs, clearly indicate different goals or treatment focus.",
                    "Include separate progress notes if services were provided at different times."
                ]
            
            # Default example
            else:
                pair["example_scenario"] = (
                    f"Codes {col1_code} and {col2_code} represent services that are either components of each other "
                    "or mutually exclusive according to CPT coding guidelines and CMS policy."
                )
                pair["documentation_requirements"] = [
                    "Clearly document medical necessity for each service.",
                    "If using modifiers (when allowed), document why services were separate and distinct.",
                    "Include relevant timing, anatomical sites, and separate documentation for each service."
                ]

def main():
    # Read the markdown file
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract code pairs
    code_pairs = extract_code_pairs(content)
    
    # Add guidance and examples
    add_resolution_guidance(code_pairs)
    add_examples_and_documentation_requirements(code_pairs)
    
    # Get allowed modifiers
    allowed_modifiers = extract_allowed_modifiers()
    
    # Combine all data
    knowledge_base = {
        "code_pairs": code_pairs,
        "allowed_modifiers": allowed_modifiers,
        "metadata": {
            "version": "1.0.0",
            "created_at": "2025-04-16",
            "source": "CMS NCCI edits documentation"
        }
    }
    
    # Save to JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        json.dump(knowledge_base, file, indent=2)
    
    not_allowed_count = len(code_pairs["modifier_not_allowed"])
    allowed_count = len(code_pairs["modifier_allowed"])
    print(f"Successfully extracted {not_allowed_count} 'modifier not allowed' code pairs and {allowed_count} 'modifier allowed' code pairs.")
    print(f"Knowledge base saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
