"""
Main Flask Application
Integrates WhatsApp message processing with AI data extraction
"""

import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import our custom modules
from core.message_manager import process_message
from core.ai_processor import extract_user_data_with_ai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'


@app.route('/webhook', defaults={'subpath': ''}, methods=['POST'])
@app.route('/webhook/<path:subpath>', methods=['POST'])
def webhook_handler(subpath):
    """
    Main webhook endpoint that processes WhatsApp messages and extracts user data.
    
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
                "id_document": None
            }), 400
        
        # Process the WhatsApp message
        message_content = process_message(payload)
        
        if message_content is None:
            return jsonify({
                "error": "Message does not meet processing criteria",
                "full_name": None,
                "phone_number": None,
                "id_document": None
            }), 200
        
        # Extract user data using AI
        extracted_data = extract_user_data_with_ai(message_content)
        
        # Add success status to response
        response = {
            "success": True,
            "message_content": message_content,
            **extracted_data
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        # Return error response with null values
        error_response = {
            "success": False,
            "error": str(e),
            "full_name": None,
            "phone_number": None,
            "id_document": None
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