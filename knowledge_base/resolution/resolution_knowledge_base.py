"""
Resolution Knowledge Base

This module implements the knowledge base for denial resolution strategies.
It contains structured information about how to resolve different types of
denials based on CMS guidelines and best practices.
"""

import json
import os
from typing import Dict, List, Any, Optional

class ResolutionKnowledgeBase:
    """
    A knowledge base for denial resolution strategies organized by denial type.
    """
    
    def __init__(self):
        """
        Initialize the resolution knowledge base with structured resolution strategies.
        """
        self.resolution_strategies = self._initialize_resolution_strategies()
        self.billing_rule_references = self._initialize_billing_rule_references()
        
    def _initialize_resolution_strategies(self) -> Dict[str, Any]:
        """
        Initialize the resolution strategies for different denial types.
        
        Returns:
            Dictionary of resolution strategies by denial type
        """
        return {
            "missing_information": {
                "name": "Missing Information",
                "description": "Denial due to incomplete or missing information on the claim",
                "related_carcs": ["16", "125", "226", "227", "228"],
                "general_steps": [
                    "Identify the specific information that's missing",
                    "Gather the required information from patient records or by contacting the patient",
                    "Verify the information for accuracy and completeness",
                    "Resubmit the claim with the complete information"
                ],
                "specific_strategies": {
                    "missing_diagnosis": [
                        "Review patient's medical record to identify all applicable diagnoses",
                        "Ensure diagnosis codes are current and valid for the date of service",
                        "Verify the diagnosis codes support medical necessity for the procedure",
                        "Submit a corrected claim with appropriate diagnosis codes"
                    ],
                    "missing_provider_information": [
                        "Verify provider's NPI (National Provider Identifier) is valid",
                        "Ensure all required provider credentials are included",
                        "Confirm provider's billing information is up-to-date",
                        "Submit a corrected claim with complete provider information"
                    ],
                    "missing_patient_information": [
                        "Verify patient's demographic information (name, DOB, gender, etc.)",
                        "Confirm patient's insurance information and coverage dates",
                        "Update patient information in the billing system",
                        "Submit a corrected claim with complete patient information"
                    ],
                    "missing_service_information": [
                        "Review documentation to ensure all service details are captured",
                        "Verify correct CPT/HCPCS codes and modifiers were used",
                        "Ensure units, dates, and place of service are accurate",
                        "Submit a corrected claim with complete service information"
                    ]
                },
                "documentation_requirements": [
                    "Complete and signed consent forms",
                    "Detailed clinical notes supporting the services provided",
                    "Completed CMS-1500 or UB-04 forms with all required fields",
                    "Any requested additional documentation"
                ]
            },
            "medical_necessity": {
                "name": "Medical Necessity",
                "description": "Denial because the service is not deemed medically necessary",
                "related_carcs": ["50", "55", "56", "167"],
                "general_steps": [
                    "Review the denial and identify the specific medical necessity issue",
                    "Check relevant LCD (Local Coverage Determination) or NCD (National Coverage Determination) policies",
                    "Gather supporting clinical documentation that demonstrates medical necessity",
                    "File an appeal with additional documentation and clinical justification"
                ],
                "specific_strategies": {
                    "diagnosis_not_covered": [
                        "Review Medicare coverage guidelines for the specific condition",
                        "Verify if the diagnosis meets the coverage criteria outlined in the LCD/NCD",
                        "Consider alternative diagnosis codes that accurately reflect the patient's condition and are covered",
                        "Obtain physician documentation clearly establishing medical necessity",
                        "Appeal with supporting clinical documentation and references to Medicare policies"
                    ],
                    "frequency_limitation": [
                        "Review Medicare frequency limitations for the specific service",
                        "Document why the service was needed more frequently than typically allowed",
                        "Obtain a letter of medical necessity from the ordering physician",
                        "Appeal with documentation supporting the medical necessity of the additional service"
                    ],
                    "experimental_service": [
                        "Determine if the service is considered experimental/investigational by Medicare",
                        "Check for any recent updates to Medicare policy that might now cover the service",
                        "Gather peer-reviewed studies supporting the service's effectiveness",
                        "Appeal with scientific evidence and physician statements about treatment appropriateness"
                    ]
                },
                "documentation_requirements": [
                    "Clear physician orders with specific details",
                    "Comprehensive progress notes showing need for service",
                    "Results of any relevant diagnostic tests supporting the need for service",
                    "Documentation of failed conservative treatments when applicable",
                    "Letters of medical necessity with clinical justification"
                ]
            },
            "bundling": {
                "name": "Bundling/Unbundling",
                "description": "Denial because services should be billed together or are included in another service",
                "related_carcs": ["97", "234", "236"],
                "general_steps": [
                    "Review the NCCI (National Correct Coding Initiative) edits for the code pair",
                    "Determine if the services were truly separate and distinct",
                    "Check if appropriate modifiers can be used to bypass the edit",
                    "Resubmit with appropriate coding or modifiers if applicable"
                ],
                "specific_strategies": {
                    "component_included_in_comprehensive_code": [
                        "Verify the NCCI edits to confirm bundling requirements",
                        "Review documentation to determine if services were distinct and separate",
                        "If truly separate services, append modifier 59 or appropriate X-modifier (XE, XP, XS, XU) to the component code",
                        "Ensure documentation clearly supports the separate nature of the services"
                    ],
                    "mutually_exclusive_procedures": [
                        "Verify if the code pair is marked as mutually exclusive in NCCI",
                        "Determine if modifier indicator is '0' (not allowed) or '1' (allowed with modifier)",
                        "For modifier indicator '1', use appropriate modifier if services were truly distinct",
                        "For modifier indicator '0', bill only the primary procedure"
                    ],
                    "lab_panels": [
                        "Check if individual labs are components of a panel code",
                        "Bill only the panel code when all component tests were performed",
                        "Document medical necessity for tests performed outside the panel"
                    ]
                },
                "documentation_requirements": [
                    "Separate procedure notes for distinct services",
                    "Documentation of different body sites, separate incisions, or separate lesions",
                    "Timing documentation if services were performed at different sessions",
                    "Medical necessity for each separate procedure"
                ]
            },
            "timely_filing": {
                "name": "Timely Filing",
                "description": "Denial because claim was not submitted within the required time frame",
                "related_carcs": ["29"],
                "general_steps": [
                    "Verify the timely filing deadline for the payer",
                    "Gather evidence of original timely submission",
                    "Submit an appeal with documentation of timely filing",
                    "Implement processes to prevent future timely filing issues"
                ],
                "specific_strategies": {
                    "proof_of_timely_filing": [
                        "Gather electronic submission records with confirmation numbers",
                        "Collect certified mail receipts or fax confirmation sheets if applicable",
                        "Document prior claim rejections or development requests within the timely filing period",
                        "Appeal with evidence of original submission within the timely filing limit"
                    ],
                    "exceptions_to_timely_filing": [
                        "Document administrative delays by the payer if applicable",
                        "Provide evidence of retroactive eligibility if applicable",
                        "Document system issues or natural disasters that prevented timely filing",
                        "Request exception to the timely filing rule with supporting documentation"
                    ]
                },
                "documentation_requirements": [
                    "Original claim submission confirmation with date stamp",
                    "Electronic clearinghouse reports showing original submission date",
                    "Correspondence with payer during the timely filing period",
                    "Documentation of any extenuating circumstances"
                ]
            },
            "coordination_of_benefits": {
                "name": "Coordination of Benefits",
                "description": "Denial due to other insurance primary or COB issues",
                "related_carcs": ["22", "23", "24", "109", "200", "201"],
                "general_steps": [
                    "Verify the patient's insurance coverage and primary/secondary payers",
                    "Obtain EOB (Explanation of Benefits) from the primary insurance",
                    "Submit claim to the correct primary payer or with primary EOB information",
                    "Appeal with documentation of correct coordination of benefits"
                ],
                "specific_strategies": {
                    "medicare_secondary_payer": [
                        "Determine why Medicare is secondary (working aged, disability, ESRD, etc.)",
                        "Obtain the primary payer's EOB showing processing of the claim",
                        "Verify the primary payer's payment information is included on the Medicare claim",
                        "Submit to Medicare with appropriate MSP information and primary EOB"
                    ],
                    "other_insurance_information_missing": [
                        "Verify current insurance information with the patient",
                        "Complete insurance verification to identify all applicable policies",
                        "Update patient insurance information in the billing system",
                        "Resubmit with complete information about all applicable coverage"
                    ]
                },
                "documentation_requirements": [
                    "Primary insurance EOB or remittance advice",
                    "Completed MSP questionnaire for Medicare patients",
                    "Documentation of termination of other coverage if applicable",
                    "Evidence of correct insurance effective dates"
                ]
            },
            "duplicate_claim": {
                "name": "Duplicate Claim",
                "description": "Denial because the claim is identified as a duplicate submission",
                "related_carcs": ["18"],
                "general_steps": [
                    "Verify if the claim is truly a duplicate",
                    "If not a duplicate, gather evidence of unique services",
                    "Appeal with documentation of separate services if applicable",
                    "Implement tracking systems to prevent duplicate submissions"
                ],
                "specific_strategies": {
                    "true_duplicate": [
                        "Confirm the claim is actually a duplicate of a previously processed claim",
                        "Check if the original claim was paid correctly",
                        "If original was paid correctly, no further action needed",
                        "If original claim had issues, correct those issues rather than resubmitting"
                    ],
                    "not_a_duplicate": [
                        "Gather documentation showing the services are distinct (different DOS, CPT codes, etc.)",
                        "Highlight differences between the current claim and the supposed duplicate",
                        "Appeal with clear evidence that the claim is not a duplicate"
                    ]
                },
                "documentation_requirements": [
                    "Original claim information and processing details",
                    "Documentation showing differences between claims if not a duplicate",
                    "Unique identifiers for each service (different times, sites, procedures)"
                ]
            },
            "patient_financial_responsibility": {
                "name": "Patient Financial Responsibility",
                "description": "Adjustment for patient responsibility amounts (deductible, coinsurance, co-pay)",
                "related_carcs": ["1", "2", "3"],
                "general_steps": [
                    "Verify the patient's benefits and financial responsibility",
                    "Confirm deductible, coinsurance, or co-pay amounts with the payer",
                    "Bill the patient for the applicable responsibility amount",
                    "Consider checking if a secondary insurance might cover the patient portion"
                ],
                "specific_strategies": {
                    "deductible": [
                        "Verify patient's current deductible status with the insurance",
                        "Inform patient of their deductible responsibility",
                        "Bill patient for the deductible amount",
                        "Check for secondary insurance that might cover the deductible"
                    ],
                    "coinsurance": [
                        "Verify the correct coinsurance percentage for the service",
                        "Calculate the correct patient responsibility amount",
                        "Bill patient for the coinsurance amount",
                        "Submit to secondary insurance if applicable"
                    ],
                    "co-payment": [
                        "Verify the correct co-pay amount for the service type",
                        "Collect co-pay at time of service when possible",
                        "Bill patient for any uncollected co-pays"
                    ]
                },
                "documentation_requirements": [
                    "Insurance verification showing patient responsibility amounts",
                    "EOB clearly indicating patient financial responsibility",
                    "Documentation of benefits education provided to patient"
                ]
            },
            "coding_mismatch": {
                "name": "Coding Mismatch",
                "description": "Denial due to inconsistency between diagnostic and procedure codes or other coding issues",
                "related_carcs": ["4", "5", "6", "7", "8", "9", "10", "11", "12", "146", "167", "181", "182"],
                "general_steps": [
                    "Identify the specific coding mismatch or issue",
                    "Review medical documentation to determine correct coding",
                    "Correct the coding mismatch based on documentation",
                    "Resubmit with correct coding and supportive documentation"
                ],
                "specific_strategies": {
                    "diagnosis_procedure_mismatch": [
                        "Review medical documentation to verify the correct diagnosis",
                        "Ensure the diagnosis supports medical necessity for the procedure",
                        "Correct diagnosis coding to accurately reflect the patient's condition",
                        "Resubmit with diagnosis codes that support the procedures performed"
                    ],
                    "gender_specific_coding": [
                        "Verify patient's gender in the medical record",
                        "Ensure procedure and diagnosis codes are appropriate for the patient's gender",
                        "Correct any gender-specific coding errors",
                        "Resubmit with gender-appropriate coding"
                    ],
                    "age_specific_coding": [
                        "Verify patient's age on the date of service",
                        "Ensure procedure and diagnosis codes are appropriate for the patient's age",
                        "Correct any age-specific coding errors",
                        "Resubmit with age-appropriate coding"
                    ],
                    "invalid_code_combination": [
                        "Check for correct code linkage between procedures and diagnoses",
                        "Review LCD/NCD policies for covered diagnosis-procedure combinations",
                        "Correct coding to reflect appropriate linkage",
                        "Resubmit with valid code combinations"
                    ]
                },
                "documentation_requirements": [
                    "Medical records supporting the correct diagnosis",
                    "Documentation of medical necessity for the procedure",
                    "Evidence of the relationship between diagnosis and procedures",
                    "Current coding guidelines supporting code selection"
                ]
            }
        }
    
    def _initialize_billing_rule_references(self) -> Dict[str, Any]:
        """
        Initialize references to billing rules and CMS guidelines.
        
        Returns:
            Dictionary of billing rule references
        """
        return {
            "medicare_manuals": [
                {
                    "title": "Medicare Claims Processing Manual",
                    "url": "https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Internet-Only-Manuals-IOMs-Items/CMS018912",
                    "chapters_of_interest": [
                        {"chapter": 1, "title": "General Billing Requirements"},
                        {"chapter": 12, "title": "Physicians/Non-physician Practitioners"},
                        {"chapter": 16, "title": "Laboratory Services"},
                        {"chapter": 23, "title": "Fee Schedule Administration and Coding Requirements"},
                        {"chapter": 30, "title": "Financial Liability Protections"}
                    ]
                },
                {
                    "title": "Medicare Benefit Policy Manual",
                    "url": "https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Internet-Only-Manuals-IOMs-Items/CMS012673",
                    "chapters_of_interest": [
                        {"chapter": 15, "title": "Covered Medical and Other Health Services"},
                        {"chapter": 16, "title": "General Exclusions from Coverage"}
                    ]
                },
                {
                    "title": "Medicare Program Integrity Manual",
                    "url": "https://www.cms.gov/Regulations-and-Guidance/Guidance/Manuals/Internet-Only-Manuals-IOMs-Items/CMS019033",
                    "chapters_of_interest": [
                        {"chapter": 3, "title": "Verifying Potential Errors and Taking Corrective Actions"},
                        {"chapter": 13, "title": "Local Coverage Determinations"}
                    ]
                }
            ],
            "coverage_policies": [
                {
                    "title": "National Coverage Determinations (NCDs)",
                    "url": "https://www.cms.gov/medicare-coverage-database/indexes/ncd-alphabetical-index.aspx",
                    "description": "Medicare's national policy statements for coverage of specific medical services"
                },
                {
                    "title": "Local Coverage Determinations (LCDs)",
                    "url": "https://www.cms.gov/medicare-coverage-database/indexes/lcd-alphabetical-index.aspx",
                    "description": "Medicare Administrative Contractors' policies for services covered in their jurisdictions"
                }
            ],
            "coding_references": [
                {
                    "title": "National Correct Coding Initiative (NCCI)",
                    "url": "https://www.cms.gov/Medicare/Coding/NationalCorrectCodInitEd",
                    "description": "CMS edits to promote correct coding and control improper coding that leads to inappropriate payment"
                },
                {
                    "title": "CMS ICD-10-CM Official Guidelines",
                    "url": "https://www.cms.gov/medicare/icd-10/2023-icd-10-cm",
                    "description": "Official diagnosis coding guidelines"
                },
                {
                    "title": "CPT Guidelines",
                    "publisher": "American Medical Association",
                    "description": "Guidelines for proper use of CPT codes"
                },
                {
                    "title": "HCPCS Level II Codes",
                    "url": "https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets",
                    "description": "CMS-maintained codes for supplies, equipment, and services not in CPT"
                }
            ],
            "timely_filing_rules": {
                "medicare": {
                    "primary_claims": "1 calendar year from date of service",
                    "secondary_claims": "1 calendar year from primary EOB date",
                    "reference": "Medicare Claims Processing Manual, Chapter 1, Section 70"
                }
            }
        }
    
    def get_resolution_strategy(self, denial_type: str) -> Optional[Dict[str, Any]]:
        """
        Get resolution strategy for a specific denial type.
        
        Args:
            denial_type: The type of denial (e.g., "missing_information", "medical_necessity")
            
        Returns:
            Dictionary containing the resolution strategy, or None if not found
        """
        return self.resolution_strategies.get(denial_type)
    
    def get_strategies_by_carc(self, carc_code: str) -> List[Dict[str, Any]]:
        """
        Get resolution strategies associated with a specific CARC code.
        
        Args:
            carc_code: The CARC code to look up
            
        Returns:
            List of resolution strategy dictionaries
        """
        matching_strategies = []
        
        for denial_type, strategy in self.resolution_strategies.items():
            if carc_code in strategy.get("related_carcs", []):
                matching_strategies.append({
                    "denial_type": denial_type,
                    "strategy": strategy
                })
        
        return matching_strategies
    
    def get_billing_rule_reference(self, reference_type: str) -> Optional[Any]:
        """
        Get billing rule references of a specific type.
        
        Args:
            reference_type: The type of reference (e.g., "medicare_manuals", "coverage_policies")
            
        Returns:
            Reference information, or None if not found
        """
        return self.billing_rule_references.get(reference_type)
    
    def save_to_json(self, file_path: str) -> None:
        """
        Save the knowledge base to a JSON file.
        
        Args:
            file_path: Path to the output JSON file
        """
        knowledge_base_data = {
            "resolution_strategies": self.resolution_strategies,
            "billing_rule_references": self.billing_rule_references,
            "metadata": {
                "version": "1.0.0",
                "created_at": "2025-04-16",
                "source": "CMS guidelines and best practices"
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(knowledge_base_data, file, indent=2)
        
        print(f"Resolution knowledge base saved to {file_path}")

def create_resolution_knowledge_base():
    """
    Create and save the resolution knowledge base.
    """
    knowledge_base = ResolutionKnowledgeBase()
    output_file = "resolution_knowledge.json"
    knowledge_base.save_to_json(output_file)
    return knowledge_base

if __name__ == "__main__":
    create_resolution_knowledge_base()
