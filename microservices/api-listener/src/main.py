"""
Main Flask Application
Integrates WhatsApp message processing with AI data extraction and Google Sheets storage
"""

import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import our custom modules
from core.message_manager import process_message
from core.ai_processor import extract_user_data_with_ai
from core.gsheets_client import GSheetsClient

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'


@app.route('/webhook', defaults={'subpath': ''}, methods=['POST'])
@app.route('/webhook/<path:subpath>', methods=['POST'])
def webhook_handler(subpath):
    """
    Main webhook endpoint that processes WhatsApp messages, extracts user data,
    and saves it to Google Sheets if valid data is found.
    
    Returns:
        JSON response with extracted user data or error information
    """
    
    try:
        print(f"Received webhook for subpath: {subpath}")
        # Get the payload from the request
        payload = request.get_json()
        
        if not payload:
            return jsonify({
                "error": "No JSON payload received",
                "full_name": None,
                "phone_number": None,
                "id_document": None,
                "saved_to_sheets": False
            }), 400
        
        # Process the WhatsApp message
        message_content = process_message(payload)
        
        if message_content is None:
            return jsonify({
                "error": "Message does not meet processing criteria",
                "full_name": None,
                "phone_number": None,
                "id_document": None,
                "saved_to_sheets": False
            }), 200
        
        # Extract user data using AI
        extracted_data = extract_user_data_with_ai(message_content)
        
        # Initialize Google Sheets client and try to save data
        saved_to_sheets = False
        sheets_error = None
        
        try:
            sheets_client = GSheetsClient()
            saved_to_sheets = sheets_client.insert_user_data(extracted_data)
            
            if saved_to_sheets:
                print(f"✅ Data successfully saved to Google Sheets: {extracted_data}")
            else:
                print("⚠️ All fields were null, data not saved to sheets")
                
        except Exception as sheets_e:
            sheets_error = str(sheets_e)
            print(f"❌ Error saving to Google Sheets: {sheets_error}")
        
        # Prepare response
        response = {
            "success": True,
            "message_content": message_content,
            "saved_to_sheets": saved_to_sheets,
            **extracted_data
        }
        
        # Add sheets error to response if it occurred
        if sheets_error:
            response["sheets_error"] = sheets_error
        
        return jsonify(response), 200
        
    except Exception as e:
        # Return error response with null values
        error_response = {
            "success": False,
            "error": str(e),
            "full_name": None,
            "phone_number": None,
            "id_document": None,
            "saved_to_sheets": False
        }
        
        print(f"Error in webhook handler: {str(e)}")
        return jsonify(error_response), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )