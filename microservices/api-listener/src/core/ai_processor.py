"""
AI Processing Module
Handles communication with Google AI Studio (Gemini) for data extraction
"""

import os
import logging
import json
from typing import Dict, Any
from google import genai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def extract_user_data_with_ai(message: str) -> Dict[str, Any]:
    """
    Extract user data (full name, phone number, ID document) from message using Gemini AI.
    
    Args:
        message (str): The message content to analyze
        
    Returns:
        Dict[str, Any]: JSON response with extracted data or null values
        
    Expected format:
    {
        "full_name": "string or null",
        "phone_number": "string or null", 
        "id_document": "string or null"
    }
    """
    
    # Default response structure in case of errors
    default_response = {
        "full_name": None,
        "phone_number": None,
        "id_document": None
    }
    
    try:
        # Initialize Gemini client
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Create dynamic prompt with message placeholder
        prompt = create_extraction_prompt(message)
        
        # Generate content using Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Parse the AI response
        ai_response_text = response.text.strip()
        logging.info(f"AI Response: {ai_response_text}")
        
        # Try to parse as JSON
        try:
            extracted_data = json.loads(ai_response_text)
            
            # Validate response structure and ensure null values for missing data
            validated_data = {
                "full_name": extracted_data.get("full_name"),
                "phone_number": extracted_data.get("phone_number"),
                "id_document": extracted_data.get("id_document")
            }
            
            logging.info(f"Successfully extracted data: {validated_data}")
            return validated_data
            
        except json.JSONDecodeError as json_error:
            logging.error(f"Failed to parse AI response as JSON: {json_error}")
            logging.error(f"Raw AI response: {ai_response_text}")
            return default_response
            
    except Exception as e:
        logging.error(f"Error communicating with AI: {str(e)}")
        return default_response


def create_extraction_prompt(message: str) -> str:
    """
    Create a dynamic prompt for data extraction with specific instructions.
    
    Args:
        message (str): The message content to include in the prompt
        
    Returns:
        str: The complete prompt for AI processing
    """
    
    prompt = f"""
    You are a data extraction specialist. Analyze the following message and extract ONLY these three pieces of information:

    1. FULL NAME: Complete name of a person (first name + last name at minimum)
    2. PHONE NUMBER: Any telephone number (with or without country code)
    3. ID DOCUMENT: Any identification document number (cédula, DNI, passport, etc.)

    STRICT RULES:
    - You MUST respond ONLY with a valid JSON object
    - If you cannot find any of the requested information, set that field to null
    - Do not include any explanations, comments, or text outside the JSON
    - Use exactly these field names: "full_name", "phone_number", "id_document"
    - Values should be strings or null (not empty strings)

    MESSAGE TO ANALYZE:
    "{message}"

    RESPOND WITH JSON ONLY:
    """
    
    return prompt
