"""
Google Sheets Client Module
Handles insertion of user data extracted from WhatsApp messages
"""

import os
import gspread
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GSheetsClient:
    def __init__(self):
        """
        Initialize Google Sheets client with credentials and sheet configuration.
        """
        # Load Environment Variables
        load_dotenv()

        # Read the paths from environment variables
        creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        sheet_name = os.getenv("SHEET_NAME")

        if not creds_path or not sheet_name:
            msg = "The environment variables 'GOOGLE_SHEETS_CREDENTIALS_PATH' and 'SHEET_NAME' must be defined."
            logger.error(msg)
            raise ValueError(msg)

        self.sheet_name = sheet_name

        # Necessary scope to use Google Sheets
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Create authentication client
        if not os.path.exists(creds_path):
            msg = f"Credentials file not found at {creds_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        self.client = gspread.authorize(credentials)

        # Open the Google Sheet
        try:
            self.sheet = self.client.open(self.sheet_name)
            logger.info(f"Successfully connected to Google Sheet: {self.sheet_name}")
        except Exception as e:
            logger.error(f"Failed to open Google Sheet '{self.sheet_name}': {e}")
            raise

    def get_worksheet(self, worksheet_title: str = None):
        """
        Get a specific worksheet by name or the first one if not specified.
        
        Args:
            worksheet_title (str, optional): Name of the worksheet
            
        Returns:
            gspread.Worksheet: The requested worksheet
        """
        try:
            if worksheet_title:
                return self.sheet.worksheet(worksheet_title)
            return self.sheet.get_worksheet(0)
        except Exception as e:
            logger.error(f"Error retrieving worksheet: {e}")
            raise ValueError(f"Worksheet '{worksheet_title}' not found in the sheet '{self.sheet_name}'.")

    def insert_user_data(self, extracted_data: Dict[str, Any], worksheet_title: str = None) -> bool:
        """
        Insert user data (full_name, phone_number, id_document) into Google Sheets.
        Only inserts if at least one field is not null.
        
        Args:
            extracted_data (Dict[str, Any]): Data extracted from AI processing
                Expected format: {
                    "full_name": str or None,
                    "phone_number": str or None,
                    "id_document": str or None
                }
            worksheet_title (str, optional): Target worksheet name
            
        Returns:
            bool: True if data was inserted, False if all fields were null
        """
        
        try:
            # Extract the fields we need
            full_name = extracted_data.get("full_name")
            phone_number = extracted_data.get("phone_number")
            id_document = extracted_data.get("id_document")
            
            # Check if all fields are null/empty
            if not any([full_name, phone_number, id_document]):
                logger.info("All extracted fields are null. Skipping insertion.")
                return False
            
            # Get the worksheet
            ws = self.get_worksheet(worksheet_title)
            
            # Prepare row data with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = [
                timestamp,
                full_name or "",  # Convert None to empty string for sheets
                phone_number or "",
                id_document or ""
            ]
            
            # Insert the row
            ws.append_row(row_data)
            
            logger.info(f"Successfully inserted user data: {extracted_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting user data into Google Sheets: {e}")
            raise

    def setup_worksheet_headers(self, worksheet_title: str = None) -> None:
        """
        Set up headers in the worksheet if they don't exist.
        This is a utility function to ensure proper column structure.
        
        Args:
            worksheet_title (str, optional): Target worksheet name
        """
        try:
            ws = self.get_worksheet(worksheet_title)
            
            # Check if headers already exist
            try:
                existing_headers = ws.row_values(1)
                if existing_headers:
                    logger.info("Headers already exist in worksheet")
                    return
            except:
                pass  # No existing data, we'll add headers
            
            # Set up headers
            headers = ["Timestamp", "Full Name", "Phone Number", "ID Document"]
            ws.insert_row(headers, 1)
            
            logger.info("Headers set up successfully in worksheet")
            
        except Exception as e:
            logger.error(f"Error setting up worksheet headers: {e}")
            raise

    def validate_extracted_data(self, extracted_data: Dict[str, Any]) -> bool:
        """
        Validate that the extracted data has the expected structure.
        
        Args:
            extracted_data (Dict[str, Any]): Data to validate
            
        Returns:
            bool: True if structure is valid
        """
        required_keys = ["full_name", "phone_number", "id_document"]
        
        if not isinstance(extracted_data, dict):
            logger.error("Extracted data is not a dictionary")
            return False
        
        for key in required_keys:
            if key not in extracted_data:
                logger.error(f"Missing required key: {key}")
                return False
        
        return True


# # Test function for Google Sheets insertion
# def test_sheets_insertion():
#     """
#     Test function for Google Sheets insertion
#     """
#     try:
#         # Create client
#         client = GSheetsClient()
        
#         # Test data
#         test_data = {
#             "full_name": "Juan Carlos Test",
#             "phone_number": "573123456789",
#             "id_document": "12345678"
#         }
        
#         # Test insertion
#         result = client.insert_user_data(test_data)
#         print(f"Insertion result: {result}")
        
#         # Test with null data
#         null_data = {
#             "full_name": None,
#             "phone_number": None,
#             "id_document": None
#         }
        
#         result_null = client.insert_user_data(null_data)
#         print(f"Null data insertion result: {result_null}")
        
#     except Exception as e:
#         print(f"Test failed: {e}")


# if __name__ == "__main__":
#     test_sheets_insertion()