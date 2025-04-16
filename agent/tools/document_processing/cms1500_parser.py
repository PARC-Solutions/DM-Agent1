"""
CMS-1500 Form Parser Tool

This module provides tools for extracting information from CMS-1500 forms using
OCR and computer vision techniques. The parser extracts key fields including patient
information, provider details, diagnosis codes, procedure codes, and billing amounts.
"""

import base64
import io
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import cv2
import numpy as np
import pytesseract
from google.cloud import vision
from google.adk.tools import tool
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Define CMS-1500 form field coordinates
# These are normalized coordinates (0-1) for field positions on the form
class CMS1500Fields(Enum):
    """Enum defining the field locations on a CMS-1500 form."""
    PATIENT_NAME = ((0.35, 0.14), (0.65, 0.17))
    PATIENT_DOB = ((0.35, 0.17), (0.45, 0.19))
    PATIENT_SEX = ((0.45, 0.17), (0.55, 0.19))
    INSURED_NAME = ((0.35, 0.19), (0.65, 0.22))
    PATIENT_ADDRESS = ((0.35, 0.22), (0.65, 0.25))
    PATIENT_CITY = ((0.35, 0.25), (0.50, 0.27))
    PATIENT_STATE = ((0.50, 0.25), (0.55, 0.27))
    PATIENT_ZIP = ((0.55, 0.25), (0.65, 0.27))
    PATIENT_PHONE = ((0.35, 0.27), (0.50, 0.29))
    INSURANCE_PLAN = ((0.35, 0.29), (0.65, 0.32))
    INSURED_ID = ((0.65, 0.14), (0.85, 0.17))
    INSURED_GROUP = ((0.65, 0.19), (0.85, 0.22))
    
    # Diagnosis codes (up to 12 in newer forms)
    DIAGNOSIS_1 = ((0.25, 0.40), (0.35, 0.42))
    DIAGNOSIS_2 = ((0.35, 0.40), (0.45, 0.42))
    DIAGNOSIS_3 = ((0.45, 0.40), (0.55, 0.42))
    DIAGNOSIS_4 = ((0.55, 0.40), (0.65, 0.42))
    DIAGNOSIS_5 = ((0.65, 0.40), (0.75, 0.42))
    DIAGNOSIS_6 = ((0.75, 0.40), (0.85, 0.42))
    DIAGNOSIS_7 = ((0.25, 0.42), (0.35, 0.44))
    DIAGNOSIS_8 = ((0.35, 0.42), (0.45, 0.44))
    DIAGNOSIS_9 = ((0.45, 0.42), (0.55, 0.44))
    DIAGNOSIS_10 = ((0.55, 0.42), (0.65, 0.44))
    DIAGNOSIS_11 = ((0.65, 0.42), (0.75, 0.44))
    DIAGNOSIS_12 = ((0.75, 0.42), (0.85, 0.44))
    
    # Service lines (up to 6 lines)
    SERVICE_DATE_1 = ((0.15, 0.47), (0.25, 0.49))
    SERVICE_PLACE_1 = ((0.25, 0.47), (0.30, 0.49))
    CPT_CODE_1 = ((0.30, 0.47), (0.40, 0.49))
    MODIFIER_1 = ((0.40, 0.47), (0.50, 0.49))
    DIAGNOSIS_POINTER_1 = ((0.50, 0.47), (0.55, 0.49))
    CHARGES_1 = ((0.55, 0.47), (0.65, 0.49))
    DAYS_UNITS_1 = ((0.65, 0.47), (0.70, 0.49))
    
    SERVICE_DATE_2 = ((0.15, 0.49), (0.25, 0.51))
    SERVICE_PLACE_2 = ((0.25, 0.49), (0.30, 0.51))
    CPT_CODE_2 = ((0.30, 0.49), (0.40, 0.51))
    MODIFIER_2 = ((0.40, 0.49), (0.50, 0.51))
    DIAGNOSIS_POINTER_2 = ((0.50, 0.49), (0.55, 0.51))
    CHARGES_2 = ((0.55, 0.49), (0.65, 0.51))
    DAYS_UNITS_2 = ((0.65, 0.49), (0.70, 0.51))
    
    SERVICE_DATE_3 = ((0.15, 0.51), (0.25, 0.53))
    SERVICE_PLACE_3 = ((0.25, 0.51), (0.30, 0.53))
    CPT_CODE_3 = ((0.30, 0.51), (0.40, 0.53))
    MODIFIER_3 = ((0.40, 0.51), (0.50, 0.53))
    DIAGNOSIS_POINTER_3 = ((0.50, 0.51), (0.55, 0.53))
    CHARGES_3 = ((0.55, 0.51), (0.65, 0.53))
    DAYS_UNITS_3 = ((0.65, 0.51), (0.70, 0.53))
    
    SERVICE_DATE_4 = ((0.15, 0.53), (0.25, 0.55))
    SERVICE_PLACE_4 = ((0.25, 0.53), (0.30, 0.55))
    CPT_CODE_4 = ((0.30, 0.53), (0.40, 0.55))
    MODIFIER_4 = ((0.40, 0.53), (0.50, 0.55))
    DIAGNOSIS_POINTER_4 = ((0.50, 0.53), (0.55, 0.55))
    CHARGES_4 = ((0.55, 0.53), (0.65, 0.55))
    DAYS_UNITS_4 = ((0.65, 0.53), (0.70, 0.55))
    
    SERVICE_DATE_5 = ((0.15, 0.55), (0.25, 0.57))
    SERVICE_PLACE_5 = ((0.25, 0.55), (0.30, 0.57))
    CPT_CODE_5 = ((0.30, 0.55), (0.40, 0.57))
    MODIFIER_5 = ((0.40, 0.55), (0.50, 0.57))
    DIAGNOSIS_POINTER_5 = ((0.50, 0.55), (0.55, 0.57))
    CHARGES_5 = ((0.55, 0.55), (0.65, 0.57))
    DAYS_UNITS_5 = ((0.65, 0.55), (0.70, 0.57))
    
    SERVICE_DATE_6 = ((0.15, 0.57), (0.25, 0.59))
    SERVICE_PLACE_6 = ((0.25, 0.57), (0.30, 0.59))
    CPT_CODE_6 = ((0.30, 0.57), (0.40, 0.59))
    MODIFIER_6 = ((0.40, 0.57), (0.50, 0.59))
    DIAGNOSIS_POINTER_6 = ((0.50, 0.57), (0.55, 0.59))
    CHARGES_6 = ((0.55, 0.57), (0.65, 0.59))
    DAYS_UNITS_6 = ((0.65, 0.57), (0.70, 0.59))
    
    # Provider information
    PROVIDER_NAME = ((0.70, 0.58), (0.90, 0.60))
    PROVIDER_NPI = ((0.70, 0.63), (0.80, 0.65))
    
    # Totals
    TOTAL_CHARGE = ((0.55, 0.59), (0.65, 0.61))


class FieldExtractionResult(BaseModel):
    """Model representing the result of field extraction."""
    text: str = Field(default="")
    confidence: float = Field(default=0.0)


class ServiceLine(BaseModel):
    """Model representing a service line on the CMS-1500 form."""
    service_date: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    place_of_service: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    cpt_code: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    modifier: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    diagnosis_pointer: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    charges: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    days_units: FieldExtractionResult = Field(default_factory=FieldExtractionResult)


class CMS1500ParseResult(BaseModel):
    """Model representing the full parsing result of a CMS-1500 form."""
    # Patient information
    patient_name: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    patient_dob: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    patient_sex: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    patient_address: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    patient_city: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    patient_state: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    patient_zip: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    patient_phone: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    
    # Insurance information
    insured_name: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    insured_id: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    insured_group: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    insurance_plan: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    
    # Diagnoses codes (ICD-10)
    diagnoses: Dict[str, FieldExtractionResult] = Field(default_factory=dict)
    
    # Service lines
    service_lines: List[ServiceLine] = Field(default_factory=list)
    
    # Provider information
    provider_name: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    provider_npi: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    
    # Totals
    total_charge: FieldExtractionResult = Field(default_factory=FieldExtractionResult)
    
    # Overall extraction metrics
    overall_confidence: float = Field(default=0.0)
    warnings: List[str] = Field(default_factory=list)
    extraction_method: str = Field(default="")


class CMS1500Parser:
    """Parser for CMS-1500 forms using OCR technology."""
    
    def __init__(self, use_cloud_vision: bool = True):
        """
        Initialize the CMS-1500 parser.
        
        Args:
            use_cloud_vision: Whether to use Google Cloud Vision API for OCR (recommended).
                             If False, falls back to pytesseract.
        """
        self.use_cloud_vision = use_cloud_vision
        self.client = None
        if use_cloud_vision:
            try:
                self.client = vision.ImageAnnotatorClient()
            except Exception as e:
                logger.warning(f"Failed to initialize Google Cloud Vision client: {e}")
                logger.warning("Falling back to pytesseract OCR")
                self.use_cloud_vision = False
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess an image to improve OCR results.
        
        Args:
            image: The input image as a numpy array
            
        Returns:
            The preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply thresholding to separate text from background
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Invert the image (text should be black, background white for OCR)
        thresh = cv2.bitwise_not(thresh)
        
        return thresh
    
    def _extract_field_cloud_vision(
        self, image: np.ndarray, field: CMS1500Fields
    ) -> FieldExtractionResult:
        """
        Extract text from a specific field using Google Cloud Vision.
        
        Args:
            image: The form image as a numpy array
            field: The field enum defining the area to extract
            
        Returns:
            FieldExtractionResult containing the extracted text and confidence
        """
        if self.client is None:
            return FieldExtractionResult(text="", confidence=0.0)
            
        h, w = image.shape[:2]
        
        # Get field coordinates
        (x1_pct, y1_pct), (x2_pct, y2_pct) = field.value
        x1, y1 = int(x1_pct * w), int(y1_pct * h)
        x2, y2 = int(x2_pct * w), int(y2_pct * h)
        
        # Extract the field region
        field_img = image[y1:y2, x1:x2]
        
        # Convert to bytes
        success, encoded_image = cv2.imencode('.png', field_img)
        if not success:
            return FieldExtractionResult(text="", confidence=0.0)
            
        content = encoded_image.tobytes()
        
        # Send to Google Cloud Vision
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        
        if response.error.message:
            logger.warning(f"Error from Google Cloud Vision: {response.error.message}")
            return FieldExtractionResult(text="", confidence=0.0)
            
        if not response.text_annotations:
            return FieldExtractionResult(text="", confidence=0.0)
            
        # Extract the text
        text = response.text_annotations[0].description.strip()
        
        # Calculate confidence
        confidence = 0.0
        if response.full_text_annotation and response.full_text_annotation.pages:
            page = response.full_text_annotation.pages[0]
            confidences = []
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_confidence = 1.0
                        for symbol in word.symbols:
                            word_confidence *= symbol.confidence
                        confidences.append(word_confidence)
            
            if confidences:
                confidence = sum(confidences) / len(confidences)
        
        return FieldExtractionResult(text=text, confidence=confidence)
    
    def _extract_field_pytesseract(
        self, image: np.ndarray, field: CMS1500Fields
    ) -> FieldExtractionResult:
        """
        Extract text from a specific field using pytesseract.
        
        Args:
            image: The form image as a numpy array
            field: The field enum defining the area to extract
            
        Returns:
            FieldExtractionResult containing the extracted text and confidence
        """
        h, w = image.shape[:2]
        
        # Get field coordinates
        (x1_pct, y1_pct), (x2_pct, y2_pct) = field.value
        x1, y1 = int(x1_pct * w), int(y1_pct * h)
        x2, y2 = int(x2_pct * w), int(y2_pct * h)
        
        # Extract the field region
        field_img = image[y1:y2, x1:x2]
        
        # Preprocess for better OCR
        preprocessed = self._preprocess_image(field_img)
        
        # Extract text using pytesseract
        config = r'--oem 3 --psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,-_/()# "' 
        data = pytesseract.image_to_data(preprocessed, config=config, output_type=pytesseract.Output.DICT)
        
        # Extract text and calculate confidence
        text_parts = []
        confidences = []
        
        for i in range(len(data['text'])):
            if data['text'][i].strip():
                text_parts.append(data['text'][i])
                confidences.append(data['conf'][i] / 100.0)
        
        text = ' '.join(text_parts).strip()
        confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return FieldExtractionResult(text=text, confidence=confidence)
    
    def _extract_field(
        self, image: np.ndarray, field: CMS1500Fields
    ) -> FieldExtractionResult:
        """
        Extract text from a specific field using the configured OCR method.
        
        Args:
            image: The form image as a numpy array
            field: The field enum defining the area to extract
            
        Returns:
            FieldExtractionResult containing the extracted text and confidence
        """
        if self.use_cloud_vision:
            return self._extract_field_cloud_vision(image, field)
        else:
            return self._extract_field_pytesseract(image, field)
    
    def _process_image(self, image: np.ndarray) -> CMS1500ParseResult:
        """
        Process a CMS-1500 form image and extract all fields.
        
        Args:
            image: The form image as a numpy array
            
        Returns:
            CMS1500ParseResult containing all extracted fields
        """
        result = CMS1500ParseResult()
        result.extraction_method = "Google Cloud Vision" if self.use_cloud_vision else "Pytesseract"
        
        # Extract patient information
        result.patient_name = self._extract_field(image, CMS1500Fields.PATIENT_NAME)
        result.patient_dob = self._extract_field(image, CMS1500Fields.PATIENT_DOB)
        result.patient_sex = self._extract_field(image, CMS1500Fields.PATIENT_SEX)
        result.patient_address = self._extract_field(image, CMS1500Fields.PATIENT_ADDRESS)
        result.patient_city = self._extract_field(image, CMS1500Fields.PATIENT_CITY)
        result.patient_state = self._extract_field(image, CMS1500Fields.PATIENT_STATE)
        result.patient_zip = self._extract_field(image, CMS1500Fields.PATIENT_ZIP)
        result.patient_phone = self._extract_field(image, CMS1500Fields.PATIENT_PHONE)
        
        # Extract insurance information
        result.insured_name = self._extract_field(image, CMS1500Fields.INSURED_NAME)
        result.insured_id = self._extract_field(image, CMS1500Fields.INSURED_ID)
        result.insured_group = self._extract_field(image, CMS1500Fields.INSURED_GROUP)
        result.insurance_plan = self._extract_field(image, CMS1500Fields.INSURANCE_PLAN)
        
        # Extract diagnosis codes
        diagnoses_fields = [
            ("1", CMS1500Fields.DIAGNOSIS_1),
            ("2", CMS1500Fields.DIAGNOSIS_2),
            ("3", CMS1500Fields.DIAGNOSIS_3),
            ("4", CMS1500Fields.DIAGNOSIS_4),
            ("5", CMS1500Fields.DIAGNOSIS_5),
            ("6", CMS1500Fields.DIAGNOSIS_6),
            ("7", CMS1500Fields.DIAGNOSIS_7),
            ("8", CMS1500Fields.DIAGNOSIS_8),
            ("9", CMS1500Fields.DIAGNOSIS_9),
            ("10", CMS1500Fields.DIAGNOSIS_10),
            ("11", CMS1500Fields.DIAGNOSIS_11),
            ("12", CMS1500Fields.DIAGNOSIS_12),
        ]
        
        for code_num, field in diagnoses_fields:
            extraction = self._extract_field(image, field)
            if extraction.text:
                result.diagnoses[code_num] = extraction
        
        # Extract service lines
        service_line_fields = [
            (
                1,
                CMS1500Fields.SERVICE_DATE_1,
                CMS1500Fields.SERVICE_PLACE_1,
                CMS1500Fields.CPT_CODE_1,
                CMS1500Fields.MODIFIER_1,
                CMS1500Fields.DIAGNOSIS_POINTER_1,
                CMS1500Fields.CHARGES_1,
                CMS1500Fields.DAYS_UNITS_1,
            ),
            (
                2,
                CMS1500Fields.SERVICE_DATE_2,
                CMS1500Fields.SERVICE_PLACE_2,
                CMS1500Fields.CPT_CODE_2,
                CMS1500Fields.MODIFIER_2,
                CMS1500Fields.DIAGNOSIS_POINTER_2,
                CMS1500Fields.CHARGES_2,
                CMS1500Fields.DAYS_UNITS_2,
            ),
            (
                3,
                CMS1500Fields.SERVICE_DATE_3,
                CMS1500Fields.SERVICE_PLACE_3,
                CMS1500Fields.CPT_CODE_3,
                CMS1500Fields.MODIFIER_3,
                CMS1500Fields.DIAGNOSIS_POINTER_3,
                CMS1500Fields.CHARGES_3,
                CMS1500Fields.DAYS_UNITS_3,
            ),
            (
                4,
                CMS1500Fields.SERVICE_DATE_4,
                CMS1500Fields.SERVICE_PLACE_4,
                CMS1500Fields.CPT_CODE_4,
                CMS1500Fields.MODIFIER_4,
                CMS1500Fields.DIAGNOSIS_POINTER_4,
                CMS1500Fields.CHARGES_4,
                CMS1500Fields.DAYS_UNITS_4,
            ),
            (
                5,
                CMS1500Fields.SERVICE_DATE_5,
                CMS1500Fields.SERVICE_PLACE_5,
                CMS1500Fields.CPT_CODE_5,
                CMS1500Fields.MODIFIER_5,
                CMS1500Fields.DIAGNOSIS_POINTER_5,
                CMS1500Fields.CHARGES_5,
                CMS1500Fields.DAYS_UNITS_5,
            ),
            (
                6,
                CMS1500Fields.SERVICE_DATE_6,
                CMS1500Fields.SERVICE_PLACE_6,
                CMS1500Fields.CPT_CODE_6,
                CMS1500Fields.MODIFIER_6,
                CMS1500Fields.DIAGNOSIS_POINTER_6,
                CMS1500Fields.CHARGES_6,
                CMS1500Fields.DAYS_UNITS_6,
            ),
        ]
        
        for (
            line_num,
            date_field,
            place_field,
            cpt_field,
            modifier_field,
            pointer_field,
            charges_field,
            days_field,
        ) in service_line_fields:
            date_result = self._extract_field(image, date_field)
            cpt_result = self._extract_field(image, cpt_field)
            
            # Only add service line if key fields are present
            if date_result.text or cpt_result.text:
                service_line = ServiceLine(
                    service_date=date_result,
                    place_of_service=self._extract_field(image, place_field),
                    cpt_code=cpt_result,
                    modifier=self._extract_field(image, modifier_field),
                    diagnosis_pointer=self._extract_field(image, pointer_field),
                    charges=self._extract_field(image, charges_field),
                    days_units=self._extract_field(image, days_field),
                )
                result.service_lines.append(service_line)
        
        # Extract provider information
        result.provider_name = self._extract_field(image, CMS1500Fields.PROVIDER_NAME)
        result.provider_npi = self._extract_field(image, CMS1500Fields.PROVIDER_NPI)
        
        # Extract totals
        result.total_charge = self._extract_field(image, CMS1500Fields.TOTAL_CHARGE)
        
        # Calculate overall confidence
        confidence_values = []
        
        # Add patient info confidences
        confidence_values.extend([
            result.patient_name.confidence,
            result.patient_dob.confidence,
            result.patient_address.confidence,
        ])
        
        # Add diagnosis code confidences
        confidence_values.extend([d.confidence for d in result.diagnoses.values()])
        
        # Add service line confidences
        for line in result.service_lines:
            confidence_values.extend([
                line.service_date.confidence,
                line.cpt_code.confidence,
                line.charges.confidence,
            ])
        
        # Add provider info confidences
        confidence_values.extend([
            result.provider_name.confidence,
            result.provider_npi.confidence,
        ])
        
        # Calculate overall confidence
        if confidence_values:
            result.overall_confidence = sum(confidence_values) / len(confidence_values)
        
        # Add warnings for low confidence fields
        low_confidence_threshold = 0.7
        if result.patient_name.confidence < low_confidence_threshold:
            result.warnings.append("Low confidence in patient name extraction")
        
        if result.service_lines and all(line.cpt_code.confidence < low_confidence_threshold for line in result.service_lines):
            result.warnings.append("Low confidence in CPT code extraction")
            
        return result
    
    def parse_pdf(self, pdf_data: Union[bytes, str, Path]) -> CMS1500ParseResult:
        """
        Parse a CMS-1500 form from a PDF file.
        
        Args:
            pdf_data: The PDF data as bytes, Base64-encoded string, or file path
            
        Returns:
            CMS1500ParseResult containing the extracted information
        """
        try:
            # Handle different input types
            if isinstance(pdf_data, str):
                if os.path.exists(pdf_data):
                    # It's a file path
                    images = convert_from_path(pdf_data)
                else:
                    # It might be Base64-encoded
                    try:
                        pdf_bytes = base64.b64decode(pdf_data)
                        images = convert_from_bytes(pdf_bytes)
                    except Exception as e:
                        logger.error(f"Failed to decode Base64 string: {e}")
                        raise ValueError("Invalid PDF data: not a valid file path or Base64 string")
            elif isinstance(pdf_data, bytes):
                # It's binary data
                images = convert_from_bytes(pdf_data)
            elif isinstance(pdf_data, Path):
                # It's a Path object
                images = convert_from_path(str(pdf_data))
            else:
                raise ValueError("Unsupported input type")
                
            # Process the first page
            if not images:
                raise ValueError("No pages found in the PDF")
                
            # Convert the PIL image to a numpy array for OpenCV
            first_page = images[0]
            image_np = np.array(first_page)
            
            # Process the image
            return self._process_image(image_np)
            
        except Exception as e:
            logger.error(f"Error parsing CMS-1500 form: {e}")
            result = CMS1500ParseResult()
            result.warnings.append(f"Error processing PDF: {str(e)}")
            return result


@tool
def analyze_cms1500_form(form_data: Union[bytes, str]) -> Dict:
    """
    Extracts relevant information from CMS-1500 forms.
    
    Args:
        form_data: Binary data or Base64-encoded string of the CMS-1500 form
        
    Returns:
        dict: Structured data from the form including patient information, 
              diagnosis codes, procedure codes, charges, and provider details
    """
    logger.info("CMS-1500 parser tool called")
    
    try:
        # Determine if the input is a file path or binary/base64 data
        if isinstance(form_data, str) and os.path.exists(form_data):
            # It's a file path
            parser = CMS1500Parser()
            result = parser.parse_pdf(form_data)
        else:
            # It's binary or base64 data
            parser = CMS1500Parser()
            result = parser.parse_pdf(form_data)
        
        # Convert to dictionary
        result_dict = result.dict()
        
        # Add a status
        result_dict["status"] = "success" if result.overall_confidence > 0.6 else "partial_success"
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Error in CMS-1500 parser: {e}")
        return {
            "status": "error",
            "message": f"Error processing CMS-1500 form: {str(e)}",
            "warnings": [str(e)]
        }
