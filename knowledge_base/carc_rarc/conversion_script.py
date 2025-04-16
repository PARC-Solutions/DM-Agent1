"""
CARC-RARC Knowledge Base Conversion Script

This script extracts CARC and RARC codes from the markdown documentation
and converts them into a structured JSON format for the knowledge base.
"""

import os
import re
import json
from typing import List, Dict, Any, Optional

# Define the path to the CARC-RARC markdown file
MARKDOWN_FILE = "../../Project Documentation/CARC-RARC-Codes.md"
OUTPUT_FILE = "carc_rarc_knowledge.json"

def extract_carc_codes(content: str) -> List[Dict[str, Any]]:
    """
    Extract CARC codes from the markdown content.
    
    Args:
        content: The markdown content
        
    Returns:
        List of dictionaries containing CARC code information
    """
    # Regular expression to match CARC code table rows
    pattern = r'\|\s*\*\*(\d+|[A-Z]\d+)\*\*\s*\|\s*\*\*([^|]+)\*\*\s*\|\s*([^|]*)\s*\|'
    matches = re.findall(pattern, content)
    
    carc_codes = []
    for match in matches:
        code, description, notes = match
        # Clean up the text
        code = code.strip()
        description = description.strip()
        notes = notes.strip()
        
        # Create structured entry
        entry = {
            "code": code,
            "description": description,
            "type": "CARC",
            "notes": notes if notes else None,
            "group_codes": [],  # Will be populated separately
            "related_rarcs": []  # Will be populated separately
        }
        carc_codes.append(entry)
    
    return carc_codes

def extract_group_codes(content: str) -> List[Dict[str, Any]]:
    """
    Extract Group Codes from the markdown content.
    
    Args:
        content: The markdown content
        
    Returns:
        List of dictionaries containing Group Code information
    """
    # Extract the Group Codes section
    group_codes_section = re.search(r'## Adjustment Group Codes \(Category Codes\)(.*?)##', content, re.DOTALL)
    
    if not group_codes_section:
        return []
    
    group_codes_content = group_codes_section.group(1)
    
    # Extract the group codes and descriptions
    pattern = r'\*\*(CO|PR|OA|PI|CR)\s*–\s*([^:]+):\*\*\s*([^(]*)(\([^)]*\))?'
    matches = re.findall(pattern, group_codes_content)
    
    group_codes = []
    for match in matches:
        code, title, description, parenthetical = match
        
        # Clean up the text
        title = title.strip()
        description = description.strip()
        
        entry = {
            "code": code,
            "title": title,
            "description": description,
            "type": "GROUP_CODE"
        }
        group_codes.append(entry)
    
    return group_codes

def extract_rarc_codes(content: str) -> List[Dict[str, Any]]:
    """
    Extract RARC codes from the markdown content.
    This is more challenging as they're not in a table format.
    
    Args:
        content: The markdown content
        
    Returns:
        List of dictionaries containing RARC code information
    """
    # Extract RARC section
    rarc_section = re.search(r'## Remittance Advice Remark Codes \(RARCs\)(.*?)##', content, re.DOTALL)
    
    if not rarc_section:
        return []
    
    rarc_content = rarc_section.group(1)
    
    # Extract RARC code patterns like MA01, N382, etc. mentioned in the text
    pattern = r'\*\*(MA\d+|MB\d+|N\d+|M\d+)\*\*\s*(?:–|-)?\s*(?:\*\*)?([^*]+)(?:\*\*)?'
    matches = re.findall(pattern, rarc_content)
    
    rarc_codes = []
    for match in matches:
        code, description = match
        
        # Clean up the description
        description = description.strip()
        if description.startswith("–") or description.startswith("-"):
            description = description[1:].strip()
        
        # Determine if this is an ALERT remark
        is_alert = "Alert:" in description
        
        entry = {
            "code": code,
            "description": description,
            "type": "RARC",
            "is_alert": is_alert,
            "related_carcs": []  # Will be populated separately
        }
        rarc_codes.append(entry)
    
    return rarc_codes

def link_carc_rarc_relationships(carc_codes: List[Dict[str, Any]], rarc_codes: List[Dict[str, Any]]) -> None:
    """
    Analyze the content to find relationships between CARC and RARC codes,
    then update the entries to reflect these relationships.
    
    Args:
        carc_codes: List of CARC code dictionaries
        rarc_codes: List of RARC code dictionaries
    """
    # Create lookup dictionaries
    carc_lookup = {entry["code"]: entry for entry in carc_codes}
    rarc_lookup = {entry["code"]: entry for entry in rarc_codes}
    
    # For each CARC code, look for mentions of RARC codes in its notes
    for carc in carc_codes:
        notes = carc.get("notes", "")
        if not notes:
            continue
        
        # Find all RARC codes mentioned in the notes
        rarc_mentions = re.findall(r'(MA\d+|MB\d+|N\d+|M\d+)', notes)
        
        for rarc_code in rarc_mentions:
            if rarc_code in rarc_lookup:
                # Add to CARC's related RARCs if not already there
                if rarc_code not in carc["related_rarcs"]:
                    carc["related_rarcs"].append(rarc_code)
                
                # Add to RARC's related CARCs if not already there
                rarc = rarc_lookup[rarc_code]
                if carc["code"] not in rarc["related_carcs"]:
                    rarc["related_carcs"].append(carc["code"])

def determine_group_code_applicability(carc_codes: List[Dict[str, Any]]) -> None:
    """
    Determine which group codes can be used with each CARC code based on the notes.
    
    Args:
        carc_codes: List of CARC code dictionaries
    """
    for carc in carc_codes:
        notes = carc.get("notes", "")
        if not notes:
            continue
        
        # Check for group code mentions
        if "Use only with Group Code CO" in notes:
            carc["group_codes"].append("CO")
        elif "Use only with Group Code PR" in notes:
            carc["group_codes"].append("PR")
        elif "Use only with Group Code OA" in notes:
            carc["group_codes"].append("OA")
        elif "Use only with Group Code PI" in notes:
            carc["group_codes"].append("PI")
        
        # Check for combined mentions
        if "Use only with Group Code PR or CO" in notes or "Use only with Group Code CO or PR" in notes:
            if "CO" not in carc["group_codes"]:
                carc["group_codes"].append("CO")
            if "PR" not in carc["group_codes"]:
                carc["group_codes"].append("PR")
        
        # If no specific group codes mentioned, assume all are valid
        if not carc["group_codes"]:
            carc["group_codes"] = ["CO", "PR", "OA", "PI"]

def add_resolution_placeholders(carc_codes: List[Dict[str, Any]]) -> None:
    """
    Add placeholder resolution steps for each CARC code.
    These will be filled in with actual resolution strategies later.
    
    Args:
        carc_codes: List of CARC code dictionaries
    """
    for carc in carc_codes:
        code_type = determine_denial_type(carc)
        carc["denial_type"] = code_type
        
        # Add placeholder resolution steps based on the denial type
        carc["resolution_steps"] = generate_placeholder_resolution(carc["code"], code_type)

def determine_denial_type(carc: Dict[str, Any]) -> str:
    """
    Determine the general type of denial based on the CARC code and description.
    
    Args:
        carc: CARC code dictionary
        
    Returns:
        String indicating the denial type
    """
    code = carc["code"]
    description = carc["description"].lower()
    
    if code in ["1", "2", "3"] or "deductible" in description or "coinsurance" in description or "copay" in description:
        return "patient_financial_responsibility"
    elif code in ["16", "125"] or "lacks information" in description or "submission error" in description:
        return "missing_information"
    elif code in ["29"] or "time limit" in description or "timely" in description:
        return "timely_filing"
    elif code in ["50", "96"] or "medical necessity" in description or "not covered" in description:
        return "medical_necessity"
    elif code in ["97", "234", "236"] or "included in" in description or "bundled" in description:
        return "bundling"
    elif code in ["18"] or "duplicate" in description:
        return "duplicate_claim"
    elif code in ["22", "23"] or "coordination of benefits" in description:
        return "coordination_of_benefits"
    elif code in ["4", "5", "6", "7", "8", "9", "10", "11", "12"] or "inconsistent" in description:
        return "coding_mismatch"
    else:
        return "other"

def generate_placeholder_resolution(code: str, denial_type: str) -> List[str]:
    """
    Generate placeholder resolution steps based on the denial type.
    
    Args:
        code: CARC code
        denial_type: Type of denial
        
    Returns:
        List of resolution steps
    """
    common_steps = [
        "Verify the information in the denial with the original claim submission",
        f"Check the specific CARC code ({code}) details and associated RARC codes for more context"
    ]
    
    if denial_type == "patient_financial_responsibility":
        return common_steps + [
            "Confirm patient's insurance coverage and benefit details",
            "Verify deductible, coinsurance, or copay amounts with payer",
            "Bill the patient for the applicable patient responsibility amount",
            "Consider checking if a secondary insurance might cover this amount"
        ]
    elif denial_type == "missing_information":
        return common_steps + [
            "Identify the specific missing information from the RARC code",
            "Gather the required information from patient records or by contacting the patient",
            "Resubmit the claim with complete information",
            "Consider using the appeals process if you believe all required information was originally submitted"
        ]
    elif denial_type == "timely_filing":
        return common_steps + [
            "Check if you have proof of timely submission (electronic confirmation, certified mail receipt)",
            "If you have proof, appeal the denial with documentation of timely filing",
            "If truly filed late, determine if there are extenuating circumstances that might support an exception",
            "Implement better tracking systems to prevent future timely filing issues"
        ]
    elif denial_type == "medical_necessity":
        return common_steps + [
            "Review documentation for evidence of medical necessity",
            "Check if the service meets Medicare's coverage criteria in LCDs/NCDs",
            "Ensure diagnosis codes accurately reflect the medical necessity for the service",
            "Appeal with additional documentation showing medical necessity",
            "Check if an Advance Beneficiary Notice (ABN) was obtained if service was potentially non-covered"
        ]
    elif denial_type == "bundling":
        return common_steps + [
            "Review NCCI edits and bundling rules for the specific codes billed",
            "Verify if modifiers (e.g., 59, XE, XP, XS, XU) are appropriate to indicate separate services",
            "Check if services were performed at different sessions, different sites, or separate injuries",
            "If services were truly separate and distinct, resubmit with appropriate modifiers"
        ]
    elif denial_type == "duplicate_claim":
        return common_steps + [
            "Check records to verify if this is truly a duplicate claim",
            "If not a duplicate, gather evidence showing differences in dates, services, or other factors",
            "Appeal with documentation showing why the claims are separate billable services",
            "Implement claim tracking system to prevent accidental duplicate submissions"
        ]
    elif denial_type == "coordination_of_benefits":
        return common_steps + [
            "Verify primary insurance information with the patient",
            "Obtain the primary EOB if billing a secondary payer",
            "Ensure the claim was properly submitted with primary insurance payment information",
            "Resubmit to the correct primary payer if claims were sent to the wrong insurance"
        ]
    elif denial_type == "coding_mismatch":
        return common_steps + [
            "Review coding for inconsistencies between procedure and diagnosis codes",
            "Ensure codes are appropriate for patient's age, gender, and condition",
            "Verify procedure codes are valid for the place of service billed",
            "Correct any coding errors and resubmit the claim"
        ]
    else:  # "other"
        return common_steps + [
            "Review all claim details to identify potential issues",
            "Contact the payer for additional information about the denial reason",
            "Determine if additional documentation could resolve the issue",
            "Consider appeal options if denial seems incorrect"
        ]

def main():
    # Read the markdown file
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract codes
    carc_codes = extract_carc_codes(content)
    group_codes = extract_group_codes(content)
    rarc_codes = extract_rarc_codes(content)
    
    # Process relationships
    link_carc_rarc_relationships(carc_codes, rarc_codes)
    determine_group_code_applicability(carc_codes)
    add_resolution_placeholders(carc_codes)
    
    # Combine all data
    knowledge_base = {
        "carc_codes": carc_codes,
        "rarc_codes": rarc_codes,
        "group_codes": group_codes,
        "metadata": {
            "version": "1.0.0",
            "created_at": "2025-04-16",
            "source": "CMS documentation"
        }
    }
    
    # Save to JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        json.dump(knowledge_base, file, indent=2)
    
    print(f"Successfully extracted {len(carc_codes)} CARC codes, {len(rarc_codes)} RARC codes, and {len(group_codes)} Group Codes.")
    print(f"Knowledge base saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
